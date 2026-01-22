# Google Scholar 用户论文爬虫 - 完整使用指南

## 项目概述

这是一个功能完整的 Google Scholar 用户论文爬虫脚本（`scraper.py`），支持爬取指定用户的所有论文信息，并以多种格式导出。

## 主要功能

### ✅ 已完成功能

1. **论文信息爬取**
   - 使用 `pagesize=100` 参数一次性获取最多 100 篇论文
   - 正确提取论文标题、作者、年份、引用数等基本信息
   - 自动获取完整的 Google Scholar 论文详情页面链接

2. **多格式导出**
   - **JSON 格式** (`papers_data.json`)：结构化数据，便于程序处理
   - **HTML 格式** (`papers_data.html`)：美观的表格展示，可直接在浏览器查看
   - **BibTeX 格式** (`papers_data.bib`)：学术论文引用格式

3. **数据统计**
   - 论文总数
   - 发表年份范围
   - 总引用次数
   - 平均引用数

## 快速开始

### 基本用法

```bash
python3 scraper.py PqrvpbkAAAAJ
```

这会生成：
- `papers_data.json` - 论文数据（JSON 格式）
- `papers_data.html` - 论文列表（HTML 表格）
- `papers_data.bib` - 论文引用（BibTeX 格式）

### 自定义输出文件名

```bash
python3 scraper.py PqrvpbkAAAAJ my_papers.json
```

这会生成：
- `my_papers.json`
- `my_papers.html`
- `my_papers.bib`

## 输出文件说明

### JSON 格式示例

```json
[
  {
    "title": "论文标题",
    "authors": "作者1, 作者2",
    "year": 2024,
    "citations": 100,
    "url": "https://scholar.google.com/...",
    "citation_url": "https://scholar.google.com/citations?view_op=view_citation&..."
  }
]
```

### HTML 格式

生成一个美观的表格，可直接在浏览器中打开查看，包含：
- 论文序号
- 论文标题
- 作者列表
- 发表年份
- 引用次数
- Google Scholar 链接

### BibTeX 格式

标准的 BibTeX 条目，可直接导入到文献管理软件（如 Zotero、Mendeley）：

```bibtex
@article{Chen2024_1,
  title={论文标题},
  author={作者1, 作者2},
  year={2024},
  url={https://scholar.google.com/...},
  citations={100}
}
```

## 爬虫框架架构

### 核心类：ScholarUserScraper

```python
class ScholarUserScraper:
    # 主要方法
    - scrape()              # 爬取论文列表
    - save_to_json()        # 保存为 JSON
    - save_to_html()        # 生成 HTML 表格
    - fetch_all_bibtex()    # 爬取 BibTeX 数据
    - save_to_bibtex()      # 保存 BibTeX
    
    # 辅助方法
    - _extract_paper_info() # 解析单篇论文信息
    - _parse_papers()       # 解析论文列表
    - _fetch_bibtex()       # 获取单篇论文的 BibTeX
    - _get_scisig()         # 获取 Google Scholar 设置令牌
    - _apply_bibtex_settings() # 应用 BibTeX 导出设置
```

## 技术细节

### 爬取策略

1. **首页爬取**
   - 使用 `pagesize=100` 参数获取最多 100 篇论文
   - URL: `https://scholar.google.com/citations?user={user_id}&pagesize=100`

2. **论文信息提取**
   - 标题：`<a class="gsc_a_at">`
   - 作者：`<div class="gs_gray">`
   - 年份：`<td class="gsc_a_y"><span class="gsc_a_h">`
   - 引用数：`<td class="gsc_a_c"><a class="gsc_a_ac">`

3. **BibTeX 导出**（架构已建立，需要会话管理）
   - 获取 scisig 令牌：`/scholar_settings`
   - 应用 BibTeX 设置：`/scholar_setprefs`
   - 导出论文：`/citations?view_op=export_citation&output=bibtex`

### 防爬虫措施

- 设置合理的 User-Agent
- 请求间隔（0.5秒）避免被检测
- 使用 requests.Session 管理连接和 Cookie

## 爬取结果示例

成功爬取用户 `PqrvpbkAAAAJ` 的所有论文：

```
开始爬取用户 PqrvpbkAAAAJ 的论文信息...
  [1] Revisiting Scaling Laws for Language Models...
  [2] Pareto self-supervised training for few-shot learning
  ...
  [68] MetaNetwork: A Task-agnostic Network Parameters...

成功爬取 68 篇论文

==================================================
爬取完成！摘要信息：
==================================================
用户ID: PqrvpbkAAAAJ
论文总数: 68
发表年份范围: 2018 - 2025
总引用次数: 1769
平均引用数: 26.01

==================================================
生成的文件：
==================================================
✓ JSON 数据: papers_data.json (24K)
✓ HTML 表格: papers_data.html (32K)
✓ BibTeX 引用: papers_data.bib (24K)
```

## 未来改进方向

1. **BibTeX 实时导出**
   - 实现完整的 Google Scholar 会话管理
   - 从网页动态内容中提取 BibTeX

2. **分页支持**
   - 处理超过 100 篇论文的用户
   - 实现完整的分页机制

3. **高级功能**
   - 导出到其他格式（CSV、RIS）
   - 论文去重和冲突检测
   - 论文分类和标签

4. **性能优化**
   - 多线程并发爬取
   - 缓存机制

## 参考资源

- 原始 scholar.py：Google Scholar 命令行工具
- BeautifulSoup：HTML 解析库
- Requests：HTTP 请求库

## 许可证

基于原始 scholar.py 项目进行改进和扩展。

---

**最后更新**：2025 年 1 月 14 日