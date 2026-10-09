# GPT Image 图像生成工具

本项目包含一个用于生成和编辑图片的 Python CLI，以及提示词参考资料和色键背景移除工具。CLI 通过 OpenAI Images API 或兼容接口工作，可生成单张图片、编辑现有图片，也可按 JSONL 批量生成。

## 项目结构

- `gpt-image/SKILL.md`：图像生成工作流程、提示词组织建议和使用约束。
- `gpt-image/scripts/image_gen.py`：图片生成、编辑和批处理命令行工具。
- `gpt-image/scripts/remove_chroma_key.py`：移除纯色背景并生成带透明通道的图片。
- `gpt-image/references/`：CLI、API 参数、提示词和网络配置说明。
- `gpt-image/assets/`：工具相关图片资源。

## 通过 skills CLI 安装

本项目可通过 Vercel `skills` CLI 从 GitHub 直接安装：

```bash
npx skills add kywrl/agent-skills --skill gpt-image
```

## 环境要求

- Python 3.9 或更高版本
- 首次生成、编辑图片或运行色键去背景功能时，需要联网下载 Python 依赖
- 生成或编辑图片仍需要配置 `GPT_IMAGE_API_KEY` 或 `OPENAI_API_KEY`

技能首次运行时会在当前操作系统用户的缓存目录中创建独立虚拟环境，并自动安装 `openai` 和 `Pillow`。后续运行会复用该环境；不会改动系统 Python、项目虚拟环境或 Codex CLI / Desktop 自身的运行环境。CLI 和 Desktop 同时首次启动时会安全串行完成初始化。

若只使用 `--dry-run` 查看请求内容，无需 API 密钥、网络连接或安装这些依赖。

## 配置 API

`image_gen.py` 从用户主目录下的 `~/.agent-skills/config.json` 读取默认配置。首次运行时会自动创建该文件，初始内容如下：

```json
{
  "gpt_image": {
    "api_key": "YOUR_API_KEY",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-image-2"
  }
}
```

将 `gpt_image.api_key` 替换为你的 API 密钥；使用 OpenAI 兼容接口时，也可修改 `gpt_image.base_url` 和 `gpt_image.model`。`base_url` 应为接口根地址，不要附加 `/images/generations` 或 `/images/edits`。命令行参数 `--api-key`、`--base-url` 和 `--model` 可分别覆盖文件中的对应值。脚本不读取 `GPT_IMAGE_API_KEY`、`OPENAI_API_KEY`、`GPT_IMAGE_BASE_URL` 或 `GPT_IMAGE_MODEL` 环境变量。

配置文件必须是 JSON 对象，且 `gpt_image.api_key`、`gpt_image.base_url`、`gpt_image.model` 的值都必须是字符串；`gpt_image.base_url` 和 `gpt_image.model` 不能为空。请勿将真实密钥提交到版本库。使用 `--dry-run` 时可以不配置 API 密钥。

## 使用方法

以下命令均从项目根目录运行。

### 预览请求（不调用 API）

```bash
python gpt-image/scripts/image_gen.py generate --prompt "一只趴在窗边的橘猫" --out output/imagegen/cat.png --dry-run
```

### 生成图片

```bash
python gpt-image/scripts/image_gen.py generate \
  --prompt "清晨山间的一座木屋，柔和自然光，写实摄影" \
  --size 1536x1024 \
  --quality high \
  --out output/imagegen/alpine-cabin.png
```

### 编辑图片

```bash
python gpt-image/scripts/image_gen.py edit \
  --image input/photo.png \
  --prompt "只将背景替换为暖色日落，保持主体和边缘不变" \
  --out output/imagegen/sunset-edit.png
```

可选地使用 `--mask mask.png` 指定编辑蒙版。编辑时可重复传入 `--image` 添加多张输入图片。

### 批量生成

为每项任务在 JSONL 文件中写一行 JSON：

```jsonl
{"prompt":"雪林中的灰狼，侧面构图","size":"1024x1024"}
{"prompt":"极简白色陶瓷咖啡杯产品照","size":"1536x1024","quality":"high"}
```

运行批处理：

```bash
python gpt-image/scripts/image_gen.py generate-batch \
  --input prompts.jsonl \
  --out-dir output/imagegen/batch \
  --concurrency 5
```

### 移除纯色背景

```bash
python gpt-image/scripts/remove_chroma_key.py \
  --input output/imagegen/subject-green-screen.png \
  --out output/imagegen/subject-transparent.png \
  --key-color "#00ff00" \
  --soft-matte \
  --spill-cleanup
```

输入图应使用纯色背景；输出格式支持 PNG 或 WebP。该脚本进行本地处理，不调用图像生成 API。

## 常用选项

- `--size`：图片尺寸；默认为 `auto`。`gpt-image-2` 支持满足模型约束的自定义尺寸。
- `--quality`：`low`、`medium`、`high` 或 `auto`；默认为 `medium`。
- `--n`：为同一提示词生成多个版本。
- `--prompt-file`：从 UTF-8 文本文件读取提示词。
- `--out`：指定输出文件；默认写入 `output/imagegen/output.png`。
- `--force`：允许覆盖已存在的目标文件。
- `--dry-run`：打印请求信息但不发起 API 调用。

透明背景支持取决于所用模型和服务商。使用 `gpt-image-2` 时，API 的 `background=transparent` 不受支持；请参阅参考文档了解兼容方式和限制。

## 参考资料

- [CLI 使用说明](gpt-image/references/cli.md)
- [图像 API 参数](gpt-image/references/image-api.md)
- [API 兼容性与配置](gpt-image/references/api-compatibility.md)
- [网络配置说明](gpt-image/references/network.md)
- [提示词编写指南](gpt-image/references/prompting.md)
- [提示词示例](gpt-image/references/sample-prompts.md)
- [完整工作流程](gpt-image/SKILL.md)

## 许可证

请参阅 [`gpt-image/LICENSE.txt`](gpt-image/LICENSE.txt) 和 [`gpt-image/NOTICE`](gpt-image/NOTICE)。
