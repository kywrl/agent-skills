---
name: "gpt-image"
description: "Generate or edit raster images through the bundled Python CLI when an agent needs photos, illustrations, sprites, mockups, or transparent-background cutouts. Use for new bitmap assets or edits; avoid when the work belongs in an existing SVG/vector/code-native asset or deterministic HTML/CSS/canvas output."
---

# Image Generation Skill

Generates or edits images for the current project (for example website assets, game assets, UI mockups, product mockups, wireframes, logo design, photorealistic images, or infographics).

## Execution mode and rules

This skill always uses its bundled Python CLI for image generation and editing, whether selected explicitly or automatically. It is self-contained and does not require an agent-provided image-generation tool.

Resolve `scripts/image_gen.py` relative to this skill directory. The CLI exposes three subcommands:

- `generate`
- `edit`
- `generate-batch`

Rules:
- Use `generate` for one prompt, `edit` when an existing image must change, and `generate-batch` for multiple distinct assets/prompts. Use `--n` only for variants of one prompt.
- Preserve the upstream intent classification, image-type taxonomy, prompt guidance, constraints, and output review workflow.
- For transparent output, follow the selected provider/model's documented support. Never silently switch from `gpt-image-2` to `gpt-image-1.5`; ask first unless the user explicitly requested `gpt-image-1.5`.
- Do not silently switch endpoints, models, or omit user-required parameters after an API error. Explain the provider limitation and ask when a change is required.
- Live CLI requests require network access and an API key in `gpt_image.api_key` in `~/.agent-skills/config.json`. The CLI creates this user-level configuration file on first invocation if it does not exist. On first live use, the bundled launcher creates a private virtual environment in the user's cache and installs the skill's Python dependencies there. This does not modify the system Python, a project environment, or Codex's own runtime.
- Do not create one-off SDK runners. Preserve upstream CLI behavior and the local provider configuration when updating the script.
- Save final project assets under `output/gptimage/` by default, or at the user's requested path. Do not overwrite existing files unless requested; otherwise use a versioned sibling filename.

Shared prompt guidance lives in `references/prompting.md` and `references/sample-prompts.md`.

CLI resources:
- `references/cli.md`
- `references/image-api.md`
- `references/network.md`
- `scripts/image_gen.py`

CLI API configuration is read from the `gpt_image` section in `~/.agent-skills/config.json`:

- `gpt_image.api_key`: API key.
- `gpt_image.base_url`: API root, default `https://api.openai.com/v1`. Do not include `/images/generations` or `/images/edits`.
- `gpt_image.model`: default model, `gpt-image-2` when unset. It may name a provider-specific model when using a compatible custom endpoint.
- CLI flags `--base-url`, `--api-key`, and `--model` override the corresponding config values.
- These settings configure the bundled script and are independent of the agent's own image tools or settings.
- For configuration examples and endpoint details, read [references/api-compatibility.md](references/api-compatibility.md).

## When to use
- Generate a new image (concept art, product shot, cover, website hero)
- Generate a new image using one or more reference images for style, composition, or mood
- Edit an existing image (inpainting, lighting or weather transformations, background replacement, object removal, compositing, transparent background)
- Produce many assets or variants for one task

## When not to use
- Extending or matching an existing SVG/vector icon set, logo system, or illustration library inside the repo
- Creating simple shapes, diagrams, wireframes, or icons that are better produced directly in SVG, HTML/CSS, or canvas
- Making a small project-local asset edit when the source file already exists in an editable native format
- Any task where the user clearly wants deterministic code-native output instead of a generated bitmap

## Decision tree

Think about two separate questions:

1. **Intent:** is this a new image or an edit of an existing image?
2. **Execution strategy:** is this one asset or many assets/variants?

Intent:
- If the user wants to modify an existing image while preserving parts of it, treat the request as **edit**.
- If the user provides images only as references for style, composition, mood, or subject guidance, treat the request as **generate**.
- If the user provides no images, treat the request as **generate**.

