"""
HTML转换配置管理
"""

import os


class HTMLConfig:
    """HTML转换配置类"""

    # 基础配置
    DEFAULT_TITLE = "Markdown转换文档"
    DEFAULT_ENCODING = "utf-8"

    # 样式文件路径
    STYLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles")

    # MathJax配置 - 仅支持本地加载
    MATHJAX_LOCAL_PATH = os.getenv(
        "MATHJAX_LOCAL_PATH",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'js', 'mathjax', 'tex-mml-chtml.js'),
    )
    
    CUSTOM_CSS = os.path.join(STYLES_DIR, "custom.css")
    

    @classmethod
    def get_css_files(cls):
        """获取CSS文件路径 - 现在使用合并后的单一文件"""
        return [cls.CUSTOM_CSS]

    @classmethod
    def read_css_content(cls):
        """读取CSS内容 - 从合并后的单一文件读取"""
        if os.path.exists(cls.CUSTOM_CSS):
            with open(cls.CUSTOM_CSS, "r", encoding=cls.DEFAULT_ENCODING) as f:
                return f.read()
        
        # 如果合并文件不存在，回退到原始方式（向后兼容）
        css_content = []
        for css_file in [cls.TABLE_CSS, cls.CUSTOM_CSS, cls.PDF_EXPORT_CSS]:
            if os.path.exists(css_file):
                with open(css_file, "r", encoding=cls.DEFAULT_ENCODING) as f:
                    css_content.append(f.read())
        
        return "\n".join(css_content)

    @classmethod
    def is_local_mathjax_available(cls):
        """
        检查本地MathJax资源是否可用

        Returns:
            bool: 本地MathJax文件是否存在
        """
        return os.path.exists(cls.MATHJAX_LOCAL_PATH)

    @classmethod
    def get_mathjax_source_info(cls):
        """
        获取当前MathJax资源来源信息

        Returns:
            dict: 包含资源来源信息的字典
        """
        local_available = cls.is_local_mathjax_available()

        return {
            "local_available": local_available,
            "source": "local",
            "path": cls.MATHJAX_LOCAL_PATH,
        }
