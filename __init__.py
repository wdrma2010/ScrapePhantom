"""
ScrapePhantom - 智能爬虫调度框架
自动选择最优爬虫工具，绕过反爬保护

内置全部依赖，无需额外安装：
  pip install scrapephantom  即可使用
"""
# 优先加载 vendor 路径
import smart_scraper.vendor  # noqa: F401

from .core.scheduler import SmartScheduler
from .tools.base import ScrapeResult

__version__ = "1.2.0"
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
