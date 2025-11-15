# Tool Reader Usage Guide

## 📋 Overview

The tool reader (`tool_reader`) provides a simple API that allows AI to directly understand what tools are available and get standardized descriptions of all tools with **just one line of code**.

## 🚀 Quick Start

### Get All Tools with One Line of Code

```python
from afm.core.tools import get_tools

# Get simple format descriptions of all tools
tools = get_tools()
print(tools)
```

### Get OpenAI Function Calling Format

```python
from afm.core.tools import get_tools

# Get OpenAI format, can be directly used with OpenAI API
openai_tools = get_tools("openai")

# Usage example: pass to OpenAI API
# client.chat.completions.create(
#     model="gpt-4",
#     messages=[...],
#     tools=openai_tools
# )
```

### Get JSON Format

```python
from afm.core.tools import get_tools_json

# Get JSON string
tools_json = get_tools_json("openai")
print(tools_json)
```

### Get Tool Summary

```python
from afm.core.tools import get_tools_summary

# Get text summary
summary = get_tools_summary()
print(summary)
```

## 📦 Supported Formats

### 1. Simple Format (Default)

A simple and readable format, suitable for quick viewing:

```python
tools = get_tools("simple")
# Output:
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

### 2. OpenAI Function Calling Format

Format compliant with OpenAI API specifications:

```python
tools = get_tools("openai")
# Output:
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
#             "description": "Parameter image_path"
#           }
#         },
#         "required": ["image_path"]
#       }
#     }
#   }
# ]
```

### 3. LangChain Format

Format suitable for use with the LangChain framework:

```python
tools = get_tools("langchain")
# Output:
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

## 💡 Complete Usage Examples

### Example 1: Integration with OpenAI API

```python
from openai import OpenAI
from afm.core.tools import get_tools

client = OpenAI()

# Get all tools
tools = get_tools("openai")

# Use tools
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Help me identify the text in this image: test.png"}
    ],
    tools=tools,
    tool_choice="auto"
)

# Handle tool calls
for tool_call in response.choices[0].message.tool_calls:
    tool_name = tool_call.function.name
    # Call the corresponding tool
    from afm.core.tools import registry
    result = registry.call_tool(tool_name, **eval(tool_call.function.arguments))
```

### Example 2: Dynamic Tool Selection

```python
from afm.core.tools import get_tools, registry

# Get all tool descriptions
tools = get_tools("simple")

# Let user select a tool
print("Available tools:")
for i, tool in enumerate(tools, 1):
    print(f"{i}. {tool['name']}: {tool['description']}")

# Call tool based on user selection
choice = int(input("Select tool number: ")) - 1
selected_tool = tools[choice]

# Call tool
result = registry.call_tool(selected_tool["name"], image_path="test.png")
print(result)
```

### Example 3: Tool Documentation Generation

```python
from afm.core.tools import get_tools_summary, get_tools_json

# Generate tool documentation
summary = get_tools_summary()
print("=== Tool Summary ===")
print(summary)

# Generate JSON documentation
tools_json = get_tools_json("simple", indent=2)
with open("tools_documentation.json", "w", encoding="utf-8") as f:
    f.write(tools_json)
```

### Example 4: Advanced Usage - Custom Reader

```python
from afm.core.tool_reader import ToolReader
from afm.core.tool_registry import get_registry

# Create custom reader
registry = get_registry()
reader = ToolReader(registry)

# Get specific tool information
tool_info = reader.get_tool_info("ocr_demo_extract_text")
print(f"Tool name: {tool_info['name']}")
print(f"Description: {tool_info['description']}")
print(f"Parameters: {tool_info['parameters']}")

# Get all tool names
all_tool_names = reader.get_all_tools()
print(f"All tools: {all_tool_names}")
```

## 🎯 Integration with AI Frameworks

### OpenAI

```python
from openai import OpenAI
from afm.core.tools import get_tools

client = OpenAI()
tools = get_tools("openai")

# Direct usage
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

# Get tool descriptions
tools_desc = get_tools("langchain")

# Create LangChain tool wrappers
from langchain.tools import Tool

langchain_tools = []
for tool_desc in tools_desc:
    tool = Tool(
        name=tool_desc["name"],
        description=tool_desc["description"],
        func=lambda name=tool_desc["name"]: registry.call_tool(name, **kwargs)
    )
    langchain_tools.append(tool)

# Use tools
llm = ChatOpenAI(model="gpt-4")
agent = create_openai_tools_agent(llm, langchain_tools, ...)
```

### Anthropic Claude

```python
import anthropic
from afm.core.tools import get_tools

client = anthropic.Anthropic()

# Convert to Claude format
tools = get_tools("openai")
claude_tools = [tool["function"] for tool in tools]

response = client.messages.create(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": "..."}],
    tools=claude_tools
)
```

## 📊 Output Format Comparison

| Format | Use Case | Features |
|--------|----------|----------|
| `simple` | Quick viewing, documentation | Easy to read, includes usage examples |
| `openai` | OpenAI API | Compliant with OpenAI specifications, can be used directly |
| `langchain` | LangChain framework | Includes complete metadata, signature information |

## 🔧 Advanced Features

### Filter Tools

```python
from afm.core.tools import get_tools

# Get all tools
all_tools = get_tools("simple")

# Filter OCR-related tools
ocr_tools = [t for t in all_tools if "ocr" in t["name"].lower()]

# Filter tools from specific plugin
plugin_tools = [t for t in all_tools if t.get("plugin") == "ocr_demo"]
```

### Tool Statistics

```python
from afm.core.tools import get_tools

tools = get_tools("simple")

# Statistics
total_tools = len(tools)
plugins = set(t.get("plugin") for t in tools if t.get("plugin"))
required_params = sum(
    sum(1 for p in t["parameters"].values() if p.get("required", False))
    for t in tools
)

print(f"Total tools: {total_tools}")
print(f"Plugins: {len(plugins)}")
print(f"Total required parameters: {required_params}")
```

## 🐛 Troubleshooting

### No Tools Available

```python
from afm.core.tools import get_tools, registry

# Check if tools are registered
if len(registry.list_tools()) == 0:
    print("No registered tools, please ensure plugins are properly installed")
else:
    tools = get_tools()
    print(f"Found {len(tools)} tools")
```

### Tool Format Error

```python
from afm.core.tools import get_tools_json

try:
    tools_json = get_tools_json("openai")
    # Validate JSON format
    import json
    json.loads(tools_json)
    print("JSON format is correct")
except Exception as e:
    print(f"Error: {e}")
```

## 💡 Best Practices

1. **Use appropriate format**: Choose the corresponding format based on your AI framework
2. **Cache tool descriptions**: Tool descriptions don't change frequently, can be cached
3. **Error handling**: Always check if tool exists before calling
4. **Documentation**: Use `get_tools_summary()` to generate tool documentation

## 📚 Related Documentation

- [Tool Registry System Usage Guide](./USAGE_TOOL_REGISTRY.md)
- [Plugin Development Guide](./PLUGIN_GUIDE.md) (if exists)
