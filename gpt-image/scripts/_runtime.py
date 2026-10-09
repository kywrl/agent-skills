"""Provision the skill's Python dependencies in a private, reusable venv."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import time
import venv
from typing import Iterator


SKILL_DIR = Path(__file__).resolve().parent.parent
REQUIREMENTS = SKILL_DIR / "requirements.txt"
READY_MARKER = ".gpt-image-ready"


def _cache_root() -> Path:
    if sys.platform == "win32":
        base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        if base:
            return Path(base) / "gpt-image-skill" / "environments"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "gpt-image-skill" / "environments"
    else:
        base = os.getenv("XDG_CACHE_HOME")
        return Path(base) / "gpt-image-skill" / "environments" if base else (
            Path.home() / ".cache" / "gpt-image-skill" / "environments"
        )
    return Path.home() / ".cache" / "gpt-image-skill" / "environments"


def _environment_path() -> Path:
    requirements = REQUIREMENTS.read_bytes()
    identity = "\0".join(
        (
            requirements.decode("utf-8"),
            str(Path(sys.base_prefix).resolve()),
            sys.implementation.name,
            f"{sys.version_info.major}.{sys.version_info.minor}",
        )
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    version = f"py{sys.version_info.major}{sys.version_info.minor}"
    return _cache_root() / f"{version}-{digest}"


@contextmanager
def _environment_lock(path: Path) -> Iterator[None]:
    """Serialize first-run setup when CLI and Desktop start the skill together."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt

            lock_file.seek(0, os.SEEK_END)
            if lock_file.tell() == 0:
                lock_file.write(b"0")
                lock_file.flush()
            while True:
                lock_file.seek(0)
                try:
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(0.2)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _python_in(environment: Path) -> Path:
    return environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _provision(environment: Path) -> None:
    marker = environment / READY_MARKER
    if marker.is_file() and _python_in(environment).is_file():
        return

    if environment.exists():
        import shutil

        shutil.rmtree(environment)

    print(
        "Setting up the gpt-image skill's private Python environment "
        "(first use only)...",
        file=sys.stderr,
    )
    try:
        venv.EnvBuilder(with_pip=True).create(environment)
        subprocess.run(
            [
                str(_python_in(environment)),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "-r",
                str(REQUIREMENTS),
            ],
            check=True,
        )
        marker.write_text("ready\n", encoding="utf-8")
    except Exception:
        import shutil

        shutil.rmtree(environment, ignore_errors=True)
        raise


def ensure_skill_environment(script: Path, arguments: list[str]) -> None:
    """Restart a live CLI command inside the skill-only dependency environment."""
    environment = _environment_path()
    try:
        if Path(sys.prefix).resolve() == environment.resolve():
            return
    except OSError:
        pass

    try:
        with _environment_lock(environment.with_suffix(".lock")):
            _provision(environment)
    except Exception as exc:
        print(
            "Error: Could not prepare the gpt-image skill's isolated Python "
            "environment. Check that Python can create virtual environments and "
            f"that package downloads are available. Details: {exc}\n"
            "No global or project Python packages were changed.",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    python = _python_in(environment)
    command = [str(python), str(script.resolve()), *arguments]
    if os.name == "nt":
        # Windows emulates execv by spawning a child process. Wait for it so
        # callers keep the CLI's output and exit status until it completes.
        completed = subprocess.run(command)
        raise SystemExit(completed.returncode)
    os.execv(str(python), command)
