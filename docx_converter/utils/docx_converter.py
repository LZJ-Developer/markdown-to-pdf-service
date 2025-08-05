"""
Markdown到DOCX的核心转换器
使用pypandoc支持学术模板
"""
# 使用新的pypandoc实现
from .docx_converter_pypandoc import DOCXConverter

# 原始的python-docx实现已移至 docx_converter_pypandoc.py 文件末尾作为注释保留