Edit semantics:
- Use the CLI `edit` subcommand for existing images and pass the accessible source path with `--image`.
- If an image is attached in the conversation but has no accessible local path, ask the user to make it available to the script through a local file path before editing.
- For edits, preserve invariants aggressively and save non-destructively by default.

Execution strategy:
- Use `generate-batch` with one job per distinct prompt when producing many distinct assets.
- Use `--n` for variants of one prompt; do not use it as a substitute for separate prompts.

Assume the user wants a new image unless they clearly ask to change an existing one.

## Workflow
1. Always use the bundled CLI; select `generate`, `edit`, or `generate-batch` based on the request.
2. Decide the intent: `generate` or `edit`.
3. Decide whether the output is preview-only or meant to be consumed by the current project.
4. Decide the execution strategy: one CLI request for one prompt, or `generate-batch` for multiple distinct prompts/assets.
5. Collect inputs up front: prompt(s), exact text (verbatim), constraints/avoid list, and any input images.
6. For every input image, label its role explicitly:
   - reference image
   - edit target
   - supporting insert/style/compositing input
7. For edits, make sure each source image is available as a local path for `--image`; use the CLI `edit` subcommand.
8. If the user asked for a photo, illustration, sprite, product image, banner, or other explicitly raster-style asset, use this skill's CLI rather than substituting SVG/HTML/CSS placeholders. If the request is for an icon, logo, or UI graphic that should match existing repo-native SVG/vector/code assets, prefer editing those directly instead.
9. Augment the prompt based on specificity:
   - If the user's prompt is already specific and detailed, normalize it into a clear spec without adding creative requirements.
   - If the user's prompt is generic, add tasteful augmentation only when it materially improves output quality.
10. Execute the request with the bundled CLI script.
11. For transparent-output requests, follow the selected provider/model guidance and preserve alpha when supported.
12. Inspect outputs and validate: subject, style, composition, text accuracy, and invariants/avoid items.
13. Iterate with a single targeted change, then re-check.
14. For preview-only work, save the CLI output to a temporary project path and render it inline when supported.
15. For project-bound work, save the selected artifact directly into the workspace and update any consuming code or references.
16. For batches or multi-asset requests, persist every requested deliverable final in the workspace unless the user explicitly asked to keep outputs preview-only. Discarded variants do not need to be kept unless requested.
17. Use `references/cli.md`, `references/image-api.md`, and `references/network.md` for model, quality, size, `input_fidelity`, masks, output format, output paths, and network setup.
18. Always report the final saved path(s) for any workspace-bound asset(s), plus the final prompt or prompt set and that the CLI script was used.

## Transparent image requests

Use the selected provider/model's documented transparency support and preserve the alpha channel. For GPT Image CLI transparency behavior, follow [references/cli.md](references/cli.md); do not silently change models.

## Prompt augmentation

Reformat user prompts into a structured, production-oriented spec. Make the user's goal clearer and more actionable, but do not blindly add detail.

Treat this as prompt-shaping guidance, not a closed schema. Use only the lines that help, and add a short extra labeled line when it materially improves clarity.

### Specificity policy

Use the user's prompt specificity to decide how much augmentation is appropriate:

- If the prompt is already specific and detailed, preserve that specificity and only normalize/structure it.
- If the prompt is generic, you may add tasteful augmentation when it will materially improve the result.

Allowed augmentations:
- composition or framing hints
- polish level or intended-use hints
- practical layout guidance
- reasonable scene concreteness that supports the stated request

Not allowed augmentations:
- extra characters or objects that are not implied by the request
- brand names, slogans, palettes, or narrative beats that are not implied
- arbitrary side-specific placement unless the surrounding layout supports it

## Use-case taxonomy (exact slugs)

Classify each request into one of these buckets and keep the slug consistent across prompts and references.

