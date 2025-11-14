# 工具讀取器使用指南

## 📋 概述

工具讀取器 (`tool_reader`) 提供了一個簡單的API，讓AI可以直接了解有哪些工具可以使用，並能**一行程式碼**就獲取所有工具的標準化描述。

## 🚀 快速開始

### 一行程式碼獲取所有工具

```python
from afm.core.tools import get_tools

# 獲取所有工具的簡單格式描述
tools = get_tools()
print(tools)
```

### 獲取OpenAI Function Calling格式

```python
from afm.core.tools import get_tools

# 獲取OpenAI格式，可直接用於OpenAI API
openai_tools = get_tools("openai")

# 使用範例：傳給OpenAI API
# client.chat.completions.create(
#     model="gpt-4",
#     messages=[...],
#     tools=openai_tools
# )
```

### 獲取JSON格式

```python
from afm.core.tools import get_tools_json

# 獲取JSON字串
tools_json = get_tools_json("openai")
print(tools_json)
```

### 獲取工具摘要

```python
from afm.core.tools import get_tools_summary

# 獲取文字摘要
summary = get_tools_summary()
print(summary)
```

## 📦 支援的格式

### 1. Simple格式（默認）

簡單易讀的格式，適合快速查看：

```python
tools = get_tools("simple")
# 輸出:
# [
#   {
#     "name": "ocr_demo_extract_text",
#     "description": "Extract text from image",
#     "usage": "ocr_demo_extract_text(image_path, language, ...)",
#     "parameters": {
#       "image_path": {"type": "str", "required": True},
#       "language": {"type": "str", "required": False}
#     }
#   }
# ]
```

### 2. OpenAI Function Calling格式

符合OpenAI API規範的格式：

```python
tools = get_tools("openai")
# 輸出:
# [
#   {
#     "type": "function",
#     "function": {
#       "name": "ocr_demo_extract_text",
#       "description": "Extract text from image",
#       "parameters": {
#         "type": "object",
#         "properties": {
#           "image_path": {
#             "type": "string",
#             "description": "參數 image_path"
#           }
#         },
#         "required": ["image_path"]
#       }
#     }
#   }
# ]
```

### 3. LangChain格式

適合LangChain框架使用的格式：

```python
tools = get_tools("langchain")
# 輸出:
# [
#   {
#     "name": "ocr_demo_extract_text",
#     "description": "Extract text from image",
#     "parameters": {...},
#     "signature": "(image_path: str, ...)",
#     "plugin": "ocr_demo"
#   }
# ]
```

## 💡 完整使用範例

### 範例1: 整合到OpenAI API

```python
from openai import OpenAI
from afm.core.tools import get_tools

client = OpenAI()

# 獲取所有工具
tools = get_tools("openai")

# 使用工具
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "幫我識別這張圖片中的文字: test.png"}
    ],
    tools=tools,
    tool_choice="auto"
)

# 處理工具調用
for tool_call in response.choices[0].message.tool_calls:
    tool_name = tool_call.function.name
    # 調用對應的工具
    from afm.core.tools import registry
    result = registry.call_tool(tool_name, **eval(tool_call.function.arguments))
```

### 範例2: 動態工具選擇

```python
from afm.core.tools import get_tools, registry

# 獲取所有工具描述
tools = get_tools("simple")

# 讓用戶選擇工具
print("可用工具:")
for i, tool in enumerate(tools, 1):
    print(f"{i}. {tool['name']}: {tool['description']}")

# 根據用戶選擇調用工具
choice = int(input("選擇工具編號: ")) - 1
selected_tool = tools[choice]

# 調用工具
result = registry.call_tool(selected_tool["name"], image_path="test.png")
print(result)
```

### 範例3: 工具文檔生成

```python
from afm.core.tools import get_tools_summary, get_tools_json

# 生成工具文檔
summary = get_tools_summary()
print("=== 工具摘要 ===")
print(summary)

# 生成JSON文檔
tools_json = get_tools_json("simple", indent=2)
with open("tools_documentation.json", "w", encoding="utf-8") as f:
    f.write(tools_json)
```

