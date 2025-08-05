"""
HTML转换配置管理
"""
import os

class HTMLConfig:
    """HTML转换配置类"""
    
    # 基础配置
    DEFAULT_TITLE = "Markdown转换文档"
    DEFAULT_ENCODING = "utf-8"
    
    # pypandoc默认参数
    DEFAULT_PANDOC_ARGS = [
        '--mathjax',  # 支持数学公式
        '--standalone',  # 生成完整的HTML文档
        '--toc',  # 生成目录
        '--highlight-style=pygments',  # 代码高亮
    ]
    
    # 样式文件路径
    STYLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles')
    TABLE_CSS = os.path.join(STYLES_DIR, 'table.css')
    CUSTOM_CSS = os.path.join(STYLES_DIR, 'custom.css')
    
    @classmethod
    def get_pandoc_args(cls, title=None, template=None, include_styles=True):
        """
        获取pypandoc参数
        
        Args:
            title: 文档标题
            template: 模板文件路径
            include_styles: 是否包含默认样式
            
        Returns:
            list: pypandoc参数列表
        """
        args = cls.DEFAULT_PANDOC_ARGS.copy()
        
        # 设置标题
        if title:
            args.extend(['--metadata', f'title={title}'])
        else:
            args.extend(['--metadata', f'title={cls.DEFAULT_TITLE}'])
        
        # 设置模板
        if template and os.path.exists(template):
            args.append(f'--template={template}')
        
        # 添加样式文件
        if include_styles:
            css_files = cls.get_css_files()
            for css_file in css_files:
                if os.path.exists(css_file):
                    args.append(f'--include-in-header={css_file}')
        
        return args
    
    @classmethod
    def get_css_files(cls):
        """获取所有CSS文件路径"""
        return [cls.TABLE_CSS, cls.CUSTOM_CSS]
    
    @classmethod
    def read_css_content(cls):
        """读取所有CSS内容并合并"""
        css_content = []
        for css_file in cls.get_css_files():
            if os.path.exists(css_file):
                with open(css_file, 'r', encoding=cls.DEFAULT_ENCODING) as f:
                    css_content.append(f.read())
        
        return '\n'.join(css_content)