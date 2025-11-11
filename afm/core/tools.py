"""
工具模組 - 自動導入所有註冊的工具，提供類似 LangChain 的使用體驗
"""
from afm.core.tool_registry import get_registry, tool
from afm.config.settings import PLUGIN_DIR
import logging
import os

logger = logging.getLogger(__name__)

# 創建全局註冊器
registry = get_registry()

# 自動掃描和註冊插件
_initialized = False

def _auto_register_plugins():
    """自動掃描並註冊所有插件"""
    global _initialized
    if _initialized:
        return
    
    plugin_dir = PLUGIN_DIR
    if os.path.exists(plugin_dir):
        registry.scan_and_register_plugins(plugin_dir)
        logger.info(f"已自動註冊 {len(registry.list_tools())} 個工具")
    else:
        logger.warning(f"插件目錄不存在: {plugin_dir}")
    
    _initialized = True

# 自動初始化
_auto_register_plugins()

# 動態創建模組級別的工具函數
def __getattr__(name: str):
    """
    魔法方法：允許直接通過模組訪問工具
    
    例如:
    from afm.core.tools import ocr_demo_extract_text
    result = ocr_demo_extract_text(image_path="test.png")
    """
    tool_func = registry.get_tool(name)
    if tool_func is not None:
        return tool_func
    raise AttributeError(f"模組 '{__name__}' 沒有工具 '{name}'")

# 導出常用功能
__all__ = [
    'registry',
    'tool',
    'get_registry',
]

