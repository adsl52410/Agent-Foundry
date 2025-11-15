# Tool Auto-Registration System Usage Guide

## 📋 Overview

Agent Foundry now supports a tool auto-registration mechanism similar to LangChain. Plugins are automatically scanned and registered, becoming directly callable methods.

## 🚀 Usage Methods

### Method 1: Direct Tool Import (Recommended, Similar to LangChain)

```python
# Automatically import registered tools
from afm.core.tools import ocr_demo_extract_text

# Use directly, just like a regular function
result = ocr_demo_extract_text(
    image_path="test.png",
    language="chi_tra+eng",
    enable_fallback=True
)

print(result)
```

### Method 2: Access via Registry

```python
from afm.core.tools import registry

# List all tools
tools = registry.list_tools()
print(f"Available tools: {tools}")

# Get tool
ocr_tool = registry.get_tool("ocr_demo_extract_text")

# Call tool
result = ocr_tool(image_path="test.png")
```

### Method 3: Access via Registry Attributes

```python
from afm.core.tools import registry

# Direct access via attributes (magic methods)
result = registry.ocr_demo_extract_text(image_path="test.png")
```

### Method 4: Dynamic Call

```python
from afm.core.tools import registry

# Dynamically call tool
tool_name = "ocr_demo_extract_text"
result = registry.call_tool(tool_name, image_path="test.png")
```

## 📦 Plugin Auto-Registration

### Auto-Scanning

The system automatically scans all plugins in the `afm/plugins/` directory and registers eligible class methods as tools.

### Supported Plugin Structures

#### 1. Service Class (Auto-register extract_text method)

```python
# afm/plugins/ocr_demo/plugin.py
class OCRService:
    def initialize(self):
        # Initialization logic
        pass
    
    def extract_text(self, image_path: str, **kwargs):
        # OCR logic
        return {"success": True, "data": {...}}
```

**Auto-registered as**: `ocr_demo_extract_text`

#### 2. Using @tool Decorator

```python
from afm.core.tool_registry import tool

@tool(name="my_custom_tool", description="My custom tool")
def my_function(arg1: str, arg2: int = 10) -> str:
    """Tool description"""
    return f"Processing result: {arg1} {arg2}"
```

**Registered as**: `my_custom_tool`

## 🔍 Query Tools

### List All Tools

```python
from afm.core.tools import registry

# List all tool names
tools = registry.list_tools()
for tool_name in tools:
    print(f"- {tool_name}")
```

### Get Tool Metadata

```python
from afm.core.tools import registry

# Get tool information
metadata = registry.get_tool_metadata("ocr_demo_extract_text")
print(f"Description: {metadata['description']}")
print(f"Signature: {metadata['signature']}")
print(f"Plugin: {metadata.get('plugin')}")
```

## 📝 Complete Usage Examples

### Example 1: Basic Usage

```python
from afm.core.tools import ocr_demo_extract_text

# Simple usage
result = ocr_demo_extract_text(image_path="test.png")

if result["success"]:
    print(f"Recognized text: {result['data']['text']}")
    print(f"Confidence: {result['data']['confidence']:.2%}")
```

### Example 2: Batch Processing

```python
from afm.core.tools import ocr_demo_extract_text
from pathlib import Path

# Batch process multiple images
image_dir = Path("./images")
for image_file in image_dir.glob("*.png"):
    result = ocr_demo_extract_text(
        image_path=str(image_file),
        language="chi_tra+eng",
        enable_fallback=True
    )
    print(f"{image_file.name}: {result['success']}")
```

### Example 3: Dynamic Tool Selection

```python
from afm.core.tools import registry

# List all OCR-related tools
ocr_tools = [name for name in registry.list_tools() if 'ocr' in name.lower()]

# Use the first OCR tool
if ocr_tools:
    tool_name = ocr_tools[0]
    result = registry.call_tool(tool_name, image_path="test.png")
    print(result)
```

