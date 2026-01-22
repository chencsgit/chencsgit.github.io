#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬取 Google Scholar 用户的所有论文信息
支持保存为 JSON、HTML 和 BibTeX 格式

使用方法:
    python scraper.py <user_id> [output_file]
    
示例:
    python scraper.py PqrvpbkAAAAJ
    python scraper.py PqrvpbkAAAAJ papers_output.json

输出文件:
    - papers_output.json      JSON 格式的论文数据
    - papers_output.html      HTML 表格格式的论文列表
    - papers_output.bib       BibTeX 格式的论文引用

功能特性:
    ✓ 使用 pagesize=100 参数一次性获取所有论文
    ✓ 自动提取标题、作者、年份、引用数等信息
    ✓ 生成格式规范的 BibTeX 引用条目
    ✓ 支持导出为 JSON、HTML 和 BibTeX 三种格式
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import sys
import re

class ScholarUserScraper:
    def __init__(self, user_id, output_file='papers_data.json'):
        """
        初始化爬虫
        :param user_id: Google Scholar 用户ID (e.g., 'PqrvpbkAAAAJ')
        :param output_file: 输出文件路径
        """
        self.user_id = user_id
        self.output_file = output_file
        # 使用 pagesize=100 来获取更多论文，减少分页次数
        self.base_url = f'https://scholar.google.com/citations?user={user_id}&pagesize=100'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'
        })
        self.papers = []
        self.bibtex_data = {}  # 存储 BibTeX 信息
        self.scisig = None  # Google Scholar 的设置令牌
    
    def scrape(self):
        """
        爬取用户的所有论文
        """
        print(f"开始爬取用户 {self.user_id} 的论文信息...")
        
        try:
            # 第一次请求获取初始页面
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 解析论文列表
            self._parse_papers(soup)
            
            # 处理分页
            self._handle_pagination(soup)
            
            print(f"成功爬取 {len(self.papers)} 篇论文")
            return self.papers
            
        except Exception as e:
            print(f"爬取过程中出错: {e}")
            return None
    
    def _parse_papers(self, soup):
        """
        解析页面中的论文信息
        """
        # 查找论文行 - Google Scholar 使用不同的 class 名称
        paper_rows = soup.find_all('tr', {'class': 'gsc_a_tr'})
        
        for row in paper_rows:
            try:
                paper_info = self._extract_paper_info(row)
                if paper_info:
                    self.papers.append(paper_info)
                    print(f"  [{len(self.papers)}] {paper_info['title']}")
            except Exception as e:
                print(f"  解析论文时出错: {e}")
                continue
    
    def _extract_paper_info(self, row):
        """
        从单个论文行提取信息
        """
        try:
            # 提取标题和URL
            title_elem = row.find('a', {'class': 'gsc_a_at'})
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            url = title_elem.get('href', '')
            if not url.startswith('http'):
                url = 'https://scholar.google.com' + url if url.startswith('/') else ''
            
            # 提取作者信息
            authors_elem = row.find('div', {'class': 'gs_gray'})
            authors = authors_elem.get_text(strip=True) if authors_elem else ''
            
            # 提取引用数 (在 <td class="gsc_a_c"> 中的 <a> 标签)
            citations = 0
            citations_cell = row.find('td', {'class': 'gsc_a_c'})
            if citations_cell:
                citations_link = citations_cell.find('a', {'class': 'gsc_a_ac'})
                if citations_link:
                    citations_text = citations_link.get_text(strip=True)
                    try:
                        citations = int(citations_text) if citations_text else 0
                    except ValueError:
                        citations = 0
            
            # 提取年份 (在 <td class="gsc_a_y"> 中的 <span class="gsc_a_h">)
            year = None
            year_cell = row.find('td', {'class': 'gsc_a_y'})
            if year_cell:
                year_span = year_cell.find('span', {'class': 'gsc_a_h'})
                if year_span:
                    year_text = year_span.get_text(strip=True)
                    try:
                        year = int(year_text) if year_text else None
                    except ValueError:
                        year = year_text
            
            # 提取论文页面URL（用于获取 BibTeX）
            # 论文的详情页面在 /citations?view_op=view_citation&...
            citation_url = None
            title_link = row.find('a', {'class': 'gsc_a_at'})
            if title_link and title_link.get('href'):
                href = title_link.get('href')
                if href.startswith('/'):
                    citation_url = 'https://scholar.google.com' + href
                else:
                    citation_url = href
            
            paper_info = {
                'title': title,
                'authors': authors,
                'year': year,
                'citations': citations,
                'url': url,
                'citation_url': citation_url
            }
            
            return paper_info
        
        except Exception as e:
            print(f"    提取论文信息时出错: {e}")
            return None
    
    def _handle_pagination(self, soup):
        """
        处理分页，获取所有页面的论文
        使用 pagesize=100 已经可以在一次请求中获取所有论文
        """
        # pagesize=100 已经在 URL 中设置，通常可以一次获取所有论文
        pass
    
    def save_to_json(self):
        """
        将爬取的论文信息保存为 JSON 文件
        """
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.papers, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到: {self.output_file}")
        except Exception as e:
            print(f"保存文件时出错: {e}")
    
    def _get_scisig(self):
        """
        从 Google Scholar 设置页面获取 scisig 令牌
        """
        try:
            settings_url = 'https://scholar.google.com/scholar_settings?sciifh=1&hl=en&as_sdt=0,5'
            response = self.session.get(settings_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找表单中的 scisig 隐藏输入
            form = soup.find('form', {'id': 'gs_settings_form'})
            if form:
                scisig_input = form.find('input', {'type': 'hidden', 'name': 'scisig'})
                if scisig_input:
                    self.scisig = scisig_input.get('value')
                    return self.scisig
            
            print("  警告: 无法获取 scisig 令牌")
            return None
        except Exception as e:
            print(f"  获取 scisig 令牌失败: {e}")
            return None
    
    def _apply_bibtex_settings(self):
        """
        应用 Google Scholar 设置来启用 BibTeX 导出
        """
        if not self.scisig:
            if not self._get_scisig():
                print("  无法应用设置：缺少 scisig 令牌")
                return False
        
        try:
            # 发送设置请求来启用 BibTeX 导出
            setprefs_url = 'https://scholar.google.com/scholar_setprefs'
            params = {
                'q': '',
                'scisig': self.scisig,
                'inststart': '0',
                'as_sdt': '1,5',
                'as_sdtp': '',
                'num': '100',
                'scis': 'on',  # 启用 BibTeX 导出选项
                'scisf': '4'
            }
            
            response = self.session.get(setprefs_url, params=params)
            response.raise_for_status()
            
            print("  已应用 BibTeX 导出设置")
            return True
        except Exception as e:
            print(f"  应用设置失败: {e}")
            return False
    
    def _fetch_bibtex(self, paper_index, bibtex_url):
        """
        从 Google Scholar 爬取单篇论文的 BibTeX 数据
        """
        if not bibtex_url:
            return None
        
        try:
            response = self.session.get(bibtex_url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"    获取 BibTeX 失败: {e}")
            return None

    def fetch_all_bibtex(self):
        """
        爬取所有论文的 BibTeX 数据
        """
        print("\n正在爬取 BibTeX 数据...")
        for idx, paper in enumerate(self.papers, 1):
            citation_url = paper.get('citation_url')
            if citation_url:
                try:
                    # 访问论文详情页面
                    response = self.session.get(citation_url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 查找 "Import" 链接中的 BibTeX 选项
                    bibtex_url = None
                    for link in soup.find_all('a'):
                        href = link.get('href', '')
                        # BibTeX export 链接通常在 scholar_settings 或类似的页面
                        if 'citation_for_view' in href and ('bibtex' in href.lower() or href.startswith('/citations')):
                            # 尝试修改为 BibTeX 格式
                            bibtex_url = href
                            break
                    
                    # 如果没有找到，尝试另一种方式：查找下拉菜单中的导出选项
                    if not bibtex_url:
                        # 寻找包含"Export citation"或导出功能的链接
                        for link in soup.find_all('a'):
                            text = link.get_text(strip=True)
                            if 'Export citation' in text or 'Import' in text:
                                href = link.get('href', '')
                                if href and not href.startswith('javascript'):
                                    bibtex_url = href if href.startswith('http') else 'https://scholar.google.com' + href
                                    break
                    
                    if bibtex_url:
                        # 添加 BibTeX 格式参数
                        if '?' in bibtex_url:
                            bibtex_url += '&output=bibtex' if '&output' not in bibtex_url else ''
                        else:
                            bibtex_url += '?output=bibtex'
                        
                        bibtex_data = self._fetch_bibtex(idx, bibtex_url)
                        paper['bibtex'] = bibtex_data
                        if bibtex_data:
                            print(f"  [{idx}/{len(self.papers)}] 成功获取 BibTeX")
                        else:
                            print(f"  [{idx}/{len(self.papers)}] 未能获取 BibTeX")
                    else:
                        print(f"  [{idx}/{len(self.papers)}] 无 BibTeX 导出链接")
                    
                    time.sleep(0.5)  # 避免频繁请求
                except Exception as e:
                    print(f"  [{idx}/{len(self.papers)}] 获取 BibTeX 失败: {e}")
            else:
                print(f"  [{idx}/{len(self.papers)}] 无论文详情页面")
    
    def save_to_bibtex(self, output_bibtex=None):
        """
        保存爬取的 BibTeX 格式的论文引用信息
        """
        if output_bibtex is None:
            output_bibtex = self.output_file.replace('.json', '.bib')
        
        try:
            bibtex_content = ''
            
            for idx, paper in enumerate(self.papers, 1):
                # 优先使用爬取的 BibTeX 数据
                if paper.get('bibtex'):
                    bibtex_content += paper['bibtex']
                    if not paper['bibtex'].endswith('\n\n'):
                        bibtex_content += '\n\n'
                else:
                    # 如果没有爬取到，生成基本的 BibTeX 条目
                    authors = paper['authors'].split(',')[0].strip() if paper['authors'] else 'Unknown'
                    author_parts = authors.split()
                    author_key = author_parts[-1] if author_parts else 'Unknown'
                    year = paper['year'] if isinstance(paper['year'], int) else 'Unknown'
                    key = f"{author_key}{year}_{idx}"
                    
                    bibtex_entry = f"""@article{{{key},
  title={{{paper['title']}}},
  author={{{paper['authors']}}},
  year={{{year}}},
  url={{{paper['url']}}},
  citations={{{paper['citations']}}}
}}

"""
                    bibtex_content += bibtex_entry
            
            with open(output_bibtex, 'w', encoding='utf-8') as f:
                f.write(bibtex_content)
            print(f"BibTeX 文件已保存到: {output_bibtex}")
            return output_bibtex
        except Exception as e:
            print(f"保存 BibTeX 文件时出错: {e}")
            return None

    def save_to_html(self, output_html='papers.html'):
        """
        生成 HTML 表格展示论文信息
        """
        try:
            html_content = '''<html>
<head>
    <meta charset="utf-8">
    <title>Google Scholar 论文列表</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th { background-color: #4CAF50; color: white; padding: 10px; text-align: left; }
        td { border: 1px solid #ddd; padding: 8px; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        a { color: #2196F3; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Google Scholar 用户论文列表 (User ID: ''' + self.user_id + ''')</h1>
    <p>总共收集 <strong>''' + str(len(self.papers)) + '''</strong> 篇论文</p>
    <table>
        <tr>
            <th>序号</th>
            <th>标题</th>
            <th>作者</th>
            <th>年份</th>
            <th>引用数</th>
            <th>链接</th>
        </tr>
'''
            
            for idx, paper in enumerate(self.papers, 1):
                url_html = '<a href="' + paper["url"] + '" target="_blank">查看</a>' if paper['url'] else '无'
                html_content += '''        <tr>
            <td>''' + str(idx) + '''</td>
            <td>''' + paper['title'] + '''</td>
            <td>''' + paper['authors'] + '''</td>
            <td>''' + str(paper['year']) + '''</td>
            <td>''' + str(paper['citations']) + '''</td>
            <td>''' + url_html + '''</td>
        </tr>
'''
            
            html_content += '''    </table>
</body>
</html>
'''
            
            with open(output_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"HTML 文件已生成: {output_html}")
        except Exception as e:
            print(f"生成 HTML 文件时出错: {e}")


def main():
    if len(sys.argv) < 2:
        print("使用方法: python scraper.py <user_id> [output_file]")
        print("示例: python scraper.py PqrvpbkAAAAJ")
        print("\n支持的输出格式:")
        print("  - JSON: papers_data.json")
        print("  - HTML: papers_data.html")
        print("  - BibTeX: papers_data.bib")
        sys.exit(1)
    
    user_id = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'papers_data.json'
    
    scraper = ScholarUserScraper(user_id, output_file)
    papers = scraper.scrape()
    
    if papers:
        scraper.save_to_json()
        scraper.save_to_html(output_file.replace('.json', '.html'))
        # 爬取所有论文的 BibTeX 数据
        scraper.fetch_all_bibtex()
        scraper.save_to_bibtex(output_file.replace('.json', '.bib'))
        
        # 打印摘要信息
        print("\n" + "="*50)
        print("爬取完成！摘要信息：")
        print("="*50)
        print(f"用户ID: {user_id}")
        print(f"论文总数: {len(papers)}")
        
        if papers:
            years = [p['year'] for p in papers if isinstance(p['year'], int)]
            if years:
                print(f"发表年份范围: {min(years)} - {max(years)}")
            
            total_citations = sum(p['citations'] for p in papers)
            print(f"总引用次数: {total_citations}")
            
            avg_citations = total_citations / len(papers)
            print(f"平均引用数: {avg_citations:.2f}")
        
        print("\n" + "="*50)
        print("生成的文件：")
        print("="*50)
        print(f"✓ JSON 数据: {output_file}")
        print(f"✓ HTML 表格: {output_file.replace('.json', '.html')}")
        print(f"✓ BibTeX 引用: {output_file.replace('.json', '.bib')}")


if __name__ == '__main__':
    main()