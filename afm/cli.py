import click
import os
from afm.core.installer import (
    install_plugin, uninstall_plugin, update_plugin, write_lockfile,
    publish_plugin, list_remote_plugins
)
from afm.core.registry import list_plugins
from afm.core.loader import run_plugin
from afm.config.settings import PLUGIN_REGISTRY_API_URL
from rich.console import Console

console = Console()

@click.group()
def main():
    pass

@main.command()
@click.argument('name')
@click.option('--version', default=None, help='Plugin version to install (e.g. 0.2.0). If not specified, uses latest from remote or default.')
def install(name, version):
    """Install a plugin from remote registry or use local simulation."""
    try:
        install_plugin(name, version)
    except Exception as e:
        raise click.ClickException(str(e))

@main.command()
def list():
    try:
        list_plugins()
    except Exception as e:
        raise click.ClickException(str(e))

@main.command()
@click.argument('name')
@click.option('--args', default='', help='Plugin args')
def run(name, args):
    try:
        run_plugin(name, args)
    except Exception as e:
        raise click.ClickException(str(e))

@main.command()
@click.argument('name')
def uninstall(name):
    """Uninstall a plugin and remove it from registry and lockfile."""
    try:
        uninstall_plugin(name)
    except Exception as e:
        raise click.ClickException(str(e))

@main.command()
@click.argument('name')
@click.option('--version', default=None, help='Target version, e.g. 0.2.0')
def update(name, version):
    """Update a plugin to the latest or specified version."""
    try:
        update_plugin(name, version)
    except Exception as e:
        raise click.ClickException(str(e))

@main.command(name="lock")
def lock_cmd():
    """Regenerate lockfile from current registry (pins exact versions)."""
    try:
        write_lockfile()
    except Exception as e:
        raise click.ClickException(str(e))


@main.command()
@click.argument('name')
@click.option('--version', default=None, help='Plugin version to publish. If not specified, uses version from manifest.')
def publish(name, version):
    """Publish a local plugin to remote registry (API or legacy file system)."""
    try:
        publish_plugin(name, version)
    except Exception as e:
        raise click.ClickException(str(e))


@main.command(name="remote-list")
def remote_list():
    """List all plugins available in remote registry."""
    try:
        list_remote_plugins()
    except Exception as e:
        raise click.ClickException(str(e))


@main.command(name="config")
@click.option('--api-url', default=None, help='Set Plugin Registry API URL (e.g., https://agent-foundry.org/api/v1)')
@click.option('--show', is_flag=True, help='Show current configuration')
def config(api_url, show):
    """Configure Plugin Registry API settings."""
    if show:
        console.print(f"Current API URL: {PLUGIN_REGISTRY_API_URL}", style="cyan")
        console.print("\nTo set configuration, use environment variable:", style="dim")
        console.print("  export PLUGIN_REGISTRY_API_URL='http://your-server:8089/api/v1'", style="dim")
        return
    
    if api_url:
        os.environ['PLUGIN_REGISTRY_API_URL'] = api_url
        console.print(f"✅ API URL set to: {api_url}", style="green")
        console.print("Note: This setting is only for current session. Use environment variable for persistence.", style="yellow")
    
    if not api_url and not show:
        console.print("Use --show to view current configuration, or --api-url to set value.", style="yellow")

if __name__ == "__main__":
    main()
