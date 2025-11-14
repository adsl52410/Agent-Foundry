"""
工具讀取器 - 為AI提供工具描述和格式轉換

這個模組提供了一個簡單的API，讓AI可以直接了解有哪些工具可以使用，
並能一行程式碼就獲取所有工具的標準化描述。
"""
import inspect
import json
from typing import Dict, Any, List, Optional, Union
from afm.core.tool_registry import get_registry
import logging

logger = logging.getLogger(__name__)


class ToolReader:
    """工具讀取器 - 讀取和格式化工具描述供AI使用"""
    
    def __init__(self, registry=None):
        """
        初始化工具讀取器
        
        Args:
            registry: 工具註冊器實例，如果為None則使用全局註冊器
        """
        self.registry = registry or get_registry()
    
    def get_all_tools(self) -> List[str]:
        """獲取所有已註冊的工具名稱"""
        return self.registry.list_tools()
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        獲取單個工具的詳細信息
        
        Args:
            tool_name: 工具名稱
            
        Returns:
            工具信息字典，包含名稱、描述、參數等
        """
        tool_func = self.registry.get_tool(tool_name)
        if tool_func is None:
            return None
        
        metadata = self.registry.get_tool_metadata(tool_name) or {}
        signature = inspect.signature(tool_func)
        
        # 解析參數
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
        """將類型註解轉換為字串"""
        if annotation == inspect.Parameter.empty:
            return "Any"
        
        if isinstance(annotation, type):
            return annotation.__name__
        
        if hasattr(annotation, "__name__"):
            return annotation.__name__
        
        return str(annotation)
    
    def to_openai_format(self) -> List[Dict[str, Any]]:
        """
        將所有工具轉換為OpenAI Function Calling格式
        
        Returns:
            OpenAI function calling格式的工具列表
        """
        tools = []
        for tool_name in self.get_all_tools():
            tool_info = self.get_tool_info(tool_name)
            if tool_info is None:
                continue
            
            # 構建OpenAI格式的參數schema
            properties = {}
            required = []
            
            for param_name, param_info in tool_info["parameters"].items():
                param_type = param_info.get("type", "string")
                
                # 將Python類型映射到JSON Schema類型
                json_type = self._python_to_json_type(param_type)
                
                properties[param_name] = {
                    "type": json_type,
                    "description": f"參數 {param_name}",
                }
                
                if param_info.get("required", False):
                    required.append(param_name)
                
                if "default" in param_info:
                    properties[param_name]["default"] = param_info["default"]
            
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_info["description"] or f"工具: {tool_name}",
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
        """將Python類型映射到JSON Schema類型"""
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
        
        return "string"  # 默認返回string
    
    def to_langchain_format(self) -> List[Dict[str, Any]]:
        """
        將所有工具轉換為LangChain格式
        
        Returns:
            LangChain格式的工具列表
        """
        tools = []
        for tool_name in self.get_all_tools():
            tool_info = self.get_tool_info(tool_name)
            if tool_info is None:
                continue
            
            langchain_tool = {
                "name": tool_name,
                "description": tool_info["description"] or f"工具: {tool_name}",
                "parameters": tool_info["parameters"],
                "signature": tool_info["signature"],
            }
            
            if tool_info.get("plugin"):
                langchain_tool["plugin"] = tool_info["plugin"]
            
            tools.append(langchain_tool)
        
        return tools
    
    def to_simple_format(self) -> List[Dict[str, Any]]:
        """
        將所有工具轉換為簡單格式（易於閱讀）
        
        Returns:
            簡單格式的工具列表
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
        獲取所有工具的描述（一行程式碼API）
        
        Args:
            format_type: 格式類型，可選值：
                - "openai": OpenAI Function Calling格式
                - "langchain": LangChain格式
                - "simple": 簡單格式（默認）
        
        Returns:
            工具描述列表
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
        將工具描述轉換為JSON字串
        
        Args:
            format_type: 格式類型
            indent: JSON縮排
        
        Returns:
            JSON字串
        """
        tools = self.to_dict(format_type)
        return json.dumps(tools, indent=indent, ensure_ascii=False)
    
    def get_tools_summary(self) -> str:
        """
        獲取所有工具的簡要摘要（文字格式）
        
        Returns:
            工具摘要文字
        """
        tools = self.get_all_tools()
        if not tools:
            return "目前沒有已註冊的工具"
        
        summary_lines = [f"可用工具總數: {len(tools)}\n"]
        
        for tool_name in tools:
            tool_info = self.get_tool_info(tool_name)
            if tool_info:
                desc = tool_info["description"] or "無描述"
                params = ", ".join(tool_info["parameters"].keys())
                summary_lines.append(
                    f"- {tool_name}: {desc}\n"
                    f"  參數: ({params})"
                )
        
        return "\n".join(summary_lines)


# 全局工具讀取器實例
_reader: Optional[ToolReader] = None


def get_tools(format_type: str = "simple") -> List[Dict[str, Any]]:
    """
    一行程式碼獲取所有工具的描述（主要API）
    
    使用範例:
        # 獲取簡單格式
        tools = get_tools()
        
        # 獲取OpenAI格式
        tools = get_tools("openai")
        
        # 獲取LangChain格式
        tools = get_tools("langchain")
    
    Args:
        format_type: 格式類型 ("simple", "openai", "langchain")
    
    Returns:
        工具描述列表
    """
    global _reader
    if _reader is None:
        _reader = ToolReader()
    return _reader.to_dict(format_type)


def get_tools_json(format_type: str = "simple") -> str:
    """
    一行程式碼獲取所有工具的JSON描述
    
    使用範例:
        tools_json = get_tools_json("openai")
        # 可以直接傳給AI API
    
    Args:
        format_type: 格式類型
    
    Returns:
        JSON字串
    """
    global _reader
    if _reader is None:
        _reader = ToolReader()
    return _reader.to_json(format_type)


def get_tools_summary() -> str:
    """
    一行程式碼獲取所有工具的摘要
    
    Returns:
        工具摘要文字
    """
    global _reader
    if _reader is None:
        _reader = ToolReader()
    return _reader.get_tools_summary()


# 導出主要功能
__all__ = [
    "ToolReader",
    "get_tools",
    "get_tools_json",
    "get_tools_summary",
]

