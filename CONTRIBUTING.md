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
# Ensure you're in the virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Basic commands
python -m afm.cli --help
python -m afm.cli list
python -m afm.cli install hello_world
python -m afm.cli publish hello_world
python -m afm.cli remote-list
```

> **Note**: Use `python -m afm.cli` instead of `python -m afm`, as the CLI module is located at `afm/cli.py`.

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

1. **Create plugin directory**:
```bash
mkdir -p afm/plugins/my_plugin
```

2. **Create plugin.py**:
```python
def run(args):
    print(f"My plugin executed with args: {args}")
    return {"status": "success"}
```

3. **Create manifest.json**:
```json
{
  "name": "my_plugin",
  "version": "0.1.0",
  "description": "My test plugin",
  "author": "Your Name",
  "dependencies": {}
}
```

4. **Test plugin**:
```bash
# Run plugin
python -m afm.cli run my_plugin --args "test"

# Publish to remote registry (for sharing)
python -m afm.cli publish my_plugin

# Install from remote (verify download functionality)
python -m afm.cli uninstall my_plugin
python -m afm.cli install my_plugin
```

5. **Add tests**: Add tests in `tests/` directory covering plugin behavior (mock external calls as much as possible).

---

## Registry, Lockfile, and Reproducibility

### Path Configuration

Paths are centralized in `afm/config/settings.py`:

**Local paths**:
- `DATA_DIR = 'data'` - Local data directory
- `REGISTRY_PATH = f"{DATA_DIR}/registry.json"` - Local plugin registry
- `LOCKFILE_PATH = f"{DATA_DIR}/lock.json"` - Version lockfile
- `PLUGIN_DIR = 'afm/plugins'` - Installed plugins directory

**Remote Registry paths**:
- `REMOTE_REGISTRY_DIR` - Remote registry root directory (default: `~/Desktop/af-registry/`)
- `REMOTE_PLUGINS_DIR` - Remote plugins directory (`{REMOTE_REGISTRY_DIR}/plugins/`)
- `REMOTE_INDEX_PATH` - Remote index file (`{REMOTE_REGISTRY_DIR}/index.json`)

### Workflow

1. **Develop plugin**: Create plugin in `afm/plugins/{your_plugin}/`
2. **Publish to remote**: `python -m afm.cli publish {your_plugin}`
3. **Install plugin**: `python -m afm.cli install {your_plugin}` (downloads from remote)
4. **Generate lockfile**: `python -m afm.cli lock` (fixes all plugin versions)
5. **Commit changes**: Commit `data/registry.json` and `data/lock.json` to ensure reproducibility

### Remote Registry Structure

```
~/Desktop/af-registry/
├── index.json              # Plugin index (automatically maintained)
└── plugins/
    └── {plugin_name}/
        └── {version}/
            ├── plugin.py
            └── manifest.json
```

`index.json` format:
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


