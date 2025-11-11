"""
工具註冊器 - 類似 LangChain 的自動工具掃描和註冊機制
"""
import importlib.util
import os
import inspect
from typing import Dict, Any, Callable, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """工具註冊器 - 自動掃描和註冊插件為可調用的方法"""
    
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
        註冊工具
        
        Args:
            name: 工具名稱（如 'ocr_extract_text'）
            func: 可調用函數
            description: 工具描述
            metadata: 額外的元數據
        """
        self._tools[name] = func
        self._tool_metadata[name] = {
            "description": description or func.__doc__ or "",
            "name": name,
            "signature": str(inspect.signature(func)),
            **(metadata or {})
        }
        logger.debug(f"已註冊工具: {name}")
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """獲取工具函數"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """列出所有已註冊的工具名稱"""
        return list(self._tools.keys())
    
    def get_tool_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """獲取工具的元數據"""
        return self._tool_metadata.get(name)
    
    def scan_and_register_plugins(self, plugin_dir: str):
        """
        掃描插件目錄並自動註冊為工具
        
        Args:
            plugin_dir: 插件目錄路徑
        """
        plugin_path = Path(plugin_dir)
        if not plugin_path.exists():
            logger.warning(f"插件目錄不存在: {plugin_dir}")
            return
        
        # 掃描所有插件目錄
        for plugin_folder in plugin_path.iterdir():
            if not plugin_folder.is_dir() or plugin_folder.name.startswith('_'):
                continue
            
            plugin_file = plugin_folder / "plugin.py"
            if not plugin_file.exists():
                continue
            
            try:
                self._register_plugin(plugin_folder.name, str(plugin_file))
            except Exception as e:
                logger.warning(f"註冊插件 {plugin_folder.name} 失敗: {e}")
    
    def _register_plugin(self, plugin_name: str, plugin_path: str):
        """
        註冊單個插件
        
        Args:
            plugin_name: 插件名稱（如 'ocr_demo'）
            plugin_path: plugin.py 文件路徑
        """
        # 動態載入模組
        spec = importlib.util.spec_from_file_location(f"plugin_{plugin_name}", plugin_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"無法載入插件: {plugin_path}")
        
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        # 尋找可註冊的類別或函數
        for attr_name in dir(mod):
            if attr_name.startswith('_'):
                continue
            
            attr = getattr(mod, attr_name)
            
            # 如果是類別，檢查是否有標準方法
            if inspect.isclass(attr):
                self._register_class_as_tools(plugin_name, attr_name, attr)
            
            # 如果是函數，檢查是否有 @tool 裝飾器或符合標準簽名
            elif inspect.isfunction(attr):
                if hasattr(attr, '_is_tool') or self._is_tool_function(attr):
                    tool_name = f"{plugin_name}_{attr_name}" if not hasattr(attr, '_tool_name') else attr._tool_name
                    description = getattr(attr, '_tool_description', attr.__doc__ or "")
                    self.register_tool(tool_name, attr, description)
    
    def _register_class_as_tools(self, plugin_name: str, class_name: str, cls: type):
        """
        將類別的方法註冊為工具
        
        支持的類別模式：
        1. OCRService 類別 -> extract_text 方法變成 ocr_demo_extract_text
        2. 有 @tool 裝飾器的方法
        """
        # 檢查是否是服務類別（如 OCRService）
        if hasattr(cls, 'extract_text') or hasattr(cls, 'initialize'):
            # 這是一個服務類別，創建單例並包裝方法
            # 使用 lazy initialization（延遲初始化）
            _instance = [None]  # 使用列表以便在閉包中修改
            
            # 創建初始化函數
            def get_instance():
                if _instance[0] is None:
                    try:
                        _instance[0] = cls()
                        if hasattr(_instance[0], 'initialize'):
                            _instance[0].initialize()
                    except Exception as e:
                        logger.warning(f"初始化 {class_name} 失敗: {e}")
                        # 如果初始化失敗，每次調用時創建新實例
                        _instance[0] = None
                return _instance[0]
            
            # 註冊 extract_text 方法
            if hasattr(cls, 'extract_text'):
                method = getattr(cls, 'extract_text')
                
                def tool_wrapper(*args, **kwargs):
                    """工具包裝函數"""
                    inst = get_instance()
                    if inst is None:
                        # 如果單例初始化失敗，每次創建新實例
                        inst = cls()
                        if hasattr(inst, 'initialize'):
                            try:
                                inst.initialize()
                            except:
                                pass
                    return method(inst, *args, **kwargs)
                
                # 保持原始函數的元數據
                tool_wrapper.__name__ = method.__name__
                tool_wrapper.__doc__ = method.__doc__
                
                tool_name = f"{plugin_name}_extract_text"
                
                # 獲取描述
                description = method.__doc__ or f"Extract text from image using {plugin_name}"
                
                self.register_tool(tool_name, tool_wrapper, description, {
                    "class": class_name,
                    "plugin": plugin_name,
                    "method": "extract_text"
                })
        
        # 掃描類別中標記為工具的方法
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
        檢查函數是否是工具函數
        
        標準：
        1. 有 @tool 裝飾器
        2. 函數名符合命名規範
        3. 有適當的文檔字符串
        """
        # 檢查裝飾器標記
        if hasattr(func, '_is_tool'):
            return True
        
        # 可以添加更多檢查邏輯
        return False
    
    def call_tool(self, name: str, *args, **kwargs) -> Any:
        """
        調用工具
        
        Args:
            name: 工具名稱
            *args, **kwargs: 傳遞給工具的參數
        
        Returns:
            工具執行結果
        """
        tool = self.get_tool(name)
        if tool is None:
            raise ValueError(f"工具未找到: {name}")
        
        return tool(*args, **kwargs)
    
    def __getattr__(self, name: str):
        """
        魔法方法：允許直接通過屬性訪問工具
        
        例如: registry.ocr_demo_extract_text(image_path="test.png")
        """
        tool = self.get_tool(name)
        if tool is not None:
            return tool
        raise AttributeError(f"'{self.__class__.__name__}' 沒有工具 '{name}'")


# 全局工具註冊器實例
_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """獲取全局工具註冊器"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def tool(name: Optional[str] = None, description: Optional[str] = None):
    """
    工具裝飾器 - 標記函數為工具
    
    使用範例:
    @tool(name="my_tool", description="我的工具")
    def my_function(arg1: str) -> str:
        return f"處理: {arg1}"
    """
    def decorator(func: Callable):
        func._is_tool = True
        func._tool_name = name or func.__name__
        func._tool_description = description or func.__doc__ or ""
        return func
    return decorator

