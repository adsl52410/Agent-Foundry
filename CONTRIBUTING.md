# Contributing to Agent Foundry

Thank you for your interest in contributing! This document explains how to set up your environment, propose changes, and add plugins. The goal is to keep contributions simple, testable, and reproducible.

---

## Table of Contents
- Getting Started
- Development Workflow
- Coding Standards
- Testing
- Adding a Plugin
- Registry, Lockfile, and Reproducibility
- Versioning and Releases
- Security
- Opening Issues and Pull Requests

---

## Getting Started

### Prerequisites
- Python 3.10+ (3.11+ recommended)
- Git
- macOS, Linux, or WSL2 on Windows

### Setup
```bash
# Clone
git clone https://github.com/<your-org-or-user>/Agent-Foundry.git
cd Agent-Foundry

# Create and activate a virtual environment (example: venv)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

# Install in editable mode + dev dependencies
python -m pip install -U pip
python -m pip install -r requirements-dev.txt -e .

# Run tests to verify your environment
pytest -q
```

### Running the CLI locally
This repository exposes a Python module entrypoint.

```bash
# 確保在虛擬環境中
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 基本命令
python -m afm.cli --help
python -m afm.cli list
python -m afm.cli install hello_world
python -m afm.cli publish hello_world
python -m afm.cli remote-list
```

> **注意**：使用 `python -m afm.cli` 而非 `python -m afm`，因為 CLI 模組位於 `afm/cli.py`。

---

## Development Workflow

### Branching
- Create topic branches from `main`:
  - `feat/<short-topic>` for new features
  - `fix/<short-topic>` for bug fixes
  - `docs/<short-topic>` for documentation-only changes
  - `chore/<short-topic>` for maintenance tasks

### Commits
Use Conventional Commits where possible:
- `feat: add registry checksum verification`
- `fix: handle missing manifest fields`
- `docs: improve README quick start`
- `test: add installer unit tests`
- `chore: update dependencies`

Keep commits focused and small. Include context in the body when the subject isn’t enough.

### Pull Requests
Before opening a PR:
- Ensure code builds locally and tests pass.
- Add/adjust tests for your changes when applicable.
- Update docs (`README.md`, examples) if behavior or UX changed.
- Fill out the PR description with motivation, approach, and trade-offs.

We recommend PRs under ~400 lines of diff for easier reviews. Larger changes should be split logically.

---

## Coding Standards
- Python style: PEP 8; prefer readable, well-named symbols over brevity.
- Type hints: add where helpful for clarity and public APIs.
- Avoid deep nesting; prefer early returns and small functions.
- Comments: only for non-obvious rationale, invariants, and edge cases.

If tooling is available in your environment, run formatters/linters before committing (e.g., `black`, `ruff`, `flake8`, `isort`). If these tools are not installed, follow the existing style in the codebase.

---

## Testing
We use `pytest`.

```bash
# Run the test suite
pytest -q

# With coverage
pytest -q --cov=afm --cov-report=term-missing --cov-report=xml
```

Add tests for new features or bug fixes. Keep tests deterministic and fast. Prefer unit tests for core logic; add integration tests when behavior spans multiple components (e.g., installer + loader + registry).

---

## Adding a Plugin
Agent Foundry supports a plugin model. A minimal plugin provides a manifest and a Python module implementing the expected interface.

### Minimal layout (example)
```
my_plugin/
  plugin.py            # exposes a callable/class per the expected interface
  manifest.json        # plugin metadata and dependencies
```

### Manifest schema
At minimum:
- `name`: string
- `version`: semver string
- `description`: string
- `author`: string
- `dependencies`: object map (optional), e.g. `{ "some_plugin": ">=0.1.0" }`

See the project README for more examples and the expected fields.

### Local development

1. **創建插件目錄**：
```bash
mkdir -p afm/plugins/my_plugin
```

2. **創建 plugin.py**：
```python
def run(args):
    print(f"My plugin executed with args: {args}")
    return {"status": "success"}
```

3. **創建 manifest.json**：
```json
{
  "name": "my_plugin",
  "version": "0.1.0",
  "description": "My test plugin",
  "author": "Your Name",
  "dependencies": {}
}
```

4. **測試插件**：
```bash
# 執行插件
python -m afm.cli run my_plugin --args "test"

# 上傳到遠端 registry（用於分享）
python -m afm.cli publish my_plugin

# 從遠端安裝（驗證下載功能）
python -m afm.cli uninstall my_plugin
python -m afm.cli install my_plugin
```

5. **添加測試**：在 `tests/` 目錄添加測試，覆蓋插件的行為（盡可能 mock 外部呼叫）。

---

## Registry, Lockfile, and Reproducibility

### 路徑設定

路徑集中在 `afm/config/settings.py`：

**本地路徑**：
- `DATA_DIR = 'data'` - 本地資料目錄
- `REGISTRY_PATH = f"{DATA_DIR}/registry.json"` - 本地插件註冊表
- `LOCKFILE_PATH = f"{DATA_DIR}/lock.json"` - 版本鎖定檔
- `PLUGIN_DIR = 'afm/plugins'` - 已安裝的插件目錄

**遠端 Registry 路徑**：
- `REMOTE_REGISTRY_DIR` - 遠端 registry 根目錄（預設：`~/Desktop/af-registry/`）
- `REMOTE_PLUGINS_DIR` - 遠端插件目錄（`{REMOTE_REGISTRY_DIR}/plugins/`）
- `REMOTE_INDEX_PATH` - 遠端索引檔案（`{REMOTE_REGISTRY_DIR}/index.json`）

### 工作流程

1. **開發插件**：在 `afm/plugins/{your_plugin}/` 創建插件
2. **上傳到遠端**：`python -m afm.cli publish {your_plugin}`
3. **安裝插件**：`python -m afm.cli install {your_plugin}`（從遠端下載）
4. **生成鎖定檔**：`python -m afm.cli lock`（固定所有插件版本）
5. **提交變更**：提交 `data/registry.json` 和 `data/lock.json` 以確保可重現性

### 遠端 Registry 結構

```
~/Desktop/af-registry/
├── index.json              # 插件索引（自動維護）
└── plugins/
    └── {plugin_name}/
        └── {version}/
            ├── plugin.py
            └── manifest.json
```

`index.json` 格式：
```json
{
  "plugin_name": {
    "versions": ["0.1.0", "0.2.0"],
    "latest": "0.2.0"
  }
}
```

---

## Versioning and Releases
- Use SemVer: `MAJOR.MINOR.PATCH`.
- Bump the version when behavior changes, even internally, if it affects users or plugins.
- Keep `CHANGELOG` entries (in PR bodies or a dedicated file) describing user-facing changes.
- For plugins, version independently and update the registry accordingly.

Release checklist:
1. Ensure tests and coverage pass.
2. Update version(s) and changelog.
3. Verify lockfile/regenerated metadata if relevant.
4. Tag the release and publish to the registry/package index as applicable.

---

## Security
- Do not include secrets in code or tests.
- Report vulnerabilities privately via security contact or a private issue/email (if available). Avoid sharing exploit details publicly before a fix is ready.
- Consider threat implications when adding new plugin capabilities.

---

## Opening Issues and Pull Requests
- Issues: provide steps to reproduce, expected vs actual results, environment details (OS, Python, commit).
- Feature requests: describe the use case and why existing features aren’t sufficient.
- Pull Requests: link related issues, include before/after behavior, and migration notes if relevant.

Thank you for helping make Agent Foundry better!


