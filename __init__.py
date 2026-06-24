"""
ScrapePhantom - 智能爬虫调度框架
自动选择最优爬虫工具，绕过反爬保护
"""
import asyncio
from .core.scheduler import SmartScheduler
from .tools.base import ScrapeResult

__version__ = "1.2.0"
__all__ = ["SmartScheduler", "ScrapeResult", "smart_scrape", "scrape"]

_scheduler = None

def get_scheduler() -> SmartScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = SmartScheduler()
    return _scheduler

async def smart_scrape(url: str, **kwargs) -> ScrapeResult:
    """异步抓取接口"""
    scheduler = get_scheduler()
    return await scheduler.scrape(url, **kwargs)

def scrape(url: str, **kwargs) -> ScrapeResult:
    """
    同步抓取接口（推荐）
    
    用法:
        from smart_scraper import scrape
        result = scrape("https://example.com")
        if result.success:
            print(result.content)
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, smart_scrape(url, **kwargs))
                return future.result(timeout=kwargs.get('timeout', 30))
        else:
            return loop.run_until_complete(smart_scrape(url, **kwargs))
    except RuntimeError:
        return asyncio.run(smart_scrape(url, **kwargs))