Generate:
- photorealistic-natural — candid/editorial lifestyle scenes with real texture and natural lighting.
- product-mockup — product/packaging shots, catalog imagery, merch concepts.
- ui-mockup — app/web interface mockups and wireframes; specify the desired fidelity.
- infographic-diagram — diagrams/infographics with structured layout and text.
- scientific-educational — classroom explainers, scientific diagrams, and learning visuals with required labels and accuracy constraints.
- ads-marketing — campaign concepts and ad creatives with audience, brand position, scene, and exact tagline/copy.
- productivity-visual — slide, chart, workflow, and data-heavy business visuals.
- logo-brand — logo/mark exploration, vector-friendly.
- illustration-story — comics, children’s book art, narrative scenes.
- stylized-concept — style-driven concept art, 3D/stylized renders.
- historical-scene — period-accurate/world-knowledge scenes.

Edit:
- text-localization — translate/replace in-image text, preserve layout.
- identity-preserve — try-on, person-in-scene; lock face/body/pose.
- precise-object-edit — remove/replace a specific element (including interior swaps).
- lighting-weather — time-of-day/season/atmosphere changes only.
- background-extraction — transparent background / clean cutout. Follow the selected provider/model's documented transparency support.
- style-transfer — apply reference style while changing subject/scene.
- compositing — multi-image insert/merge with matched lighting/perspective.
- sketch-to-render — drawing/line art to photoreal render.

## Shared prompt schema

Use the following labeled spec as shared prompt scaffolding for both top-level modes:

```text
Use case: <taxonomy slug>
Asset type: <where the asset will be used>
Primary request: <user's main prompt>
Input images: <Image 1: role; Image 2: role> (optional)
Scene/backdrop: <environment>
Subject: <main subject>
Style/medium: <photo/illustration/3D/etc>
Composition/framing: <wide/close/top-down; placement>
Lighting/mood: <lighting + mood>
Color palette: <palette notes>
Materials/textures: <surface details>
Text (verbatim): "<exact text>"
Constraints: <must keep/must avoid>
Avoid: <negative constraints>
```

Notes:
- `Asset type` and `Input images` are prompt scaffolding, not dedicated CLI flags.
- `Scene/backdrop` refers to the visual setting. It is not the same as the CLI `background` parameter, which controls output transparency behavior.
- Execution notes such as `Quality:`, `Input fidelity:`, masks, output format, and output paths are CLI controls; keep them separate from the visual prompt when the API exposes dedicated parameters.

Augmentation rules:
- Keep it short.
- Add only the details needed to improve the prompt materially.
- For edits, explicitly list invariants (`change only X; keep Y unchanged`).
- If any critical detail is missing and blocks success, ask a question; otherwise proceed.

## Examples

### Generation example (hero image)
```text
Use case: product-mockup
Asset type: landing page hero
Primary request: a minimal hero image of a ceramic coffee mug
Style/medium: clean product photography
Composition/framing: wide composition with usable negative space for page copy if needed
Lighting/mood: soft studio lighting
Constraints: no logos, no text, no watermark
```

### Edit example (invariants)
```text
Use case: precise-object-edit
Asset type: product photo background replacement
Primary request: replace only the background with a warm sunset gradient
Constraints: change only the background; keep the product and its edges unchanged; no text; no watermark
```

## Prompting best practices
- Structure prompt as scene/backdrop -> subject -> details -> constraints.
- Include intended use (ad, UI mock, infographic) to set the mode and polish level.
- Use camera/composition language for photorealism.
- Only use SVG/vector stand-ins when the user explicitly asked for vector output or a non-image placeholder.
- Quote exact text and specify typography + placement.
- For tricky words, spell them letter-by-letter and require verbatim rendering.
- For multi-image inputs, reference images by index and describe how they should be used.
- For edits, repeat invariants every iteration to reduce drift.
- Iterate with single-change follow-ups.
- If the prompt is generic, add only the extra detail that will materially help.
- If the prompt is already detailed, normalize it instead of expanding it.
- See `references/cli.md` and `references/image-api.md` for model, `quality`, `input_fidelity`, masks, output format, and output-path guidance.
- For transparent images, follow the provider/model guidance and preserve alpha when supported.

