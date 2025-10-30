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

## ⚙️ Core Features (MVP → Future)  

- 🔌 **Plugin System** — standardized interfaces for AI, OCR, window, screenshot, and more.  
- 📦 **Registry (File-system based)** — simple NAS/local folder registry with `index.json`, `meta.json`, `checksums.txt`.  
- 🔒 **Lockfiles** — guarantee reproducibility across machines and teams.  
- 🛠 **CLI & API** — `agent-foundry` CLI for installing, verifying, and running pipelines.  
- 🚀 **Pipeline Execution** — start with Python APIs, later support declarative YAML + lock.  

---

## ⚡ Quick Start (MVP idea)  

```bash
# Lock down plugin versions
agent-foundry lock resolve --from ./af-registry

# Install and verify plugins
agent-foundry plugins install --from ./af-registry
agent-foundry plugins verify --from ./af-registry

# Run a pipeline (e.g. Window → Screenshot → OCR → AI)
agent-foundry line --pipeline examples/line_pipeline_demo.py --save-artifacts
```

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

```bash
# Build the wheel
agent-foundry plugin build

# Put it into the registry
mkdir -p ./af-registry/plugins/ocr.tesseract/0.4.2
cp dist/agent_foundry_ocr_tesseract-0.4.2-*.whl ./af-registry/plugins/ocr.tesseract/0.4.2/
agent-foundry cloud fs checksum ./af-registry/plugins/ocr.tesseract/0.4.2
agent-foundry cloud fs promote ocr.tesseract --version 0.4.2 --channel stable --root ./af-registry
agent-foundry cloud fs update-index ./af-registry
```

### 5. Use it in a pipeline

```python
from agent_foundry.container import Container

c = Container(registry_map={"ocr.tesseract": "agent_foundry_ocr_tesseract@0.4.2"})
ocr = c.resolve("ocr.tesseract")

res = ocr.extract_text("sample.png")
print(res)
# => {"success": True, "data": {"text": "Hello world"}, "meta": {"engine": "tesseract"}}
```

---

## 🤝 How to Contribute

Agent Foundry is meant to be **built together**. You can help by:

1. Submitting new plugins (OCR, AI adapters, integrations).
2. Writing docs, guides, or examples.
3. Improving testing, CI/CD, and conformance checks.
4. Sharing ideas and feedback in issues/discussions.

👉 See `CONTRIBUTING.md` (coming soon) for setup steps.

---

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

