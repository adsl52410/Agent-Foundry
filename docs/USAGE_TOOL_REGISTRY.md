# 工具自動註冊系統使用指南

## 📋 概述

Agent Foundry 現在支援類似 LangChain 的工具自動註冊機制。插件會自動被掃描和註冊，變成可直接調用的方法。

## 🚀 使用方式

### 方式 1: 直接導入工具（推薦，類似 LangChain）

```python
# 自動導入已註冊的工具
from afm.core.tools import ocr_demo_extract_text

# 直接使用，就像普通函數
result = ocr_demo_extract_text(
    image_path="test.png",
    language="chi_tra+eng",
    enable_fallback=True
)

print(result)
```

### 方式 2: 通過註冊器訪問

```python
from afm.core.tools import registry

# 列出所有工具
tools = registry.list_tools()
print(f"可用工具: {tools}")

# 獲取工具
ocr_tool = registry.get_tool("ocr_demo_extract_text")

# 調用工具
result = ocr_tool(image_path="test.png")
```

### 方式 3: 通過註冊器屬性訪問

```python
from afm.core.tools import registry

# 直接通過屬性訪問（魔法方法）
result = registry.ocr_demo_extract_text(image_path="test.png")
```

### 方式 4: 動態調用

```python
from afm.core.tools import registry

# 動態調用工具
tool_name = "ocr_demo_extract_text"
result = registry.call_tool(tool_name, image_path="test.png")
```

## 📦 插件自動註冊

### 自動掃描

系統會自動掃描 `afm/plugins/` 目錄下的所有插件，並將符合條件的類別方法註冊為工具。

### 支援的插件結構

#### 1. 服務類別（自動註冊 extract_text 方法）

```python
# afm/plugins/ocr_demo/plugin.py
class OCRService:
    def initialize(self):
        # 初始化邏輯
        pass
    
    def extract_text(self, image_path: str, **kwargs):
        # OCR 邏輯
        return {"success": True, "data": {...}}
```

**自動註冊為**: `ocr_demo_extract_text`

#### 2. 使用 @tool 裝飾器

```python
from afm.core.tool_registry import tool

@tool(name="my_custom_tool", description="我的自定義工具")
def my_function(arg1: str, arg2: int = 10) -> str:
    """工具描述"""
    return f"處理結果: {arg1} {arg2}"
```

**註冊為**: `my_custom_tool`

## 🔍 查詢工具

### 列出所有工具

```python
from afm.core.tools import registry

# 列出所有工具名稱
tools = registry.list_tools()
for tool_name in tools:
    print(f"- {tool_name}")
```

### 獲取工具元數據

```python
from afm.core.tools import registry

# 獲取工具信息
metadata = registry.get_tool_metadata("ocr_demo_extract_text")
print(f"描述: {metadata['description']}")
print(f"簽名: {metadata['signature']}")
print(f"插件: {metadata.get('plugin')}")
```

## 📝 完整使用範例

### 範例 1: 基本使用

```python
from afm.core.tools import ocr_demo_extract_text

# 簡單使用
result = ocr_demo_extract_text(image_path="test.png")

if result["success"]:
    print(f"識別文字: {result['data']['text']}")
    print(f"置信度: {result['data']['confidence']:.2%}")
```

### 範例 2: 批次處理

```python
from afm.core.tools import ocr_demo_extract_text
from pathlib import Path

# 批次處理多張圖片
image_dir = Path("./images")
for image_file in image_dir.glob("*.png"):
    result = ocr_demo_extract_text(
        image_path=str(image_file),
        language="chi_tra+eng",
        enable_fallback=True
    )
    print(f"{image_file.name}: {result['success']}")
```

### 範例 3: 動態工具選擇

```python
from afm.core.tools import registry

# 列出所有 OCR 相關工具
ocr_tools = [name for name in registry.list_tools() if 'ocr' in name.lower()]

# 使用第一個 OCR 工具
if ocr_tools:
    tool_name = ocr_tools[0]
    result = registry.call_tool(tool_name, image_path="test.png")
    print(result)
```