### 範例4: 高級使用 - 自定義讀取器

```python
from afm.core.tool_reader import ToolReader
from afm.core.tool_registry import get_registry

# 創建自定義讀取器
registry = get_registry()
reader = ToolReader(registry)

# 獲取特定工具信息
tool_info = reader.get_tool_info("ocr_demo_extract_text")
print(f"工具名稱: {tool_info['name']}")
print(f"描述: {tool_info['description']}")
print(f"參數: {tool_info['parameters']}")

# 獲取所有工具名稱
all_tool_names = reader.get_all_tools()
print(f"所有工具: {all_tool_names}")
```

## 🎯 與AI框架整合

### OpenAI

```python
from openai import OpenAI
from afm.core.tools import get_tools

client = OpenAI()
tools = get_tools("openai")

# 直接使用
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "..."}],
    tools=tools
)
```

### LangChain

```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from afm.core.tools import get_tools, registry

# 獲取工具描述
tools_desc = get_tools("langchain")

# 創建LangChain工具包裝器
from langchain.tools import Tool

langchain_tools = []
for tool_desc in tools_desc:
    tool = Tool(
        name=tool_desc["name"],
        description=tool_desc["description"],
        func=lambda name=tool_desc["name"]: registry.call_tool(name, **kwargs)
    )
    langchain_tools.append(tool)

# 使用工具
llm = ChatOpenAI(model="gpt-4")
agent = create_openai_tools_agent(llm, langchain_tools, ...)
```

### Anthropic Claude

```python
import anthropic
from afm.core.tools import get_tools

client = anthropic.Anthropic()

# 轉換為Claude格式
tools = get_tools("openai")
claude_tools = [tool["function"] for tool in tools]

response = client.messages.create(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": "..."}],
    tools=claude_tools
)
```

## 📊 輸出格式對比

| 格式 | 用途 | 特點 |
|------|------|------|
| `simple` | 快速查看、文檔 | 易讀、包含使用範例 |
| `openai` | OpenAI API | 符合OpenAI規範、可直接使用 |
| `langchain` | LangChain框架 | 包含完整元數據、簽名信息 |

## 🔧 進階功能

### 過濾工具

```python
from afm.core.tools import get_tools

# 獲取所有工具
all_tools = get_tools("simple")

# 過濾OCR相關工具
ocr_tools = [t for t in all_tools if "ocr" in t["name"].lower()]

# 過濾特定插件的工具
plugin_tools = [t for t in all_tools if t.get("plugin") == "ocr_demo"]
```

### 工具統計

```python
from afm.core.tools import get_tools

tools = get_tools("simple")

# 統計信息
total_tools = len(tools)
plugins = set(t.get("plugin") for t in tools if t.get("plugin"))
required_params = sum(
    sum(1 for p in t["parameters"].values() if p.get("required", False))
    for t in tools
)

print(f"總工具數: {total_tools}")
print(f"插件數: {len(plugins)}")
print(f"必需參數總數: {required_params}")
```

## 🐛 故障排除

### 沒有工具可用

```python
from afm.core.tools import get_tools, registry

# 檢查工具是否已註冊
if len(registry.list_tools()) == 0:
    print("沒有已註冊的工具，請確保插件已正確安裝")
else:
    tools = get_tools()
    print(f"找到 {len(tools)} 個工具")
```

### 工具格式錯誤

```python
from afm.core.tools import get_tools_json

try:
    tools_json = get_tools_json("openai")
    # 驗證JSON格式
    import json
    json.loads(tools_json)
    print("JSON格式正確")
except Exception as e:
    print(f"錯誤: {e}")
```

## 💡 最佳實踐

1. **使用適當的格式**: 根據你的AI框架選擇對應格式
2. **緩存工具描述**: 工具描述不會頻繁變化，可以緩存
3. **錯誤處理**: 始終檢查工具是否存在再調用
4. **文檔化**: 使用 `get_tools_summary()` 生成工具文檔

## 📚 相關文檔

- [工具註冊系統使用指南](./USAGE_TOOL_REGISTRY.md)
- [插件開發指南](./PLUGIN_GUIDE.md) (如果存在)

