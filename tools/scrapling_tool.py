"""Scrapling 工具 - 自适应爬虫，页面变化容忍"""
import time
from .base import BaseTool, ScrapeResult
from ..config import DEFAULT_TIMEOUT


class ScraplingTool(BaseTool):
    name = "scrapling"
    priority = 3
    capabilities = [
        "adaptive", "anti_bot", "js_render", "stealth",
        "auto_relocate", "cloudflare"
    ]
    
    async def fetch(self, url: str, **kwargs) -> ScrapeResult:
        start = time.time()
        headless = kwargs.get("headless", True)
        
        try:
            from scrapling.fetchers import Fetcher, StealthyFetcher
            
            use_stealth = kwargs.get("stealth", True)
            
            if use_stealth:
                page = StealthyFetcher.fetch(url, headless=headless, network_idle=True)
            else:
                page = Fetcher().get(url)
            
            content = page.html_content if hasattr(page, 'html_content') else str(page)
            duration = time.time() - start
            
            return ScrapeResult(
                success=bool(content),
                content=content,
                tool_used=self.name,
                duration=duration,
                url=url,
            )
        except ImportError:
            return ScrapeResult(
                success=False,
                tool_used=self.name,
                duration=time.time() - start,
                error="scrapling 未安装，请运行: pip install scrapling[all]",
                url=url,
            )
        except Exception as e:
            return ScrapeResult(
                success=False,
                tool_used=self.name,
                duration=time.time() - start,
                error=str(e),
                url=url,
            )
    
    async def check_availability(self) -> bool:
        try:
            from scrapling.fetchers import Fetcher
            return True
        except ImportError:
            return False
