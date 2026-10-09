# API compatibility and configuration

The included CLI targets the common OpenAI-compatible image API shape:

- Generate: `POST {GPT_IMAGE_BASE_URL}/images/generations`
- Edit: `POST {GPT_IMAGE_BASE_URL}/images/edits` as `multipart/form-data`
- Authentication: `Authorization: Bearer <key>`
- Results: `data[]` entries containing `b64_json` or `url`

`GPT_IMAGE_BASE_URL` is the API root, commonly ending in `/v1`; do not include `/images/generations` in the value. Trailing slashes are removed. The CLI sends `GPT_IMAGE_API_KEY` as `Authorization: Bearer <key>`; it takes precedence over `OPENAI_API_KEY`. `GPT_IMAGE_MODEL` sets the default model and may be overridden with `--model`. The CLI also accepts `--base-url` and `--api-key` overrides.

Example configuration in a shell session (keep real keys out of checked-in files):

```sh
export GPT_IMAGE_BASE_URL="https://api.example.com/v1"
export GPT_IMAGE_API_KEY="..."
export GPT_IMAGE_MODEL="provider-image-model"
```

PowerShell:

```powershell
$env:GPT_IMAGE_BASE_URL = "https://api.example.com/v1"
$env:GPT_IMAGE_API_KEY = "..."
$env:GPT_IMAGE_MODEL = "provider-image-model"
```

Compatibility varies by provider and model. Optional fields such as `quality`, `size`, `n`, `output_format`, and edit `mask` are not universally supported. Consult the provider's API documentation and omit unsupported options. The script does not silently change endpoints, models, or parameters. URL results are fetched without forwarding the API key to the result host.

The API protocol does not define transparent-output support consistently. Request transparency only when the selected provider/model documents support for it, and inspect the resulting alpha channel. A prompt asking for a transparent background alone does not guarantee transparency.

## CLI examples

```sh
python gpt-image/scripts/image_gen.py generate --prompt "A clean product photo of a blue glass bottle" --size 1024x1024 --quality high --out output/imagegen/bottle.png
python gpt-image/scripts/image_gen.py edit --image photo.png --mask mask.png --prompt "Change only the marked background" --out output/imagegen/edited.png
python gpt-image/scripts/image_gen.py generate --prompt "A simple test" --out output/imagegen/test.png --dry-run
```

The dry run prints the endpoint and request fields but never prints the key. It does not require a key or make a network request.