### 範例 4: 整合到現有程式

```python
from afm.core.tools import registry

class MyApp:
    def __init__(self):
        # 初始化時檢查工具是否可用
        self.ocr_tool = registry.get_tool("ocr_demo_extract_text")
        if self.ocr_tool is None:
            raise RuntimeError("OCR 工具未找到")
    
    def process_images(self, image_paths: list):
        """處理多張圖片"""
        results = []
        for path in image_paths:
            result = self.ocr_tool(image_path=path)
            results.append(result)
        return results

# 使用
app = MyApp()
results = app.process_images(["img1.png", "img2.png"])
```

## 🎯 工具命名規則

- **服務類別的 extract_text 方法**: `{plugin_name}_extract_text`
  - 例如: `ocr_demo_extract_text`
  
- **使用 @tool 裝飾器的函數**: 使用裝飾器指定的名稱，或函數名
  - 例如: `@tool(name="my_tool")` -> `my_tool`

## ⚙️ 自定義工具

### 創建自定義工具

```python
# 在你的插件或模組中
from afm.core.tool_registry import tool, get_registry

@tool(name="calculate_sum", description="計算兩個數字的和")
def add_numbers(a: int, b: int) -> int:
    """計算兩個數字的和"""
    return a + b

# 或者手動註冊
registry = get_registry()
registry.register_tool(
    name="multiply",
    func=lambda x, y: x * y,
    description="計算兩個數字的乘積"
)
```

### 在插件中使用

```python
# afm/plugins/my_plugin/plugin.py
from afm.core.tool_registry import tool

class MyService:
    @tool(name="my_service_process")
    def process(self, data: str) -> str:
        """處理數據"""
        return f"處理: {data}"
```

## 🔧 高級用法

### 禁用自動掃描

```python
from afm.core.tool_registry import ToolRegistry

# 創建新的註冊器（不自動掃描）
custom_registry = ToolRegistry()

# 手動註冊工具
custom_registry.register_tool("my_tool", my_function)
```

### 批量註冊

```python
from afm.core.tool_registry import get_registry

registry = get_registry()

# 批量註冊多個工具
tools = {
    "tool1": func1,
    "tool2": func2,
    "tool3": func3,
}

for name, func in tools.items():
    registry.register_tool(name, func)
```

## 📚 與 LangChain 的對比

| 特性 | LangChain | Agent Foundry |
|------|-----------|---------------|
| 工具定義 | 使用 @tool 裝飾器 | 自動掃描或 @tool 裝飾器 |
| 導入方式 | `from langchain.tools import tool_name` | `from afm.core.tools import tool_name` |
| 自動掃描 | 需要手動註冊 | 自動掃描插件目錄 |
| 服務類別 | 需要手動包裝 | 自動識別和註冊 |

## 🐛 故障排除

### 工具未找到

```python
# 檢查工具是否存在
from afm.core.tools import registry

if "ocr_demo_extract_text" in registry.list_tools():
    print("工具已註冊")
else:
    print("工具未註冊，檢查插件目錄")
```

### 插件未被自動掃描

1. 確保插件目錄結構正確: `afm/plugins/{plugin_name}/plugin.py`
2. 確保插件包含可識別的類別或函數
3. 檢查日誌中的錯誤訊息

### 工具調用失敗

```python
try:
    result = ocr_demo_extract_text(image_path="test.png")
except Exception as e:
    print(f"工具調用失敗: {e}")
    # 檢查工具元數據
    metadata = registry.get_tool_metadata("ocr_demo_extract_text")
    print(f"工具簽名: {metadata['signature']}")
```

## 💡 最佳實踐

1. **使用明確的工具名稱**: 確保工具名稱清晰且唯一
2. **提供完整的文檔字符串**: 工具描述會自動從 `__doc__` 提取
3. **處理錯誤**: 工具應該返回標準化的結果格式
4. **重用服務實例**: 服務類別會自動使用單例模式，提高性能
5. **類型提示**: 使用類型提示讓工具簽名更清晰

