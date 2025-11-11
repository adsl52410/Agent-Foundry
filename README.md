# Agent Foundry  

We believe the real power of LLMs isn’t just in chatting — it’s in the **tools** they can use.  

Agent Foundry is an **open-source toolbox and plugin ecosystem** for building, sharing, and combining tools that make AI useful in the real world. Think of it as a forge 🔨 where the community co-creates tools, versions them, and makes sure everything is reproducible.  

---

## 🌟 Vision  

- **Tools-first AI** — LLMs become powerful when they can call tools to act.  
- **Community-built** — anyone can create new plugins (OCR, screenshots, window control, AI analysis, etc.) and share them.  
- **Reproducible & governed** — plugins come with versioning, release channels (stable/beta/canary), and lockfiles to ensure consistent results.  
- **Composable pipelines** — mix and match tools into repeatable workflows, either programmatically or declaratively.  

---

## ⚙️ Core Features  

- 🔌 **Plugin System** — standardized interfaces for AI, OCR, window, screenshot, and more.  
- 📦 **Remote Registry** — file-system based registry (default: `~/Desktop/af-registry/`) with version management and `index.json`.  
- 📥 **Plugin Management** — install, update, and publish plugins via CLI with automatic version resolution.  
- 🔒 **Lockfiles** — guarantee reproducibility across machines and teams.  
- 🛠 **CLI** — comprehensive command-line interface for plugin lifecycle management.  
- 🚀 **Pipeline Execution** — run plugins individually or compose them into workflows.  

---

## ⚡ Quick Start  

### 環境設定

```bash
# 創建並啟動虛擬環境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
```

### 基本使用

```bash
# 啟動虛擬環境（每次使用前）
source venv/bin/activate

# 上傳插件到遠端 registry（桌面資料夾）
python3 -m afm.cli publish hello_world

# 查看遠端可用的插件
python3 -m afm.cli remote-list

# 從遠端安裝插件
python3 -m afm.cli install hello_world

# 查看已安裝的插件
python3 -m afm.cli list

# 執行插件
python3 -m afm.cli run hello_world --args "你的參數"

# 更新插件到最新版本
python3 -m afm.cli update hello_world

# 生成鎖定檔
python3 -m afm.cli lock
```

> **注意**：遠端 registry 預設位置在 `~/Desktop/af-registry/`，可在 `afm/config/settings.py` 中修改。

---

## 🔌 Example Plugin: `ocr.tesseract`

Here’s how a plugin looks in Agent Foundry.
Each plugin just needs to follow a standard **interface (Protocol)** and return a consistent result format.

### 1. Implement the interface

```python
# agent_foundry_ocr_tesseract/ocr_plugin.py
from agent_foundry.interfaces import OCRService, Result
import pytesseract
from PIL import Image

class TesseractOCR(OCRService):
    def initialize(self, config: dict) -> bool:
        return True  # load configs if needed

    def extract_text(self, image_path: str) -> Result:
        try:
            text = pytesseract.image_to_string(Image.open(image_path))
            return {"success": True, "data": {"text": text}, "meta": {"engine": "tesseract"}}
        except Exception as e:
            return {"success": False, "error": {"code": "OCRFailed", "message": str(e)}}
```

### 2. Register it as a plugin

```toml
# pyproject.toml
[project.entry-points."agent_foundry.plugins"]
"ocr.tesseract" = "agent_foundry_ocr_tesseract.ocr_plugin:TesseractOCR"
```

### 3. Add metadata for the registry

`meta.json`

```json
{
  "name": "agent_foundry_ocr_tesseract",
  "version": "0.4.2",
  "core": ">=0.3,<0.4",
  "apis": ["OCRService@1"],
  "description": "OCR plugin using Tesseract"
}
```

`checksums.txt`

```
sha256  agent_foundry_ocr_tesseract-0.4.2-py3-none-any.whl  a7d2...9f
```

### 4. Publish to the registry

使用 CLI 上傳插件到遠端 registry：

```bash
# 上傳插件（自動讀取 manifest.json 中的版本）
python3 -m afm.cli publish ocr.tesseract

# 或指定版本
python3 -m afm.cli publish ocr.tesseract --version 0.4.2
```

插件會自動上傳到 `~/Desktop/af-registry/plugins/ocr.tesseract/0.4.2/`，並更新 `index.json`。

### 5. Install and use the plugin

```bash
# 從遠端安裝
python3 -m afm.cli install ocr.tesseract

# 或安裝特定版本
python3 -m afm.cli install ocr.tesseract --version 0.4.2

# 執行插件
python3 -m afm.cli run ocr.tesseract --args '{"image_path": "sample.png"}'
```

### 6. Plugin Registry Structure

遠端 registry 結構（預設在 `~/Desktop/af-registry/`）：

