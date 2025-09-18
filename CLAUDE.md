# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个将Markdown文档转换为多种格式（HTML、DOCX等）的Python库，提供了命令行接口和API接口两种使用方式。

## 核心架构

### 模块结构
- `common/base_converter.py`: 转换器基类，提供统一接口和格式注册机制
- `html_converter/`: HTML格式转换实现，包含样式文件和模板
- `docx_converter/`: DOCX格式转换实现，支持Word模板和样式
- `cli.py`: 命令行接口，支持单文件和批量转换
- `markdown_converter_api.py`: 简洁的API接口，为LLM调用设计

### 转换流程
1. `MarkdownConverter` 作为统一入口，根据格式分发到具体转换器
2. 各格式转换器实现具体的转换逻辑
3. 返回标准化的 `ConversionResult` 结果

## 开发命令

### 安装依赖
```bash
# 使用uv（推荐，项目已有uv.lock）
uv pip install python-docx markdown beautifulsoup4 pypandoc pillow

# 或使用pip
pip install python-docx markdown beautifulsoup4 pypandoc pillow
```

### 运行转换

#### 命令行方式
```bash
# 单文件转换
python -m markdownTo.cli example.md html
python -m markdownTo.cli example.md docx -o output.docx

# 批量转换
python -m markdownTo.cli *.md html -d output_dir/

# 查看支持的格式
python -m markdownTo.cli --list-formats
```

#### API方式
```python
from markdownTo.markdown_converter_api import convert_markdown_file

# 转换为HTML
result = convert_markdown_file(
    "/path/to/markdown",
    "example.md",
    "html",
    {"title": "文档标题"}
)

# 转换为DOCX
result = convert_markdown_file(
    "/path/to/markdown",
    "example.md",
    "docx",
    {"title": "文档标题", "template_doc": "path/to/template.docx"}
)
```

### 测试
```bash
# 运行API测试（需要先启动API服务器）
python test_api.py

# 测试基础功能
python markdown_converter_api.py
```

## 扩展新格式

1. 在对应的converter目录下创建新的转换器类
2. 实现 `convert_to_format()` 方法
3. 在 `base_converter.py` 的 `_register_converters()` 中注册新格式
4. 更新 `OutputFormat` 枚举添加新格式

## 注意事项

- 所有转换器返回统一的 `ConversionResult` 字典格式
- 中文文档使用宋体，英文使用Times New Roman
- 图片路径相对于Markdown文件所在目录
- DOCX模板文件在 `docx_converter/templates/` 目录下