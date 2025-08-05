"""
Markdown到DOCX的转换器 - 使用pypandoc
支持学术文献模板
"""
import os
import pypandoc
from .config import DOCXConfig


class DOCXConverter:
    """Markdown转DOCX转换器 - pypandoc版本"""
    
    def __init__(self, config=None):
        """
        初始化转换器
        
        Args:
            config: DOCXConfig实例，如果为None则使用默认配置
        """
        self.config = config or DOCXConfig()
    
    def convert_to_docx(self, markdown_file, output_file=None, title=None, **kwargs):
        """
        使用pypandoc转换Markdown文件为DOCX
        
        Args:
            markdown_file: 输入的Markdown文件路径
            output_file: 输出的DOCX文件路径（可选）
            title: 文档标题（可选）
            **kwargs: 其他选项
                - template_doc: DOCX模板文件路径
                - csl_file: CSL引用样式文件路径
                - bibliography: 参考文献文件路径（.bib）
                - toc: 是否生成目录
                
        Returns:
            tuple: (success: bool, output_path: str, error_msg: str)
        """
        # 检查输入文件
        if not os.path.exists(markdown_file):
            return False, None, f"找不到文件: {markdown_file}"
        
        # 确定输出文件名
        if output_file is None:
            base_name = os.path.splitext(markdown_file)[0]
            output_file = f"{base_name}.docx"
        
        try:
            # 准备pypandoc参数
            extra_args = []
            
            # 添加中文支持
            extra_args.extend([
                '--variable', 'CJKmainfont=宋体',
                '--variable', 'CJKsansfont=黑体',
                '--variable', 'CJKmonofont=仿宋'
            ])
            
            # 模板文件
            template_doc = kwargs.get('template_doc')
            if template_doc and os.path.exists(template_doc):
                extra_args.extend(['--reference-doc', template_doc])
            else:
                # 检查默认模板
                default_template = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'templates',
                    'default_academic.docx'
                )
                if os.path.exists(default_template):
                    extra_args.extend(['--reference-doc', default_template])
            
            # CSL引用样式
            csl_file = kwargs.get('csl_file')
            if csl_file and os.path.exists(csl_file):
                extra_args.extend(['--csl', csl_file])
                extra_args.append('--citeproc')  # 启用引用处理
            
            # 参考文献文件
            bibliography = kwargs.get('bibliography')
            if bibliography and os.path.exists(bibliography):
                extra_args.extend(['--bibliography', bibliography])
            
            # 标题
            if title:
                extra_args.extend(['--metadata', f'title={title}'])
            
            # 目录
            if kwargs.get('toc', False):
                extra_args.append('--toc')
                extra_args.extend(['--toc-depth', '3'])
            
            # 表格样式设置
            if kwargs.get('three_line_table', True):
                # 尝试使用更简洁的表格样式
                extra_args.extend([
                    '--variable', 'tablestyle=Plain Table 1'
                ])
            
            # 其他有用的参数
            extra_args.extend([
                '--standalone',  # 生成完整文档
                '--wrap=preserve',  # 保留换行
                '--columns=80'  # 列宽
            ])
            
            # 执行转换
            pypandoc.convert_file(
                markdown_file,
                'docx',
                outputfile=output_file,
                extra_args=extra_args
            )
            
            return True, output_file, None
            
        except Exception as e:
            return False, None, str(e)


"""
# =====================================================
# 以下是原始的python-docx实现，保留作为参考
# =====================================================

import markdown
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn


class DOCXConverterPythonDocx:
    '''原始的python-docx实现版本'''
    
    def __init__(self, config=None):
        self.config = config or DOCXConfig()
        self.heading_counters = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        self.table_counter = 0
        self.image_counter = 0
    
    def convert_to_docx(self, markdown_file, output_file=None, title=None, **kwargs):
        # ... 原实现代码 ...
        # 具体实现参见 docx_converter.py
        pass
    
    def _setup_document_styles(self, doc):
        # 设置文档样式，确保中文兼容性
        sections = doc.sections
        for section in sections:
            section.top_margin = DOCXConfig.PAGE_MARGIN['top']
            section.bottom_margin = DOCXConfig.PAGE_MARGIN['bottom']
            section.left_margin = DOCXConfig.PAGE_MARGIN['left']
            section.right_margin = DOCXConfig.PAGE_MARGIN['right']
        
        # 设置默认样式的中文字体
        styles = doc.styles
        
        # Normal样式
        normal_style = styles['Normal']
        normal_style.font.name = DOCXConfig.DEFAULT_ASCII_FONT
        normal_style.font.size = DOCXConfig.get_font_settings()['size']
        normal_style._element.rPr.rFonts.set(qn('w:eastAsia'), DOCXConfig.DEFAULT_EAST_ASIA_FONT)
        
        # 标题样式
        for i in range(1, 7):
            heading_style = styles[f'Heading {i}']
            font_settings = DOCXConfig.get_font_settings(f'heading{i}')
            heading_style.font.name = font_settings['ascii_font']
            heading_style.font.size = font_settings['size']
            heading_style._element.rPr.rFonts.set(qn('w:eastAsia'), font_settings['east_asia_font'])
    
    # ... 其他方法的实现 ...
    # 完整实现请参考原始的 docx_converter.py 文件
"""