#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Markdown转换工具命令行接口
"""

import sys
import argparse
from .common.base_converter import MarkdownConverter


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='markdown-convert',
        description='将Markdown文件转换为各种格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换为HTML
  python -m markdownTo.cli example.md html
  
  # 转换为HTML并指定输出文件
  python -m markdownTo.cli example.md html -o output.html
  
  # 批量转换
  python -m markdownTo.cli *.md html -d output_dir/
  
  # 使用自定义标题
  python -m markdownTo.cli example.md html --title "我的文档"
  
  # 查看支持的格式
  python -m markdownTo.cli --list-formats
        """
    )
    
    # 位置参数
    parser.add_argument('input', nargs='*', 
                       help='输入的Markdown文件（支持通配符）')
    parser.add_argument('format', nargs='?',
                       help='输出格式 (html, docx, pdf等)')
    
    # 可选参数
    parser.add_argument('-o', '--output',
                       help='输出文件路径')
    parser.add_argument('-d', '--output-dir',
                       help='批量转换时的输出目录')
    parser.add_argument('--title',
                       help='文档标题')
    parser.add_argument('--template',
                       help='模板文件路径')
    
    # 功能选项
    parser.add_argument('--list-formats', action='store_true',
                       help='列出所有支持的输出格式')
    parser.add_argument('--show-options', metavar='FORMAT',
                       help='显示特定格式的可用选项')
    
    return parser


def main():
    """命令行主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 创建转换器
    converter = MarkdownConverter()
    
    # 处理功能选项
    if args.list_formats:
        print("支持的输出格式:")
        for fmt in converter.get_supported_formats():
            print(f"  - {fmt}")
        return 0
    
    if args.show_options:
        options = converter.get_format_options(args.show_options)
        if options:
            print(f"{args.show_options.upper()} 格式支持的选项:")
            for opt, desc in options.items():
                print(f"  - {opt}: {desc}")
        else:
            print(f"未知格式: {args.show_options}")
        return 0
    
    # 检查必需参数
    if not args.input or not args.format:
        parser.print_help()
        return 1
    
    # 准备转换选项
    options = {}
    if args.title:
        options['title'] = args.title
    if args.template:
        options['template'] = args.template
    
    # 处理文件列表（支持通配符）
    import glob
    input_files = []
    for pattern in args.input:
        matched_files = glob.glob(pattern)
        if matched_files:
            input_files.extend(matched_files)
        else:
            # 如果没有匹配，可能是单个文件
            input_files.append(pattern)
    
    # 执行转换
    if len(input_files) == 1 and not args.output_dir:
        # 单文件转换
        result = converter.convert(
            input_files[0],
            args.format,
            args.output,
            options
        )
        
        if result['success']:
            print(f"✓ 转换成功: {result['output_path']}")
            return 0
        else:
            print(f"✗ 转换失败: {result['error_msg']}", file=sys.stderr)
            return 1
    else:
        # 批量转换
        output_dir = args.output_dir or '.'
        results = converter.batch_convert(
            input_files,
            args.format,
            output_dir,
            options
        )
        
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        print(f"\n转换完成: {success_count}/{total_count} 成功")
        
        # 显示失败的文件
        for i, result in enumerate(results):
            if not result['success']:
                print(f"  ✗ {input_files[i]}: {result['error_msg']}")
        
        return 0 if success_count == total_count else 1


if __name__ == '__main__':
    sys.exit(main())