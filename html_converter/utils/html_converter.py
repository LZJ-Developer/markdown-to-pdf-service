"""
Markdown到HTML的核心转换器
"""
import os
import pypandoc
import tempfile
from .config import HTMLConfig


class HTMLConverter:
    """Markdown转HTML转换器"""
    
    def __init__(self, config=None):
        """
        初始化转换器
        
        Args:
            config: HTMLConfig实例，如果为None则使用默认配置
        """
        self.config = config or HTMLConfig()
    
    def convert_to_html(self, markdown_file, output_file=None, title=None, template=None):
        """
        转换Markdown文件为HTML
        
        Args:
            markdown_file: 输入的Markdown文件路径
            output_file: 输出的HTML文件路径（可选）
            title: HTML文档标题（可选）
            template: 自定义模板路径（可选）
            
        Returns:
            tuple: (success: bool, output_path: str, error_msg: str)
        """
        # 检查输入文件
        if not os.path.exists(markdown_file):
            return False, None, f"找不到文件: {markdown_file}"
        
        # 确定输出文件名
        if output_file is None:
            base_name = os.path.splitext(markdown_file)[0]
            output_file = f"{base_name}.html"
        
        try:
            # 读取Markdown内容
            with open(markdown_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # 获取文档标题（如果未指定）
            if title is None:
                title = self._extract_title(markdown_content) or HTMLConfig.DEFAULT_TITLE
            
            # 创建临时CSS文件
            css_content = self._prepare_css()
            temp_css_file = self._create_temp_css(css_content)
            
            try:
                # 获取pandoc参数
                pandoc_args = HTMLConfig.get_pandoc_args(
                    title=title,
                    template=template,
                    include_styles=False  # 我们手动处理CSS
                )
                
                # 添加临时CSS文件
                pandoc_args.append(f'--include-in-header={temp_css_file}')
                
                # 执行转换
                pypandoc.convert_text(
                    markdown_content,
                    'html5',
                    format='markdown',
                    outputfile=output_file,
                    extra_args=pandoc_args
                )
                
                return True, output_file, None
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_css_file):
                    os.unlink(temp_css_file)
                    
        except Exception as e:
            return False, None, str(e)
    
    def _extract_title(self, markdown_content):
        """从Markdown内容中提取第一个H1标题"""
        lines = markdown_content.split('\n')
        for line in lines:
            if line.strip().startswith('# '):
                return line.strip()[2:].strip()
        return None
    
    def _prepare_css(self):
        """准备CSS内容"""
        css_parts = ['<style>']
        
        # 读取CSS文件
        css_content = HTMLConfig.read_css_content()
        if css_content:
            css_parts.append(css_content)
        
        css_parts.append('</style>')
        return '\n'.join(css_parts)
    
    def _create_temp_css(self, css_content):
        """创建临时CSS文件"""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.html',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(css_content)
            return f.name
    
    def batch_convert_to_html(self, markdown_files, output_dir=None):
        """
        批量转换多个Markdown文件为HTML
        
        Args:
            markdown_files: Markdown文件路径列表
            output_dir: 输出目录（可选）
            
        Returns:
            list: 转换结果列表 [(success, output_path, error_msg), ...]
        """
        results = []
        
        for md_file in markdown_files:
            if output_dir:
                base_name = os.path.basename(md_file)
                output_name = os.path.splitext(base_name)[0] + '.html'
                output_file = os.path.join(output_dir, output_name)
            else:
                output_file = None
            
            result = self.convert_to_html(md_file, output_file)
            results.append(result)
        
        return results