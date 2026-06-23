"""
SmartScraper - 智能爬虫调度框架
根据任务复杂度自动选择最优爬虫工具
"""
from .core.scheduler import SmartScheduler
from .tools.base import ScrapeResult

__version__ = "1.0.0"
__all__ = ["SmartScheduler", "ScrapeResult", "smart_scrape"]

_scheduler = None

def get_scheduler() -> SmartScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = SmartScheduler()
    return _scheduler

async def smart_scrape(url: str, **kwargs) -> ScrapeResult:
    scheduler = get_scheduler()
    return await scheduler.scrape(url, **kwargs)
