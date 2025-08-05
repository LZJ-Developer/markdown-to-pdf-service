"""
DOCX转换配置管理
支持学术模板和中文兼容性
"""
import os
# 注意：新的pypandoc实现不需要docx库
# from docx.shared import Pt, Inches
# from docx.enum.text import WD_ALIGN_PARAGRAPH


class DOCXConfig:
    """DOCX转换配置类"""
    
    # 字体配置 - 这是处理中文兼容性的关键
    DEFAULT_ASCII_FONT = 'Times New Roman'  # 英文字体
    DEFAULT_EAST_ASIA_FONT = '宋体'          # 中文字体（宋体兼容性最好）
    DEFAULT_FONT_SIZE = 12                   # 默认字号（磅）
    
    # 标题字体大小
    HEADING_SIZES = {
        1: 24,  # 一级标题
        2: 18,  # 二级标题
        3: 16,  # 三级标题
        4: 14,  # 四级标题
        5: 12,  # 五级标题
        6: 12   # 六级标题
    }
    
    # 页面设置（单位：英寸）
    PAGE_MARGIN = {
        'top': 1.0,
        'bottom': 1.0,
        'left': 1.25,
        'right': 1.25
    }
    
    # 段落样式
    PARAGRAPH_SPACING = {
        'before': 0,          # 段前间距（磅）
        'after': 12,          # 段后间距（磅）
        'line_spacing': 1.5   # 行距
    }
    
    # 表格样式
    TABLE_STYLE = 'Table Grid'  # 网格型表格
    
    # 列表样式
    LIST_STYLES = {
        'bullet': 'List Bullet',    # 无序列表
        'number': 'List Number'     # 有序列表
    }
    
    # 样式映射
    STYLE_MAP = {
        'normal': 'Normal',
        'title': 'Title',
        'heading1': 'Heading 1',
        'heading2': 'Heading 2', 
        'heading3': 'Heading 3',
        'heading4': 'Heading 4',
        'heading5': 'Heading 5',
        'heading6': 'Heading 6',
        'quote': 'Quote',
        'code': 'Code'
    }
    
    @classmethod
    def get_font_settings(cls, style_type='normal'):
        """
        获取字体设置
        
        Args:
            style_type: 样式类型
            
        Returns:
            dict: 包含字体设置的字典
        """
        size = cls.DEFAULT_FONT_SIZE
        
        # 根据样式类型调整字号
        if style_type.startswith('heading'):
            level = int(style_type[-1]) if style_type[-1].isdigit() else 1
            size = cls.HEADING_SIZES.get(level, cls.DEFAULT_FONT_SIZE)
        elif style_type == 'title':
            size = cls.HEADING_SIZES[1]
        
        return {
            'ascii_font': cls.DEFAULT_ASCII_FONT,
            'east_asia_font': cls.DEFAULT_EAST_ASIA_FONT,
            'size': size  # 返回磅值，不再使用Pt()
        }
    
    @classmethod
    def apply_font_to_run(cls, run, style_type='normal', bold=False, italic=False):
        """
        应用字体设置到run对象
        处理中文兼容性的核心方法
        
        Args:
            run: python-docx的run对象
            style_type: 样式类型
            bold: 是否加粗
            italic: 是否斜体
        """
        font_settings = cls.get_font_settings(style_type)
        
        # 设置字体 - 关键：必须同时设置name和element
        run.font.name = font_settings['ascii_font']
        run.font.size = font_settings['size']
        run.font.bold = bold
        run.font.italic = italic
        
        # 直接操作XML确保中文字体正确应用
        # 这是解决中文兼容性问题的关键
        from docx.oxml.ns import qn
        r = run._element
        rPr = r.get_or_add_rPr()
        rFonts = rPr.get_or_add_rFonts()
        rFonts.set(qn('w:ascii'), font_settings['ascii_font'])
        rFonts.set(qn('w:hAnsi'), font_settings['ascii_font'])
        rFonts.set(qn('w:eastAsia'), font_settings['east_asia_font'])
    
    @classmethod
    def apply_paragraph_format(cls, paragraph, alignment=None):
        """
        应用段落格式
        
        Args:
            paragraph: python-docx的paragraph对象
            alignment: 对齐方式
        """
        # 设置段落间距
        paragraph.paragraph_format.space_before = cls.PARAGRAPH_SPACING['before']
        paragraph.paragraph_format.space_after = cls.PARAGRAPH_SPACING['after']
        paragraph.paragraph_format.line_spacing = cls.PARAGRAPH_SPACING['line_spacing']
        
        # 设置对齐
        if alignment:
            paragraph.alignment = alignment
    
    # ===== 新增：学术模板相关配置 =====
    
    # 模板目录
    TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    
    # 预定义的学术模板
    ACADEMIC_TEMPLATES = {
        'ieee': 'ieee_conference.docx',
        'acm': 'acm_sigconf.docx', 
        'springer': 'springer_lncs.docx',
        'chinese': 'chinese_journal.docx',
        'default': 'default_academic.docx'
    }
    
    # CSL引用样式
    CSL_STYLES = {
        'ieee': 'ieee.csl',
        'apa': 'apa.csl',
        'mla': 'mla.csl',
        'chicago': 'chicago-author-date.csl',
        'gb7714': 'chinese-gb7714-2005-numeric.csl'  # 中文参考文献格式
    }
    
    @classmethod
    def get_template_path(cls, template_name='default'):
        """获取模板文件路径"""
        filename = cls.ACADEMIC_TEMPLATES.get(template_name, template_name)
        if not filename.endswith('.docx'):
            filename += '.docx'
        return os.path.join(cls.TEMPLATES_DIR, filename)