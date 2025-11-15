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

### Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Activate virtual environment (before each use)
source venv/bin/activate

# Publish plugin to remote registry (Desktop folder)
python3 -m afm.cli publish hello_world

# View available plugins in remote registry
python3 -m afm.cli remote-list

# Install plugin from remote
python3 -m afm.cli install hello_world

# List installed plugins
python3 -m afm.cli list

# Run plugin
python3 -m afm.cli run hello_world --args "your parameters"

# Update plugin to latest version
python3 -m afm.cli update hello_world

# Generate lockfile
python3 -m afm.cli lock
```

> **Note**: Remote registry default location is `~/Desktop/af-registry/`, can be modified in `afm/config/settings.py`.

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

Use CLI to upload plugin to remote registry:

```bash
# Publish plugin (automatically reads version from manifest.json)
python3 -m afm.cli publish ocr.tesseract

# Or specify version
python3 -m afm.cli publish ocr.tesseract --version 0.4.2
```

Plugin will be automatically uploaded to `~/Desktop/af-registry/plugins/ocr.tesseract/0.4.2/` and `index.json` will be updated.

### 5. Install and use the plugin

```bash
# Install from remote
python3 -m afm.cli install ocr.tesseract

# Or install specific version
python3 -m afm.cli install ocr.tesseract --version 0.4.2

# Run plugin
python3 -m afm.cli run ocr.tesseract --args '{"image_path": "sample.png"}'
```

### 6. Plugin Registry Structure

Remote registry structure (default at `~/Desktop/af-registry/`):

```
af-registry/
├── index.json              # Plugin index, records all available plugins and versions
└── plugins/
    └── {plugin_name}/
        └── {version}/
            ├── plugin.py
            └── manifest.json
```

Locally installed plugins are located at `afm/plugins/{plugin_name}/`, registry information is in `data/registry.json`.

---

## 📚 CLI Command Reference

### Plugin Management

- `install <name> [--version VERSION]` - Install plugin from remote registry (automatically uses latest version if not specified)
- `list` - List installed plugins
- `uninstall <name>` - Uninstall plugin
- `update <name> [--version VERSION]` - Update plugin (automatically checks and updates to latest version if not specified)
- `run <name> [--args ARGS]` - Run plugin

### Registry Operations

- `publish <name> [--version VERSION]` - Upload local plugin to remote registry
- `remote-list` - List all available plugins in remote registry
- `lock` - Regenerate lockfile (fix exact versions of all current plugins)

### Examples

```bash
# Complete workflow
python3 -m afm.cli publish my_plugin          # Publish plugin
python3 -m afm.cli remote-list                # View remote plugins
python3 -m afm.cli install my_plugin          # Install plugin
python3 -m afm.cli list                        # View installed
python3 -m afm.cli run my_plugin --args "test" # Run plugin
python3 -m afm.cli update my_plugin            # Update to latest version
python3 -m afm.cli lock                        # Generate lockfile
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

