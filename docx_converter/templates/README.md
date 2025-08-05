# DOCX 学术模板说明

这个文件夹用于存放 DOCX 格式的学术论文模板。

## 使用方法

1. 下载您需要的学术期刊/会议的 DOCX 模板
2. 将模板文件放在此文件夹中
3. 在转换时通过 `template_doc` 参数指定模板

## 常见学术模板下载地址

### 英文模板
- **IEEE**: https://www.ieee.org/conferences/publishing/templates.html
- **ACM**: https://www.acm.org/publications/proceedings-template
- **Springer**: https://www.springer.com/gp/authors-editors/manuscript-preparation/word-templates
- **Elsevier**: https://www.elsevier.com/authors/author-schemas/latex-instructions

### 中文模板
- **中国科学**: http://www.scichina.com/
- **计算机学报**: http://cjc.ict.ac.cn/
- **软件学报**: http://www.jos.org.cn/

## 模板文件命名建议

- `ieee_conference.docx` - IEEE 会议论文模板
- `acm_sigconf.docx` - ACM 会议论文模板
- `springer_lncs.docx` - Springer LNCS 模板
- `chinese_journal.docx` - 中文期刊通用模板

## 使用示例

```python
from markdownTo.common.base_converter import MarkdownConverter

converter = MarkdownConverter()
result = converter.convert(
    "paper.md",
    "docx",
    options={
        "template_doc": "docx_converter/templates/ieee_conference.docx",
        "csl_file": "ieee.csl"  # 可选：引用样式
    }
)
```

## 注意事项

1. 模板文件必须是有效的 DOCX 文件
2. 模板中的样式会被自动应用到生成的文档
3. 建议使用官方提供的最新模板
4. 中文模板需要确保字体设置正确（如宋体、黑体等）