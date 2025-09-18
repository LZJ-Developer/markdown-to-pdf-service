#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Markdown转换器API - 为LLM调用设计的简洁接口
"""

import os
import sys
import subprocess
import platform
from typing import Dict, Optional, Any

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.base_converter import MarkdownConverter


def docx_to_pdf_with_libreoffice(docx_file: str, output_dir: str) -> bool:
    """使用LibreOffice转换DOCX为PDF"""
    
    # 根据操作系统确定LibreOffice命令
    system = platform.system()
    if system == "Darwin":  # macOS
        cmd = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    elif system == "Windows":
        cmd = 'soffice.exe'  # 需要在PATH中
    else:  # Linux
        cmd = 'libreoffice'
    
    try:
        # LibreOffice命令行转换
        subprocess.run([
            cmd,
            '--headless',  # 无界面模式
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            docx_file
        ], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"LibreOffice转换失败: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"找不到LibreOffice，请先安装")
        return False


def convert_markdown_file(
    markdown_path: str,
    markdown_filename: str,
    output_format: str,
    template_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """将Markdown文件转换为指定格式"""
    
    # 构建完整路径
    input_file = os.path.join(markdown_path, markdown_filename)
    base_name = os.path.splitext(markdown_filename)[0]
    output_file = os.path.join(markdown_path, f"{base_name}.{output_format}")
    
    # PDF格式：先转DOCX，再转PDF
    if output_format == 'pdf':
        try:
            # 第一步：Markdown → DOCX
            docx_file = os.path.join(markdown_path, f"{base_name}.docx")
            converter = MarkdownConverter()
            docx_result = converter.convert(
                input_file=input_file,
                output_format='docx',
                output_file=docx_file,
                options=template_options or {}
            )
            
            if not docx_result["success"]:
                return {
                    "success": False,
                    "output_path": None,
                    "error_msg": f"DOCX转换失败: {docx_result['error_msg']}",
                    "metadata": {"format": "pdf"}
                }
            
            # 第二步：DOCX → PDF (使用LibreOffice)
            if docx_to_pdf_with_libreoffice(docx_file, markdown_path):
                return {
                    "success": True,
                    "output_path": output_file,
                    "error_msg": None,
                    "metadata": {"format": "pdf", "title": template_options.get("title", "")}
                }
            else:
                return {
                    "success": False,
                    "output_path": None,
                    "error_msg": "LibreOffice转换PDF失败，请确保已安装LibreOffice",
                    "metadata": {"format": "pdf"}
                }
            
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "error_msg": f"PDF转换失败: {str(e)}",
                "metadata": {"format": "pdf"}
            }
    
    # 其他格式：直接转换
    else:
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
            "template_doc": "docx_converter/templates/reference.docx",
            "title": "大语言模型的能力与应用"
        }
    )
    
    if result["success"]:
        print(f"✓ DOCX转换成功: {result['output_path']}")
    else:
        print(f"✗ DOCX转换失败: {result['error_msg']}")
    
    # 测试转换为PDF
    result = convert_markdown_file(
        markdown_path="../Example",
        markdown_filename="example.md",
        output_format="pdf",
        template_options={"title": "大语言模型的能力与应用"}
    )
    
    if result["success"]:
        print(f"✓ PDF转换成功: {result['output_path']}")
    else:
        print(f"✗ PDF转换失败: {result['error_msg']}")
    
    # 显示支持的格式
    print(f"\n支持的格式: html, docx, pdf")