# Agent Foundry (afm)

Large Language Models (LLMs) aren’t just about chatting — their real magic comes when they can **use tools to act in the real world**.

Imagine an AI that doesn’t just answer questions, but can open windows, take screenshots, run OCR, fetch data, or even get tasks done for you.

Here’s what we’re building:

- **A community-driven toolbox** – anyone can contribute their own tool, or use what others have shared.
- **A reproducible, governed ecosystem** – every plugin has versions, release channels (stable/beta/canary), and lockfiles to guarantee consistent results.
- **A fun workshop** – like a forge for AI, where people craft new abilities, share them, remix them, and level them up together.

Agent Foundry is for developers, researchers, and tinkerers who want to mix and match tools easily, making AI into a real shared infrastructure.

## Installation

```bash
pip install afm
```

## Usage

```bash
# Install a plugin
python -m afm install hello_world

# List installed plugins
python -m afm list

# Run a plugin
python -m afm run hello_world --args "test"
```

## Plugin management

```bash
# Uninstall a plugin
python -m afm uninstall hello_world

# Update a plugin (to latest or a specific version)
python -m afm update hello_world
python -m afm update hello_world --version 0.2.0

# Regenerate lockfile (pins exact versions from registry)
python -m afm lock
```

## Manifest schema (plugin/manifest.json)

Required/optional fields:
- name: string
- version: string (semver)
- description: string
- author: string
- dependencies: object, e.g. { "some_plugin": ">=0.1.0" }

## Configuration

Paths are centralized in `afm/config/settings.py`:
- `DATA_DIR = 'data'`
- `REGISTRY_PATH = f"{DATA_DIR}/registry.json"`
- `LOCKFILE_PATH = f"{DATA_DIR}/lock.json"`
- `PLUGIN_DIR = 'afm/plugins'`

## Testing

```bash
python -m pip install -r requirements-dev.txt -e .
pytest -q
# With coverage
pytest -q --cov=afm --cov-report=term-missing --cov-report=xml
```

 
