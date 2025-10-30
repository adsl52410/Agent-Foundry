import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from afm.cli import main as cli


@pytest.fixture()
def runner(tmp_path, monkeypatch):
    # Run in a temporary directory to avoid polluting data/registry.json
    monkeypatch.chdir(tmp_path)
    # Create minimal directory structure
    (tmp_path / "afm" / "core").mkdir(parents=True)
    (tmp_path / "afm" / "plugins").mkdir(parents=True)
    (tmp_path / "afm" / "config").mkdir(parents=True)

    # We import the installed afm package; only a clean cwd is required
    return CliRunner()


def test_install_and_list_and_run(runner, tmp_path):
    # Install a fake plugin
    result_install = runner.invoke(cli, ["install", "hello_world"])
    assert result_install.exit_code == 0
    assert "✅ Simulating download of plugin" in result_install.output

    # Check registry.json content
    registry_path = tmp_path / "data" / "registry.json"
    assert registry_path.exists()
    data = json.loads(registry_path.read_text())
    assert "hello_world" in data

    # Listing should include hello_world (table output)
    result_list = runner.invoke(cli, ["list"])
    assert result_list.exit_code == 0
    assert "hello_world" in result_list.output

    # Run the plugin
    result_run = runner.invoke(cli, ["run", "hello_world", "--args", "TEST_ARG"])
    assert result_run.exit_code == 0
    assert "Hello from" in result_run.output or "Hello World Plugin:" in result_run.output


