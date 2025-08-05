#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Markdown转换器API - 为LLM调用设计的简洁接口
"""

import os
import sys
from typing import Dict, Optional, Any

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.base_converter import MarkdownConverter


def convert_markdown_file(
    markdown_path: str,
    markdown_filename: str,
    output_format: str,
    template_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    将Markdown文件转换为指定格式
    
    Args:
        markdown_path (str): Markdown文件所在的目录路径
        markdown_filename (str): Markdown文件名（包含.md扩展名）
        output_format (str): 输出格式 (html/docx/pdf/latex/epub)
        template_options (dict, optional): 格式特定的选项，如:
            通用选项:
            - title: 文档标题
            
            HTML格式选项:
            - template: 自定义HTML模板文件路径
            注意: CSS样式已内置，无需指定css_file
            
            DOCX格式选项:
            - styles: Word样式模板文件路径
            - reference_doc: 参考文档路径
            
    Returns:
        dict: 转换结果
            {
                "success": bool,        # 是否成功
                "output_path": str,     # 输出文件路径
                "error_msg": str,       # 错误信息
                "metadata": dict        # 元数据
            }
            
    Example:
        >>> # 转换为HTML
        >>> result = convert_markdown_file(
        ...     "/Users/docs",
        ...     "example.md",
        ...     "html",
        ...     {"title": "示例文档"}
        ... )
        >>> 
        >>> # 转换为DOCX
        >>> result = convert_markdown_file(
        ...     "/Users/docs",
        ...     "report.md",
        ...     "docx",
        ...     {"title": "月度报告"}
        ... )
    """
    # 构建完整路径
    input_file = os.path.join(markdown_path, markdown_filename)
    
    # 生成输出文件路径
    base_name = os.path.splitext(markdown_filename)[0]
    output_file = os.path.join(markdown_path, f"{base_name}.{output_format}")
    
    # 创建转换器并执行转换
    converter = MarkdownConverter()
    return converter.convert(
        input_file=input_file,
        output_format=output_format,
        output_file=output_file,
        options=template_options or {}
    )


if __name__ == "__main__":

    # 测试示例
    print("=== Markdown转换器API测试 ===\n")
    
    # 测试转换为HTML
    result = convert_markdown_file(
        markdown_path="../Example",
        markdown_filename="example.md",
        output_format="html",
        template_options={"title": "大语言模型的能力与应用"}
    )
    
    if result["success"]:
        print(f"✓ HTML转换成功: {result['output_path']}")
    else:
        print(f"✗ HTML转换失败: {result['error_msg']}")
    
    # 测试转换为DOCX
    result = convert_markdown_file(
        markdown_path="../Example",
        markdown_filename="example.md",
        output_format="docx",
        template_options={
        "template_doc": "docx_converter/templates/ference.docx",
        "title": "大语言模型的能力与应用"  # 可选：引用样式
    }
    )
    
    if result["success"]:
        print(f"✓ DOCX转换成功: {result['output_path']}")
    else:
        print(f"✗ DOCX转换失败: {result['error_msg']}")
    
    # 显示支持的格式
    converter = MarkdownConverter()
    print(f"\n支持的格式: {', '.join(converter.get_supported_formats())}")