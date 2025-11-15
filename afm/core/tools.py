"""
Tools module - Automatically imports all registered tools, providing a LangChain-like experience
"""
from afm.core.tool_registry import get_registry, tool
from afm.core.tool_reader import (
    ToolReader,
    get_tools,
    get_tools_json,
    get_tools_summary,
)
from afm.config.settings import PLUGIN_DIR
import logging
import os

logger = logging.getLogger(__name__)

# Create global registry
registry = get_registry()

# Auto-scan and register plugins
_initialized = False

def _auto_register_plugins():
    """Automatically scan and register all plugins"""
    global _initialized
    if _initialized:
        return
    
    plugin_dir = PLUGIN_DIR
    if os.path.exists(plugin_dir):
        registry.scan_and_register_plugins(plugin_dir)
        logger.info(f"Automatically registered {len(registry.list_tools())} tools")
    else:
        logger.warning(f"Plugin directory does not exist: {plugin_dir}")
    
    _initialized = True

# Auto-initialize
_auto_register_plugins()

# Dynamically create module-level tool functions
def __getattr__(name: str):
    """
    Magic method: Allows direct access to tools through the module
    
    Example:
    from afm.core.tools import ocr_demo_extract_text
    result = ocr_demo_extract_text(image_path="test.png")
    """
    tool_func = registry.get_tool(name)
    if tool_func is not None:
        return tool_func
    raise AttributeError(f"Module '{__name__}' has no tool '{name}'")

# Export common functionality
__all__ = [
    'registry',
    'tool',
    'get_registry',
    # Tool reader functionality
    'ToolReader',
    'get_tools',
    'get_tools_json',
    'get_tools_summary',
]

