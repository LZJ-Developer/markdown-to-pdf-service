#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Markdown转换器API - 为LLM调用设计的简洁接口
"""

import os
import sys
from typing import Dict, Optional, Any
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common.base_converter import MarkdownConverter

def convert_markdown_file(
    markdown_path: str,
    markdown_filename: str,
    output_format: str,
    template_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    # 构建完整路径
    input_file = os.path.join(markdown_path, markdown_filename)
    
    # 生成输出文件路径
    base_name = os.path.splitext(markdown_filename)[0]
    output_file = os.path.join(markdown_path, f"{base_name}.{output_format}")
    
    # 如果是PDF格式，特殊处理
    if output_format == 'pdf':
        try:
            # 先转换为HTML
            converter = MarkdownConverter()
            html_file = os.path.join(markdown_path, f"{base_name}_temp.html")
            
            # 调用转换器生成HTML
            html_result = converter.convert(
                input_file=input_file,
                output_format='html',
                output_file=html_file,
                options=template_options or {}
            )
            
            if not html_result["success"]:
                return {
                    "success": False,
                    "output_path": None,
                    "error_msg": f"HTML转换失败: {html_result['error_msg']}",
                    "metadata": {"format": "pdf"}
                }
            
            # 使用Playwright渲染并转换为PDF
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # 加载HTML文件
                page.goto(f"file://{os.path.abspath(html_file)}")
                
                # 等待MathJax渲染完成
                page.wait_for_timeout(3000)  # 等待3秒让公式渲染
                
                # 或者更智能地等待MathJax
                page.evaluate("""
                    () => {
                        return new Promise((resolve) => {
                            if (window.MathJax) {
                                window.MathJax.startup.document.state(0);
                                window.MathJax.typesetPromise().then(resolve);
                            } else {
                                resolve();
                            }
                        });
                    }
                """)
                
                # 生成PDF
                page.pdf(
                    path=output_file,
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '20mm',
                        'right': '20mm',
                        'bottom': '20mm',
                        'left': '20mm'
                    }
                )
                
                browser.close()
            
            # 删除临时HTML文件
            if os.path.exists(html_file):
                os.remove(html_file)
            
            return {
                "success": True,
                "output_path": output_file,
                "error_msg": None,
                "metadata": {"format": "pdf", "title": template_options.get("title", "")}
            }
            
        except Exception as e:
            # 清理临时文件
            temp_html = os.path.join(markdown_path, f"{base_name}_temp.html")
            if os.path.exists(temp_html):
                os.remove(temp_html)
                
            return {
                "success": False,
                "output_path": None,
                "error_msg": f"PDF转换失败: {str(e)}",
                "metadata": {"format": "pdf"}
            }
    
    # 其他格式使用原有转换器
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
        "title": "大语言模型的能力与应用"  # 可选：引用样式
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
        output_format="pdf",  # 直接指定pdf格式
        template_options={"title": "大语言模型的能力与应用"}
    )
    if result["success"]:
        print(f"✓ PDF转换成功: {result['output_path']}")
    else:
        print(f"✗ PDF转换失败: {result['error_msg']}")


    # 显示支持的格式
    converter = MarkdownConverter()
    print(f"\n支持的格式: {', '.join(converter.get_supported_formats())}")