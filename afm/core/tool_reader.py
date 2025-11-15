"""
Tool Reader - Provides tool descriptions and format conversion for AI

This module provides a simple API that allows AI to directly understand what tools are available,
and can get standardized descriptions of all tools with a single line of code.
"""
import inspect
import json
from typing import Dict, Any, List, Optional, Union
from afm.core.tool_registry import get_registry
import logging

logger = logging.getLogger(__name__)


class ToolReader:
    """Tool Reader - Reads and formats tool descriptions for AI use"""
    
    def __init__(self, registry=None):
        """
        Initialize tool reader
        
        Args:
            registry: Tool registry instance, if None uses global registry
        """
        self.registry = registry or get_registry()
    
    def get_all_tools(self) -> List[str]:
        """Get all registered tool names"""
        return self.registry.list_tools()
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a single tool
        
        Args:
            tool_name: Tool name
            
        Returns:
            Tool information dictionary containing name, description, parameters, etc.
        """
        tool_func = self.registry.get_tool(tool_name)
        if tool_func is None:
            return None
        
        metadata = self.registry.get_tool_metadata(tool_name) or {}
        signature = inspect.signature(tool_func)
        
        # Parse parameters
        parameters = {}
        for param_name, param in signature.parameters.items():
            param_info = {
                "type": self._get_type_name(param.annotation),
                "required": param.default == inspect.Parameter.empty,
            }
            
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
            
            if param.annotation != inspect.Parameter.empty:
                param_info["type"] = self._get_type_name(param.annotation)
            
            parameters[param_name] = param_info
        
        return {
            "name": tool_name,
            "description": metadata.get("description", tool_func.__doc__ or ""),
            "parameters": parameters,
            "signature": str(signature),
            "plugin": metadata.get("plugin"),
            "class": metadata.get("class"),
            "method": metadata.get("method"),
        }
    
    def _get_type_name(self, annotation: Any) -> str:
        """Convert type annotation to string"""
        if annotation == inspect.Parameter.empty:
            return "Any"
        
        if isinstance(annotation, type):
            return annotation.__name__
        
        if hasattr(annotation, "__name__"):
            return annotation.__name__
        
        return str(annotation)
    
    def to_openai_format(self) -> List[Dict[str, Any]]:
        """
        Convert all tools to OpenAI Function Calling format
        
        Returns:
            List of tools in OpenAI function calling format
        """
        tools = []
        for tool_name in self.get_all_tools():
            tool_info = self.get_tool_info(tool_name)
            if tool_info is None:
                continue
            
            # Build OpenAI format parameter schema
            properties = {}
            required = []
            
            for param_name, param_info in tool_info["parameters"].items():
                param_type = param_info.get("type", "string")
                
                # Map Python types to JSON Schema types
                json_type = self._python_to_json_type(param_type)
                
                properties[param_name] = {
                    "type": json_type,
                    "description": f"Parameter {param_name}",
                }
                
                if param_info.get("required", False):
                    required.append(param_name)
                
                if "default" in param_info:
                    properties[param_name]["default"] = param_info["default"]
            
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_info["description"] or f"Tool: {tool_name}",
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    }
                }
            }
            
            tools.append(openai_tool)
        
        return tools
    
    def _python_to_json_type(self, python_type: str) -> str:
        """Map Python types to JSON Schema types"""
        type_mapping = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object",
            "Any": "string",
        }
        
        python_type_lower = python_type.lower()
        for py_type, json_type in type_mapping.items():
            if py_type in python_type_lower:
                return json_type
        
        return "string"  # Default to string
    
    def to_langchain_format(self) -> List[Dict[str, Any]]:
        """
        Convert all tools to LangChain format
        
        Returns:
            List of tools in LangChain format
        """
        tools = []
        for tool_name in self.get_all_tools():
            tool_info = self.get_tool_info(tool_name)
            if tool_info is None:
                continue
            
            langchain_tool = {
                "name": tool_name,
                "description": tool_info["description"] or f"Tool: {tool_name}",
                "parameters": tool_info["parameters"],
                "signature": tool_info["signature"],
            }
            
            if tool_info.get("plugin"):
                langchain_tool["plugin"] = tool_info["plugin"]
            
            tools.append(langchain_tool)
        
        return tools
    
    def to_simple_format(self) -> List[Dict[str, Any]]:
        """
        Convert all tools to simple format (easy to read)
        
        Returns:
            List of tools in simple format
        """
        tools = []
        for tool_name in self.get_all_tools():
            tool_info = self.get_tool_info(tool_name)
            if tool_info is None:
                continue
            
            simple_tool = {
                "name": tool_name,
                "description": tool_info["description"],
                "usage": f"{tool_name}({', '.join(tool_info['parameters'].keys())})",
                "parameters": {
                    name: {
                        "type": info.get("type", "Any"),
                        "required": info.get("required", False),
                    }
                    for name, info in tool_info["parameters"].items()
                }
            }
            
            tools.append(simple_tool)
        
        return tools
    
    def to_dict(self, format_type: str = "simple") -> List[Dict[str, Any]]:
        """
        Get descriptions of all tools (one-line code API)
        
        Args:
            format_type: Format type, options:
                - "openai": OpenAI Function Calling format
                - "langchain": LangChain format
                - "simple": Simple format (default)
        
        Returns:
            List of tool descriptions
        """
        format_map = {
            "openai": self.to_openai_format,
            "langchain": self.to_langchain_format,
            "simple": self.to_simple_format,
        }
        
        formatter = format_map.get(format_type.lower(), self.to_simple_format)
        return formatter()
    
    def to_json(self, format_type: str = "simple", indent: int = 2) -> str:
        """
        Convert tool descriptions to JSON string
        
        Args:
            format_type: Format type
            indent: JSON indentation
        
        Returns:
            JSON string
        """
        tools = self.to_dict(format_type)
        return json.dumps(tools, indent=indent, ensure_ascii=False)
    
    def get_tools_summary(self) -> str:
        """
        Get a brief summary of all tools (text format)
        
        Returns:
            Tool summary text
        """
        tools = self.get_all_tools()
        if not tools:
            return "No tools are currently registered"
        
        summary_lines = [f"Total available tools: {len(tools)}\n"]
        
        for tool_name in tools:
            tool_info = self.get_tool_info(tool_name)
            if tool_info:
                desc = tool_info["description"] or "No description"
                params = ", ".join(tool_info["parameters"].keys())
                summary_lines.append(
                    f"- {tool_name}: {desc}\n"
                    f"  Parameters: ({params})"
                )
        
        return "\n".join(summary_lines)


# Global tool reader instance
_reader: Optional[ToolReader] = None


def get_tools(format_type: str = "simple") -> List[Dict[str, Any]]:
    """
    Get descriptions of all tools with one line of code (main API)
    
    Usage examples:
        # Get simple format
        tools = get_tools()
        
        # Get OpenAI format
        tools = get_tools("openai")
        
        # Get LangChain format
        tools = get_tools("langchain")
    
    Args:
        format_type: Format type ("simple", "openai", "langchain")
    
    Returns:
        List of tool descriptions
    """
    global _reader
    if _reader is None:
        _reader = ToolReader()
    return _reader.to_dict(format_type)


def get_tools_json(format_type: str = "simple") -> str:
    """
    Get JSON descriptions of all tools with one line of code
    
    Usage example:
        tools_json = get_tools_json("openai")
        # Can be directly passed to AI API
    
    Args:
        format_type: Format type
    
    Returns:
        JSON string
    """
    global _reader
    if _reader is None:
        _reader = ToolReader()
    return _reader.to_json(format_type)


def get_tools_summary() -> str:
    """
    Get summary of all tools with one line of code
    
    Returns:
        Tool summary text
    """
    global _reader
    if _reader is None:
        _reader = ToolReader()
    return _reader.get_tools_summary()


# Export main functionality
__all__ = [
    "ToolReader",
    "get_tools",
    "get_tools_json",
    "get_tools_summary",
]

