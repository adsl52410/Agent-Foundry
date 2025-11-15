"""
Tool Registry - Automatic tool scanning and registration mechanism similar to LangChain
"""
import importlib.util
import os
import inspect
from typing import Dict, Any, Callable, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Tool Registry - Automatically scans and registers plugins as callable methods"""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._tool_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(
        self,
        name: str,
        func: Callable,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register a tool
        
        Args:
            name: Tool name (e.g., 'ocr_extract_text')
            func: Callable function
            description: Tool description
            metadata: Additional metadata
        """
        self._tools[name] = func
        self._tool_metadata[name] = {
            "description": description or func.__doc__ or "",
            "name": name,
            "signature": str(inspect.signature(func)),
            **(metadata or {})
        }
        logger.debug(f"Registered tool: {name}")
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get tool function"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())
    
    def get_tool_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool metadata"""
        return self._tool_metadata.get(name)
    
    def scan_and_register_plugins(self, plugin_dir: str):
        """
        Scan plugin directory and automatically register as tools
        
        Args:
            plugin_dir: Plugin directory path
        """
        plugin_path = Path(plugin_dir)
        if not plugin_path.exists():
            logger.warning(f"Plugin directory does not exist: {plugin_dir}")
            return
        
        # Scan all plugin directories
        for plugin_folder in plugin_path.iterdir():
            if not plugin_folder.is_dir() or plugin_folder.name.startswith('_'):
                continue
            
            plugin_file = plugin_folder / "plugin.py"
            if not plugin_file.exists():
                continue
            
            try:
                self._register_plugin(plugin_folder.name, str(plugin_file))
            except Exception as e:
                logger.warning(f"Failed to register plugin {plugin_folder.name}: {e}")
    
    def _register_plugin(self, plugin_name: str, plugin_path: str):
        """
        Register a single plugin
        
        Args:
            plugin_name: Plugin name (e.g., 'ocr_demo')
            plugin_path: plugin.py file path
        """
        # Dynamically load module
        spec = importlib.util.spec_from_file_location(f"plugin_{plugin_name}", plugin_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load plugin: {plugin_path}")
        
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        # Find registerable classes or functions
        for attr_name in dir(mod):
            if attr_name.startswith('_'):
                continue
            
            attr = getattr(mod, attr_name)
            
            # If it's a class, check if it has standard methods
            if inspect.isclass(attr):
                self._register_class_as_tools(plugin_name, attr_name, attr)
            
            # If it's a function, check if it has @tool decorator or matches standard signature
            elif inspect.isfunction(attr):
                if hasattr(attr, '_is_tool') or self._is_tool_function(attr):
                    tool_name = f"{plugin_name}_{attr_name}" if not hasattr(attr, '_tool_name') else attr._tool_name
                    description = getattr(attr, '_tool_description', attr.__doc__ or "")
                    self.register_tool(tool_name, attr, description)
    
    def _register_class_as_tools(self, plugin_name: str, class_name: str, cls: type):
        """
        Register class methods as tools
        
        Supported class patterns:
        1. OCRService class -> extract_text method becomes ocr_demo_extract_text
        2. Methods with @tool decorator
        """
        # Check if it's a service class (e.g., OCRService)
        if hasattr(cls, 'extract_text') or hasattr(cls, 'initialize'):
            # This is a service class, create singleton and wrap methods
            # Use lazy initialization
            _instance = [None]  # Use list to allow modification in closure
            
            # Create initialization function
            def get_instance():
                if _instance[0] is None:
                    try:
                        _instance[0] = cls()
                        if hasattr(_instance[0], 'initialize'):
                            _instance[0].initialize()
                    except Exception as e:
                        logger.warning(f"Failed to initialize {class_name}: {e}")
                        # If initialization fails, create new instance on each call
                        _instance[0] = None
                return _instance[0]
            
            # Register extract_text method
            if hasattr(cls, 'extract_text'):
                method = getattr(cls, 'extract_text')
                
                def tool_wrapper(*args, **kwargs):
                    """Tool wrapper function"""
                    inst = get_instance()
                    if inst is None:
                        # If singleton initialization failed, create new instance each time
                        inst = cls()
                        if hasattr(inst, 'initialize'):
                            try:
                                inst.initialize()
                            except:
                                pass
                    return method(inst, *args, **kwargs)
                
                # Preserve original function metadata
                tool_wrapper.__name__ = method.__name__
                tool_wrapper.__doc__ = method.__doc__
                
                tool_name = f"{plugin_name}_extract_text"
                
                # Get description
                description = method.__doc__ or f"Extract text from image using {plugin_name}"
                
                self.register_tool(tool_name, tool_wrapper, description, {
                    "class": class_name,
                    "plugin": plugin_name,
                    "method": "extract_text"
                })
        
        # Scan methods marked as tools in the class
        for method_name in dir(cls):
            if method_name.startswith('_'):
                continue
            
            method = getattr(cls, method_name)
            if inspect.ismethod(method) or inspect.isfunction(method):
                if hasattr(method, '_is_tool'):
                    tool_name = getattr(method, '_tool_name', f"{plugin_name}_{method_name}")
                    description = getattr(method, '_tool_description', method.__doc__ or "")
                    self.register_tool(tool_name, method, description)
    
    def _is_tool_function(self, func: Callable) -> bool:
        """
        Check if a function is a tool function
        
        Criteria:
        1. Has @tool decorator
        2. Function name matches naming convention
        3. Has appropriate docstring
        """
        # Check decorator marker
        if hasattr(func, '_is_tool'):
            return True
        
        # Can add more checking logic
        return False
    
    def call_tool(self, name: str, *args, **kwargs) -> Any:
        """
        Call a tool
        
        Args:
            name: Tool name
            *args, **kwargs: Parameters to pass to the tool
        
        Returns:
            Tool execution result
        """
        tool = self.get_tool(name)
        if tool is None:
            raise ValueError(f"Tool not found: {name}")
        
        return tool(*args, **kwargs)
    
    def __getattr__(self, name: str):
        """
        Magic method: Allows direct access to tools through attributes
        
        Example: registry.ocr_demo_extract_text(image_path="test.png")
        """
        tool = self.get_tool(name)
        if tool is not None:
            return tool
        raise AttributeError(f"'{self.__class__.__name__}' has no tool '{name}'")


# Global tool registry instance
_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get global tool registry"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def tool(name: Optional[str] = None, description: Optional[str] = None):
    """
    Tool decorator - Mark function as a tool
    
    Usage example:
    @tool(name="my_tool", description="My tool")
    def my_function(arg1: str) -> str:
        return f"Process: {arg1}"
    """
    def decorator(func: Callable):
        func._is_tool = True
        func._tool_name = name or func.__name__
        func._tool_description = description or func.__doc__ or ""
        return func
    return decorator