More prompting principles: `references/prompting.md`.
Copy/paste prompt recipes: `references/sample-prompts.md`.

## Guidance by asset type
Asset-type templates (website assets, game assets, wireframes, logo) are consolidated in `references/sample-prompts.md`.

## gpt-image-2 guidance

The CLI defaults to `gpt-image-2`.

- Use `gpt-image-2` for new CLI/API workflows unless the user confirms a different model.
- CLI `gpt-image-2` does not support `background=transparent`; ask before using `gpt-image-1.5` unless the user explicitly requested that model.
- `gpt-image-2` always uses high fidelity for image inputs; do not set `input_fidelity` with this model.
- `gpt-image-2` supports `quality` values `low`, `medium`, `high`, and `auto`.
- Use `quality low` for fast drafts, thumbnails, and quick iterations. Use `medium`, `high`, or `auto` for final assets, dense text, diagrams, identity-sensitive edits, or high-resolution outputs.
- Square images are typically fastest to generate. Use `1024x1024` for fast square drafts.
- If the user asks for 4K-style output, use `3840x2160` for landscape or `2160x3840` for portrait.
- `gpt-image-2` size may be `auto` or `WIDTHxHEIGHT` if all constraints hold: max edge `<= 3840px`, both edges multiples of `16px`, long-to-short ratio `<= 3:1`, total pixels between `655,360` and `8,294,400`.

Popular `gpt-image-2` sizes:
- `1024x1024` square
- `1536x1024` landscape
- `1024x1536` portrait
- `2048x2048` 2K square
- `2048x1152` 2K landscape
- `3840x2160` 4K landscape
- `2160x3840` 4K portrait
- `auto`

## CLI mode

### Temp and output conventions
These conventions apply to script outputs.
- Use `tmp/gptimage/` for intermediate files (for example JSONL batches); delete them when done.
- Write final artifacts under `output/gptimage/`.
- Use `--out` or `--out-dir` to control output paths; keep filenames stable and descriptive.

### Dependencies and first use

- Requires Python 3.9 or newer. The first live image generation/edit or chroma-key removal creates an isolated environment in the operating-system user cache and installs `openai` and `Pillow` automatically.
- The first setup requires network access to download packages. Later calls reuse the cached environment. Concurrent first use from Codex CLI and Codex Desktop is serialized safely.
- `--dry-run` does not install packages and does not require an API key.
- This environment is separate from the user's global Python, project virtual environments, Codex CLI, and Codex Desktop. The skill reads API configuration from `~/.agent-skills/config.json`, outside the skill installation directory.

### Environment
- `~/.agent-skills/config.json` must contain a valid `gpt_image.api_key` for live API calls. `gpt_image.base_url` and `gpt_image.model` optionally select a compatible API root and model.
- Never ask the user to paste the full key in chat. Ask them to set it locally and confirm when ready.

If the key is missing, ask the user to add it to `gpt_image.api_key` in `~/.agent-skills/config.json`; do not ask them to paste the full key in chat. For OpenAI, keys can be created at https://platform.openai.com/api-keys.

If automatic setup fails, explain that the skill needs a working Python installation with `venv`/`pip` and package download access. Do not install packages into the user's global or project Python environment as a fallback.

### Script-mode notes
- CLI commands + examples: `references/cli.md`
- API parameter quick reference: `references/image-api.md`
- Network access and sandbox requirements: `references/network.md`

## Reference map
- `references/prompting.md`: prompting principles for all image requests handled by this skill.
- `references/sample-prompts.md`: copy/paste prompt recipes for this skill's CLI workflow.
- `references/cli.md`: CLI usage via `scripts/image_gen.py`.
- `references/image-api.md`: API/CLI parameter reference.
- `references/network.md`: network/sandbox troubleshooting for CLI requests.
- `scripts/image_gen.py`: implementation used for every image request routed through this skill.
