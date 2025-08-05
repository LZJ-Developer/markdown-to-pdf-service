"""
基础转换器抽象类 - 支持LLM Function Calling
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class OutputFormat(Enum):
    """支持的输出格式枚举"""
    HTML = "html"
    DOCX = "docx"
    PDF = "pdf"
    LATEX = "latex"
    EPUB = "epub"
    
    @classmethod
    def list_formats(cls):
        """获取所有支持的格式列表"""
        return [format.value for format in cls]


class ConversionResult:
    """转换结果数据类"""
    def __init__(self, success: bool, output_path: Optional[str] = None, 
                 error_msg: Optional[str] = None, metadata: Optional[Dict] = None):
        self.success = success
        self.output_path = output_path
        self.error_msg = error_msg
        self.metadata = metadata or {}
    
    def to_dict(self):
        """转换为字典格式，便于JSON序列化"""
        return {
            "success": self.success,
            "output_path": self.output_path,
            "error_msg": self.error_msg,
            "metadata": self.metadata
        }


class MarkdownConverter:
    """
    通用Markdown转换器 - 可被LLM Function Calling调用
    
    这个类提供了统一的接口来转换Markdown到各种格式
    """
    
    def __init__(self):
        """初始化转换器，注册所有可用的格式转换器"""
        self._converters = {}
        self._register_converters()
    
    def _register_converters(self):
        """注册所有可用的转换器"""
        # 动态导入并注册转换器
        try:
            from html_converter.utils.html_converter import HTMLConverter
            self._converters[OutputFormat.HTML] = HTMLConverter()
        except ImportError as e:
            print(f"Warning: Cannot import HTML converter: {e}")
        
        # 注册DOCX转换器
        try:
            from docx_converter.utils.docx_converter import DOCXConverter
            self._converters[OutputFormat.DOCX] = DOCXConverter()
        except ImportError as e:
            print(f"Warning: Cannot import DOCX converter: {e}")
    
    def convert(self, 
                input_file: str,
                output_format: str,
                output_file: Optional[str] = None,
                options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        转换Markdown文件到指定格式
        
        Args:
            input_file (str): 输入的Markdown文件路径
            output_format (str): 输出格式 (html, docx, pdf等)
            output_file (str, optional): 输出文件路径，如果不指定则自动生成
            options (dict, optional): 格式特定的选项，如:
                - title: 文档标题
                - template: 模板文件路径
                - css_file: CSS文件路径 (HTML专用)
                - styles: 样式设置 (DOCX专用)
                
        Returns:
            dict: 包含转换结果的字典
                {
                    "success": bool,
                    "output_path": str,
                    "error_msg": str,
                    "metadata": dict
                }
                
        Examples:
            >>> converter = MarkdownConverter()
            >>> result = converter.convert(
            ...     "example.md", 
            ...     "html",
            ...     options={"title": "My Document"}
            ... )
            >>> if result["success"]:
            ...     print(f"Converted to: {result['output_path']}")
        """
        # 验证输出格式
        try:
            format_enum = OutputFormat(output_format.lower())
        except ValueError:
            return ConversionResult(
                success=False,
                error_msg=f"不支持的输出格式: {output_format}. 支持的格式: {OutputFormat.list_formats()}"
            ).to_dict()
        
        # 检查是否有对应的转换器
        if format_enum not in self._converters:
            return ConversionResult(
                success=False,
                error_msg=f"转换器未实现: {output_format}"
            ).to_dict()
        
        # 检查输入文件
        if not os.path.exists(input_file):
            return ConversionResult(
                success=False,
                error_msg=f"输入文件不存在: {input_file}"
            ).to_dict()
        
        # 生成输出文件名
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.{format_enum.value}"
        
        # 执行转换
        converter = self._converters[format_enum]
        options = options or {}
        
        try:
            # 根据不同格式调用相应的转换方法
            if format_enum == OutputFormat.HTML:
                success, output_path, error = converter.convert_to_html(
                    input_file,
                    output_file,
                    title=options.get("title"),
                    template=options.get("template")
                )
            elif format_enum == OutputFormat.DOCX:
                # 提取title避免重复传递
                docx_options = options.copy()
                title = docx_options.pop("title", None)
                success, output_path, error = converter.convert_to_docx(
                    input_file,
                    output_file,
                    title=title,
                    **docx_options
                )
            else:
                return ConversionResult(
                    success=False,
                    error_msg=f"转换器方法未实现: {output_format}"
                ).to_dict()
            
            return ConversionResult(
                success=success,
                output_path=output_path,
                error_msg=error,
                metadata={
                    "format": output_format,
                    "options_used": options
                }
            ).to_dict()
            
        except Exception as e:
            return ConversionResult(
                success=False,
                error_msg=f"转换过程出错: {str(e)}"
            ).to_dict()
    
    def batch_convert(self,
                     input_files: List[str],
                     output_format: str,
                     output_dir: Optional[str] = None,
                     options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        批量转换多个Markdown文件
        
        Args:
            input_files (list): Markdown文件路径列表
            output_format (str): 输出格式
            output_dir (str, optional): 输出目录
            options (dict, optional): 转换选项
            
        Returns:
            list: 转换结果列表
        """
        results = []
        
        # 确保输出目录存在
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        for input_file in input_files:
            if output_dir:
                base_name = os.path.basename(input_file)
                name_without_ext = os.path.splitext(base_name)[0]
                output_file = os.path.join(
                    output_dir, 
                    f"{name_without_ext}.{output_format}"
                )
            else:
                output_file = None
            
            result = self.convert(
                input_file,
                output_format,
                output_file,
                options
            )
            results.append(result)
        
        return results
    
    def get_supported_formats(self) -> List[str]:
        """
        获取当前支持的所有输出格式
        
        Returns:
            list: 支持的格式列表
        """
        return [fmt.value for fmt in self._converters.keys()]
    
    def get_format_options(self, output_format: str) -> Dict[str, str]:
        """
        获取特定格式支持的选项说明
        
        Args:
            output_format (str): 输出格式
            
        Returns:
            dict: 选项说明字典
        """
        format_options = {
            "html": {
                "title": "文档标题",
                "template": "HTML模板文件路径",
                "css_file": "自定义CSS文件路径",
                "toc": "是否生成目录 (true/false)",
                "mathjax": "是否支持数学公式 (true/false)"
            },
            "docx": {
                "title": "文档标题",
                "styles": "样式模板文件路径",
                "reference_doc": "参考文档路径"
            },
            "pdf": {
                "title": "文档标题",
                "paper_size": "纸张大小 (A4, Letter等)",
                "margin": "页边距设置"
            }
        }
        
        return format_options.get(output_format.lower(), {})