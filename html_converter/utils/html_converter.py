"""
Markdown到HTML的核心转换器
"""

import os
import re
import markdown2
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

        # 配置 markdown2 扩展
        self.markdown_extras = {
            # 结构和导航
            "metadata": None,  # 从前置元数据中提取 title, authors, date, tags
            "header-ids": None,  # 为章节生成稳定的锚点
            "toc": None,  # 自动生成目录
            # 表格和图形
            "tables": None,  # GFM/Extra 风格的表格
            "numbering": None,  # 顺序编号（图表/表格/公式）
            # 代码和输出
            "fenced-code-blocks": None,  # ``` 代码块
            "highlightjs-lang": None,  # 支持语言提示进行语法高亮
            "code-friendly": None,  # 在类代码文本中不将 _ / __ 视为强调
            # 链接和交叉引用
            "link-shortrefs": None,  # 允许快捷引用链接
            # 注释和引用
            "footnotes": None,  # 整洁的脚注用于引用/注释
            # 排版和格式控制
            "middle-word-em": None,  # 避免将 snake_case 转换为斜体
            "breaks": {  # 明确控制硬换行
                "on_newline": True,  # 默认保持段落完整
                "on_backslash": True,  # 允许尾随反斜杠强制 <br>
            },
            "cuddled-lists": None,
            "latex": None,  # 转换为 mathlex
            # HTML + 高级块（有时在报告中使用）
            "markdown-in-html": None,  # <div markdown="1">…</div> 内的 markdown
            # 特殊功能
            "wavedrom": None,  # 时序图（需要时）
        }

        # 初始化 markdown2 实例
        self.md = markdown2.Markdown(extras=self.markdown_extras)

    def convert_to_html(
        self, markdown_file, output_file=None, title=None, template=None
    ):
        """
        转换Markdown文件为HTML

        Args:
            markdown_file (str): 输入的Markdown文件路径
            output_file (str, optional): 输出的HTML文件路径（可选）
            title (str, optional): HTML文档标题（可选）
            template (str, optional): 自定义模板路径（可选）

        Returns:
            tuple: (success: bool, output_path: str, error_msg: str)

        Raises:
            FileNotFoundError: 当输入文件不存在时
            IOError: 当文件读写出现问题时
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
            with open(markdown_file, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            # 使用 markdown2 转换内容
            html_content = self.md.convert(markdown_content)

            # 获取文档标题（优先级：参数 > 元数据 > 内容提取 > 默认）
            if title is None:
                # 尝试从 markdown2 元数据中获取标题
                if (
                    hasattr(self.md, "metadata")
                    and self.md.metadata
                    and "title" in self.md.metadata
                ):
                    title = self.md.metadata["title"]
                else:
                    # 从内容中提取标题
                    title = (
                        self._extract_title(markdown_content)
                        or HTMLConfig.DEFAULT_TITLE
                    )

            # 生成完整的HTML文档
            full_html = self._build_complete_html(
                html_content=html_content, title=title, template=template, output_file=output_file
            )

            # 写入输出文件
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(full_html)

            return True, output_file, None

        except Exception as e:
            return False, None, str(e)

    def _extract_title(self, markdown_content):
        """
        从Markdown内容中提取第一个H1标题

        Args:
            markdown_content (str): Markdown内容

        Returns:
            str or None: 提取的标题，如果没有找到则返回None
        """
        lines = markdown_content.split("\n")
        for line in lines:
            if line.strip().startswith("# "):
                return line.strip()[2:].strip()
        return None

    def _build_complete_html(self, html_content, title, template=None, output_file=None):
        """
        构建完整的HTML文档

        Args:
            html_content (str): 转换后的HTML内容
            title (str): 文档标题
            template (str, optional): 自定义模板路径
            output_file (str, optional): 输出文件路径，用于计算相对路径

        Returns:
            str: 完整的HTML文档
        """
        # 获取CSS内容
        css_content = self._get_css_content()

        # 获取MathJax配置
        mathjax_script = self._get_mathjax_script(output_file)

        # 获取动态表格布局脚本
        dynamic_table_script = self._get_dynamic_table_script()

        # 处理表格容器包装
        html_content = self._wrap_tables_in_containers(html_content)

        # 生成目录导航栏（pypandoc风格）
        toc_html, html_content = self._generate_toc_navigation(html_content)

        # 如果有自定义模板，使用模板
        if template and os.path.exists(template):
            return self._apply_template(
                template, html_content, title, css_content, mathjax_script, toc_html, dynamic_table_script
            )

        # 使用默认模板
        return self._build_default_html(
            html_content, title, css_content, mathjax_script, toc_html, dynamic_table_script
        )

    def _get_css_content(self):
        """
        获取CSS内容

        Returns:
            str: CSS样式内容
        """
        css_content = HTMLConfig.read_css_content()
        if css_content:
            return f"<style>\n{css_content}\n</style>"
        return ""

    def _get_mathjax_script(self, output_file_path=None):
        """
        获取MathJax脚本配置，仅支持本地加载

        Args:
            output_file_path (str, optional): 输出HTML文件的路径，用于计算相对路径

        Returns:
            str: MathJax脚本标签

        Raises:
            FileNotFoundError: 当本地MathJax文件不存在时
        """
        # 检查本地MathJax文件是否存在
        if not os.path.exists(HTMLConfig.MATHJAX_LOCAL_PATH):
            raise FileNotFoundError(
                f"本地MathJax文件不存在: {HTMLConfig.MATHJAX_LOCAL_PATH}"
            )
        
        # 如果提供了输出文件路径，计算相对于输出文件的路径
        if output_file_path:
            output_dir = os.path.dirname(os.path.abspath(output_file_path))
            relative_path = os.path.relpath(HTMLConfig.MATHJAX_LOCAL_PATH, output_dir)
            # 确保在Windows和Unix系统上都使用正斜杠
            relative_path = relative_path.replace(os.sep, '/')
        else:
            # 回退到原来的逻辑（相对于html_converter包的路径）
            relative_path = os.path.relpath(
                HTMLConfig.MATHJAX_LOCAL_PATH,
                os.path.dirname(os.path.dirname(__file__)),
            ).replace(os.sep, '/')
        
        return f'<script src="{relative_path}"></script>'

    def _get_dynamic_table_script(self):
        """
        获取动态表格布局脚本

        Returns:
            str: 动态表格脚本HTML
        """
        # 尝试读取本地JavaScript文件
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'static', 'js', 'dynamic-table-layout.js'
        )
        
        if os.path.exists(script_path):
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                return f"<script>\n{script_content}\n</script>"
            except IOError:
                # 如果读取失败，返回空脚本
                pass
        
        # 如果本地文件不存在或读取失败，返回空脚本
        return "<script>console.log('Dynamic table layout script not found');</script>"

    def _wrap_tables_in_containers(self, html_content):
        """
        将表格包装在容器中以支持动态布局

        Args:
            html_content (str): HTML内容

        Returns:
            str: 包装后的HTML内容
        """
        # 使用正则表达式找到所有表格并包装在容器中
        table_pattern = r'(<table[^>]*>.*?</table>)'
        
        def wrap_table(match):
            table_html = match.group(1)
            # 为表格添加动态布局类
            if 'class=' in table_html:
                table_html = re.sub(
                    r'class="([^"]*)"', 
                    r'class="\1 dynamic-layout"', 
                    table_html
                )
            else:
                table_html = table_html.replace('<table', '<table class="dynamic-layout"', 1)
            
            return f'<div class="table-container">{table_html}</div>'
        
        return re.sub(table_pattern, wrap_table, html_content, flags=re.DOTALL)

    def _apply_template(
        self, template_path, html_content, title, css_content, mathjax_script, toc_html, dynamic_table_script
    ):
        """
        应用自定义模板

        Args:
            template_path (str): 模板文件路径
            html_content (str): HTML内容
            title (str): 文档标题
            css_content (str): CSS内容
            mathjax_script (str): MathJax脚本
            toc_html (str): 目录HTML
            dynamic_table_script (str): 动态表格脚本

        Returns:
            str: 应用模板后的HTML
        """
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            # 简单的模板变量替换
            template_content = template_content.replace("{{title}}", title)
            template_content = template_content.replace("{{css}}", css_content)
            template_content = template_content.replace("{{mathjax}}", mathjax_script)
            template_content = template_content.replace("{{toc}}", toc_html)
            template_content = template_content.replace("{{content}}", html_content)
            template_content = template_content.replace("{{dynamic_table_script}}", dynamic_table_script)

            return template_content
        except Exception:
            # 如果模板应用失败，回退到默认模板
            return self._build_default_html(
                html_content, title, css_content, mathjax_script, toc_html, dynamic_table_script
            )

    def _generate_toc_navigation(self, html_content):
        """
        生成pypandoc风格的导航栏

        Args:
            html_content (str): HTML内容

        Returns:
            tuple: (导航栏HTML, 更新后的HTML内容)
        """
        # 提取所有标题
        heading_pattern = r'<h([1-6])(?:\s+id="([^"]*)")?[^>]*>(.*?)</h[1-6]>'
        headings = re.findall(heading_pattern, html_content, re.IGNORECASE | re.DOTALL)

        if not headings:
            return "", html_content

        # 构建导航栏结构
        toc_items = []
        updated_html = html_content

        for level_str, heading_id, heading_text in headings:
            level = int(level_str)

            # 清理标题文本（移除HTML标签）
            clean_text = re.sub(r"<[^>]+>", "", heading_text).strip()

            # 如果没有id，生成一个
            if not heading_id:
                heading_id = self._generate_heading_id(clean_text)
                # 更新原HTML中的标题，添加id
                old_pattern = (
                    f"<h{level_str}([^>]*)>{re.escape(heading_text)}</h{level_str}>"
                )
                new_heading = (
                    f'<h{level_str}\\1 id="{heading_id}">{heading_text}</h{level_str}>'
                )
                updated_html = re.sub(
                    old_pattern, new_heading, updated_html, count=1, flags=re.IGNORECASE
                )

            toc_items.append(
                {
                    "level": level,
                    "id": heading_id,
                    "text": clean_text,
                    "indent": level - 1,
                }
            )

        # 生成嵌套的HTML结构
        return self._build_toc_html(toc_items), updated_html

    def _generate_heading_id(self, text):
        """
        为标题生成ID

        Args:
            text (str): 标题文本

        Returns:
            str: 生成的ID
        """
        # 转换为小写，替换空格和特殊字符为连字符
        heading_id = re.sub(r"[^\w\s-]", "", text.lower())
        heading_id = re.sub(r"[-\s]+", "-", heading_id)
        return heading_id.strip("-")

    def _build_toc_html(self, toc_items):
        """
        构建TOC的HTML结构

        Args:
            toc_items (list): TOC项目列表

        Returns:
            str: TOC HTML
        """
        if not toc_items:
            return ""
        
        # 找到最小标题级别
        min_level = min(item['level'] for item in toc_items)
        
        # 构建嵌套结构
        def build_nested_list(items, start_level):
            if not items:
                return ""
            
            html = ["<ul>"]
            i = 0
            while i < len(items):
                item = items[i]
                if item['level'] < start_level:
                    break
                elif item['level'] == start_level:
                    # 找到所有子项
                    children = []
                    j = i + 1
                    while j < len(items) and items[j]['level'] > start_level:
                        children.append(items[j])
                        j += 1
                    
                    # 添加当前项
                    html.append(f'<li><a href="#{item["id"]}">{item["text"]}</a>')
                    
                    # 递归处理子项
                    if children:
                        child_html = build_nested_list(children, start_level + 1)
                        html.append(child_html)
                    
                    html.append("</li>")
                    i = j
                else:
                    i += 1
            
            html.append("</ul>")
            return "\n".join(html)
        
        # 生成完整的导航栏HTML
        nav_html = ["<nav id=\"TOC\">"]
        nav_html.append(build_nested_list(toc_items, min_level))
        nav_html.append("</nav>")
        
        return "\n".join(nav_html)

    def _build_default_html(
        self, html_content, title, css_content, mathjax_script, toc_html, dynamic_table_script
    ):
        """
        构建默认HTML文档

        Args:
            html_content (str): HTML内容
            title (str): 文档标题
            css_content (str): CSS内容
            mathjax_script (str): MathJax脚本
            toc_html (str): 目录HTML
            dynamic_table_script (str): 动态表格脚本

        Returns:
            str: 完整的HTML文档
        """
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {css_content}
    {mathjax_script}
    {dynamic_table_script}
</head>
<body>
    {toc_html}
    <div class="container">
        <h1 class="document-title">{title}</h1>
        <div class="content">
            {html_content}
        </div>
    </div>
</body>
</html>"""

    def batch_convert_to_html(self, markdown_files, output_dir=None):
        """
        批量转换多个Markdown文件为HTML

        Args:
            markdown_files (list): Markdown文件路径列表
            output_dir (str, optional): 输出目录（可选）

        Returns:
            list: 转换结果列表 [(success, output_path, error_msg), ...]

        Raises:
            TypeError: 当 markdown_files 不是列表时
        """
        results = []

        for md_file in markdown_files:
            if output_dir:
                base_name = os.path.basename(md_file)
                output_name = os.path.splitext(base_name)[0] + ".html"
                output_file = os.path.join(output_dir, output_name)
            else:
                output_file = None

            result = self.convert_to_html(md_file, output_file)
            results.append(result)

        return results
