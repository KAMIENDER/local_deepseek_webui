import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import quote_plus

class SearchResult:
    def __init__(self, title: str, snippet: str, link: str):
        self.title = title
        self.snippet = snippet
        self.link = link

class WebSearch:
    @staticmethod
    def search_duckduckgo(query: str, num_results: int = 5) -> List[SearchResult]:
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for result in soup.select('.result')[:num_results]:
                title = result.select_one('.result__title').get_text(strip=True)
                snippet = result.select_one('.result__snippet').get_text(strip=True)
                link = result.select_one('.result__url').get('href')
                
                results.append(SearchResult(title, snippet, link))
            
            return results
        except Exception as e:
            print(f"搜索出错: {str(e)}")
            return []
    
    @staticmethod
    def format_results(results: List[SearchResult]) -> str:
        formatted = "搜索结果:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.title}\n"
            formatted += f"   {result.snippet}\n"
            formatted += f"   链接: {result.link}\n\n"
        return formatted