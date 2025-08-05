# Elsevier（爱思唯尔）模板信息

## 官方下载地址
- **主页**: https://www.elsevier.com/authors/policies-and-guidelines/latex-instructions
- **Word模板下载**: https://www.elsevier.com/authors/author-schemas/word-templates-for-journal-articles

## Elsevier模板特点
1. **专业的表格样式** - 通常包含简洁的表格格式，接近三线表
2. **标准的学术格式** - 符合国际期刊要求
3. **多种模板选择**：
   - Single column（单栏）
   - Double column（双栏）
   - CAS template（更现代的样式）

## 推荐下载
1. **Elsevier CAS template** - 最新的模板，表格样式更简洁
   - 文件名通常为：`cas-dc-template.docx`（双栏）或 `cas-sc-template.docx`（单栏）

2. **传统Elsevier模板**
   - 文件名：`elsarticle-template.docx`

## 使用方法

1. 从上述链接下载模板（需要选择您的期刊类型）
2. 将模板文件放入 `templates/` 文件夹
3. 转换时使用：

```python
# 测试Elsevier模板
result = converter.convert(
    "paper.md",
    "docx",
    options={
        "template_doc": "docx_converter/templates/cas-sc-template.docx",
        "title": "Your Paper Title"
    }
)
```

## 注意事项
- Elsevier的CAS（Camera-ready Article Style）模板的表格样式最接近三线表
- 模板中的表格样式名通常为 "Table Grid Light" 或类似的简洁样式
- 这些模板已经针对学术出版优化，包括正确的字体、间距和样式