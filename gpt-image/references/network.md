# Network access and sandbox notes

The bundled CLI sends requests to the `base_url` configured in `~/.agent-skills/config.json` and downloads image results when the provider returns URLs. It needs outbound HTTPS access to the configured API host and, for URL-based results, the result host.

Some agent environments run commands in a sandbox that blocks network access or asks for approval. Follow the host agent's network and command-approval controls. Approval settings and network access are separate in some environments; approving a command does not necessarily enable network access.

## Codex-specific note

In Codex, network access depends on the selected sandbox mode and configuration. For example, the `workspace-write` sandbox can be configured in `~/.codex/config.toml`:

```toml
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
```

Other agents use their own network controls; this skill and its image CLI do not depend on Codex-specific networking.

Only enable outbound network access for trusted workspaces and configured API hosts.
