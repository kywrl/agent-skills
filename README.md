# GPT Image

这是一个面向 AI Agent 的图像生成技能仓库，当前提供 `gpt-image` 技能。技能通过随附的 Python CLI 调用 OpenAI Images API 或兼容接口，可生成图片、编辑图片、批量生成，并可在本地移除纯色背景。

## 使用

### 安装技能

需要先安装 Node.js（提供 `npx`）和 Git，然后通过 [Vercel `skills` CLI](https://github.com/vercel-labs/skills) 从 GitHub 安装：

```bash
npx skills add kywrl/agent-skills --skill gpt-image
```

常用安装选项：

- `--agent`（或 `-a`）：指定目标 Agent，名称格式见下表。
- `--global`（或 `-g`）：安装到用户级目录，供当前用户的所有项目使用；不加该选项时默认安装到当前项目，请在目标项目根目录运行。

| Agent | `--agent` 用法 |
| --- | --- |
| Codex | `--agent codex` |
| Claude Code | `--agent claude-code` |
| Command Code | `--agent command-code` |

例如，将技能安装到 Codex 的用户级目录：

```bash
npx skills add kywrl/agent-skills --skill gpt-image --agent codex --global
```

也可以直接使用仓库中的脚本：

```bash
python gpt-image/scripts/image_gen.py --help
```

### 配置 API

首次运行 CLI 时，会在用户主目录创建 `~/.agent-skills/config.json`。编辑该文件，填入 API 密钥；如使用兼容服务，也可以设置接口根地址和模型：

```json
{
  "gpt_image": {
    "api_key": "YOUR_API_KEY",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-image-2"
  }
}
```

`base_url` 填 API 根地址，不要附加 `/images/generations` 或 `/images/edits`。命令行参数 `--api-key`、`--base-url` 和 `--model` 可以覆盖配置文件中的对应值。CLI 不读取 API 密钥或模型相关环境变量。请勿将真实密钥提交到仓库。

### 生成图片

```bash
python gpt-image/scripts/image_gen.py generate --prompt "清晨山间的一座木屋，柔和自然光，写实摄影" --size 1536x1024 --quality high --out output/gptimage/alpine-cabin.png
```

常用参数：

- `--prompt` 或 `--prompt-file`：提供提示词。
- `--size`：图片尺寸，默认 `auto`。
- `--quality`：`low`、`medium`、`high` 或 `auto`，默认 `medium`。
- `--n`：为同一提示词生成多个版本。
- `--out`：输出文件路径，默认 `output/gptimage/output.png`。
- `--force`：允许覆盖已存在的输出文件。
- `--dry-run`：只显示请求和输出路径，不调用 API。

### 编辑图片

```bash
python gpt-image/scripts/image_gen.py edit --image input/photo.png --prompt "只将背景替换为暖色日落，保持主体不变" --out output/gptimage/sunset-edit.png
```

可重复使用 `--image` 提供多张输入图片，也可用 `--mask` 指定编辑蒙版。模型对蒙版和图像参数的支持有所不同，详见 [图像 API 参数](gpt-image/references/image-api.md)。

### 批量生成

JSONL 文件每行描述一个生成任务：

```jsonl
{"prompt":"雪林中的灰狼，侧面构图","size":"1024x1024"}
{"prompt":"极简白色陶瓷咖啡杯产品照","size":"1536x1024","quality":"high"}
```

运行批处理时必须指定输出目录：

```bash
python gpt-image/scripts/image_gen.py generate-batch --input prompts.jsonl --out-dir output/gptimage/batch --concurrency 5
```

### 移除纯色背景

```bash
python gpt-image/scripts/remove_chroma_key.py --input output/gptimage/subject-green-screen.png --out output/gptimage/subject-transparent.png --key-color "#00ff00" --soft-matte --spill-cleanup
```

该工具在本地处理图片，不调用图像生成 API；输出支持 PNG 和 WebP。

### 运行环境与更多说明

需要 Python 3.9 或更高版本。首次执行实际生成、编辑或去背时，脚本会在用户缓存目录创建独立虚拟环境并安装 `openai` 和 `Pillow`，因此首次初始化需要网络。该环境不会修改系统 Python 或项目虚拟环境。使用 `--dry-run` 不需要 API 密钥、网络或已安装依赖。

默认模型为 `gpt-image-2`。该模型不支持 `background=transparent`；透明输出能力取决于模型和服务商。配置、网络限制、完整参数和提示词建议见下方参考资料。

## 开发

### 仓库结构

```text
gpt-image/
├── SKILL.md                    # Agent 使用流程与行为约定
├── agents/openai.yaml          # 技能的 Agent 元数据
├── scripts/
│   ├── image_gen.py            # 生成、编辑和批量生成 CLI
│   ├── remove_chroma_key.py    # 本地纯色背景移除工具
│   └── _runtime.py             # 私有 Python 环境初始化
├── references/                 # CLI、API、网络和提示词文档
├── assets/                     # 技能资源
├── requirements.txt            # 技能运行时依赖
├── LICENSE.txt
└── NOTICE
```

### 本地开发

在仓库根目录运行 CLI。`--dry-run` 可用于检查参数解析、请求内容和输出路径，不需要密钥或安装依赖：

```bash
python gpt-image/scripts/image_gen.py generate --prompt "本地预览" --out output/gptimage/preview.png --dry-run
```

验证真实 API 调用或修改去背逻辑时，按“使用”一节配置密钥并运行相应命令。脚本会自行管理隔离的运行时环境；依赖列表统一维护在 `gpt-image/requirements.txt`。

### 修改约定

- 保持技能入口和行为说明与 CLI 一致；更新命令或参数时，同步检查 `gpt-image/SKILL.md` 和 `gpt-image/references/cli.md`。
- API 参数与服务商差异记录在 `gpt-image/references/image-api.md`、`gpt-image/references/api-compatibility.md`；网络问题记录在 `gpt-image/references/network.md`。
- 提示词原则和示例分别维护在 `gpt-image/references/prompting.md` 与 `gpt-image/references/sample-prompts.md`。
- 不要在代码、文档示例或提交中放入真实 API 密钥、用户配置或生成产物。

### 参考资料

- [CLI 完整说明](gpt-image/references/cli.md)
- [图像 API 参数](gpt-image/references/image-api.md)
- [API 兼容性与配置](gpt-image/references/api-compatibility.md)
- [网络配置与排查](gpt-image/references/network.md)
- [提示词编写指南](gpt-image/references/prompting.md)
- [提示词示例](gpt-image/references/sample-prompts.md)
- [完整技能流程](gpt-image/SKILL.md)
- [许可证](gpt-image/LICENSE.txt) 与 [NOTICE](gpt-image/NOTICE)