### Example 4: Integration into Existing Program

```python
from afm.core.tools import registry

class MyApp:
    def __init__(self):
        # Check if tool is available during initialization
        self.ocr_tool = registry.get_tool("ocr_demo_extract_text")
        if self.ocr_tool is None:
            raise RuntimeError("OCR tool not found")
    
    def process_images(self, image_paths: list):
        """Process multiple images"""
        results = []
        for path in image_paths:
            result = self.ocr_tool(image_path=path)
            results.append(result)
        return results

# Usage
app = MyApp()
results = app.process_images(["img1.png", "img2.png"])
```

## 🎯 Tool Naming Rules

- **Service class extract_text method**: `{plugin_name}_extract_text`
  - Example: `ocr_demo_extract_text`
  
- **Functions using @tool decorator**: Use the name specified in the decorator, or the function name
  - Example: `@tool(name="my_tool")` -> `my_tool`

## ⚙️ Custom Tools

### Create Custom Tool

```python
# In your plugin or module
from afm.core.tool_registry import tool, get_registry

@tool(name="calculate_sum", description="Calculate the sum of two numbers")
def add_numbers(a: int, b: int) -> int:
    """Calculate the sum of two numbers"""
    return a + b

# Or manually register
registry = get_registry()
registry.register_tool(
    name="multiply",
    func=lambda x, y: x * y,
    description="Calculate the product of two numbers"
)
```

### Use in Plugins

```python
# afm/plugins/my_plugin/plugin.py
from afm.core.tool_registry import tool

class MyService:
    @tool(name="my_service_process")
    def process(self, data: str) -> str:
        """Process data"""
        return f"Processed: {data}"
```

## 🔧 Advanced Usage

### Disable Auto-Scanning

```python
from afm.core.tool_registry import ToolRegistry

# Create new registry (no auto-scanning)
custom_registry = ToolRegistry()

# Manually register tools
custom_registry.register_tool("my_tool", my_function)
```

### Batch Registration

```python
from afm.core.tool_registry import get_registry

registry = get_registry()

# Batch register multiple tools
tools = {
    "tool1": func1,
    "tool2": func2,
    "tool3": func3,
}

for name, func in tools.items():
    registry.register_tool(name, func)
```

## 📚 Comparison with LangChain

| Feature | LangChain | Agent Foundry |
|---------|-----------|---------------|
| Tool Definition | Use @tool decorator | Auto-scan or @tool decorator |
| Import Method | `from langchain.tools import tool_name` | `from afm.core.tools import tool_name` |
| Auto-Scanning | Requires manual registration | Auto-scan plugin directory |
| Service Classes | Requires manual wrapping | Auto-identify and register |

## 🐛 Troubleshooting

### Tool Not Found

```python
# Check if tool exists
from afm.core.tools import registry

if "ocr_demo_extract_text" in registry.list_tools():
    print("Tool is registered")
else:
    print("Tool not registered, check plugin directory")
```

### Plugin Not Auto-Scanned

1. Ensure plugin directory structure is correct: `afm/plugins/{plugin_name}/plugin.py`
2. Ensure plugin contains identifiable classes or functions
3. Check error messages in logs

### Tool Call Failed

```python
try:
    result = ocr_demo_extract_text(image_path="test.png")
except Exception as e:
    print(f"Tool call failed: {e}")
    # Check tool metadata
    metadata = registry.get_tool_metadata("ocr_demo_extract_text")
    print(f"Tool signature: {metadata['signature']}")
```

## 💡 Best Practices

1. **Use clear tool names**: Ensure tool names are clear and unique
2. **Provide complete docstrings**: Tool descriptions are automatically extracted from `__doc__`
3. **Handle errors**: Tools should return standardized result formats
4. **Reuse service instances**: Service classes automatically use singleton pattern for better performance
5. **Type hints**: Use type hints to make tool signatures clearer