```
af-registry/
├── index.json              # 插件索引，記錄所有可用插件和版本
└── plugins/
    └── {plugin_name}/
        └── {version}/
            ├── plugin.py
            └── manifest.json
```

本地安裝的插件位於 `afm/plugins/{plugin_name}/`，註冊表資訊在 `data/registry.json`。

---

## 📚 CLI 命令參考

### 插件管理

- `install <name> [--version VERSION]` - 從遠端 registry 安裝插件（未指定版本時自動使用最新版本）
- `list` - 列出已安裝的插件
- `uninstall <name>` - 解除安裝插件
- `update <name> [--version VERSION]` - 更新插件（未指定版本時自動檢查並更新到最新版本）
- `run <name> [--args ARGS]` - 執行插件

### Registry 操作

- `publish <name> [--version VERSION]` - 上傳本地插件到遠端 registry
- `remote-list` - 列出遠端 registry 中所有可用的插件
- `lock` - 重新生成鎖定檔（固定當前所有插件的確切版本）

### 範例

```bash
# 完整工作流程
python3 -m afm.cli publish my_plugin          # 上傳插件
python3 -m afm.cli remote-list                # 查看遠端插件
python3 -m afm.cli install my_plugin          # 安裝插件
python3 -m afm.cli list                        # 查看已安裝
python3 -m afm.cli run my_plugin --args "test" # 執行插件
python3 -m afm.cli update my_plugin            # 更新到最新版本
python3 -m afm.cli lock                        # 生成鎖定檔
```

## 🤝 How to Contribute

Agent Foundry is meant to be **built together**. You can help by:

1. Submitting new plugins (OCR, AI adapters, integrations).
2. Writing docs, guides, or examples.
3. Improving testing, CI/CD, and conformance checks.
4. Sharing ideas and feedback in issues/discussions.

👉 See `CONTRIBUTING.md` for setup steps and development guidelines.

---

 ## 📦 Parameters and I/O Specification

 Agent Foundry plugins and pipelines follow a consistent contract for inputs and outputs to enable composition, testing, and reproducibility.

 ### Parameters

 - Format: JSON object (UTF-8)
 - Validation: JSON Schema (Draft 7+) or Pydantic models (recommended in Python)
 - Versioning: Schemas should be versioned alongside the plugin (e.g., `OCRService@1`)

 Example schema (JSON Schema):

 ```json
 {
   "$schema": "https://json-schema.org/draft-07/schema#",
   "$id": "https://agent-foundry.dev/schemas/ocr.extract_text@1.json",
   "title": "OCR.extract_text parameters",
   "type": "object",
   "required": ["image_path"],
   "properties": {
     "image_path": { "type": "string" },
     "lang": { "type": "string", "default": "eng" },
     "dpi": { "type": "integer", "minimum": 72, "maximum": 1200 }
   },
   "additionalProperties": false
 }
 ```

 Recommended validation flow:
 1) Load JSON params → 2) Validate against schema → 3) Pass typed object to implementation.

 ### Standard Output/Errors/Exit Code

 - stdout: Structured JSON result on success
 - stderr: Human-readable logs, warnings, and error diagnostics
 - exit code: `0` for success; non-zero for failure (e.g., `2` for validation error, `3` for runtime error)

 Success payload shape:

 ```json
 {
   "success": true,
   "data": { /* task-specific result */ },
   "meta": { "plugin": "ocr.tesseract", "version": "0.4.2", "elapsed_ms": 123 }
 }
 ```

 Error payload shape (written to stdout for machine consumption, details to stderr):

 ```json
 {
   "success": false,
   "error": {
     "code": "ValidationError",
     "message": "'image_path' is required",
     "details": { "path": ["image_path"], "schema": "ocr.extract_text@1" }
   },
   "meta": { "plugin": "ocr.tesseract", "version": "0.4.2" }
 }
 ```

 Suggested exit codes:
 - 2: Parameter/Schema validation error
 - 3: Dependency or environment error (e.g., missing binary/model)
 - 4: External I/O failure (network/filesystem)
 - 5: Plugin-defined runtime error

## 🗺 Roadmap

* **M1**: Core skeleton (interfaces, container, CLI, file-registry driver, lock system).
* **M2**: Plugin ecosystem (AI/OCR/Window/Screenshot as separate packages, lock + verify + checksum).
* **M3**: Docs & conformance tests (PLUGIN_GUIDE, VERSIONING, SECURITY, CI).
* **M4**: Declarative YAML pipelines, multi-version coexistence, optional signing.

---

## 📜 License

MIT — free to use, share, and modify.

---

✨ Agent Foundry is not just another framework — it’s a **community forge for AI tools**.
Let’s build the toolbox that makes LLMs truly useful.

