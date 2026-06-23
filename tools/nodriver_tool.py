"""Nodriver 工具 - 终极反爬武器，直接驱动Chrome"""
import time
from .base import BaseTool, ScrapeResult
from ..config import DEFAULT_TIMEOUT


class NodriverTool(BaseTool):
    name = "nodriver"
    priority = 4
    capabilities = [
        "anti_bot", "js_render", "login", "cloudflare",
        "datadome", "browser", "full_render"
    ]
    
    async def fetch(self, url: str, **kwargs) -> ScrapeResult:
        start = time.time()
        wait = kwargs.get("wait", 3)
        headless = kwargs.get("headless", True)
        
        try:
            import nodriver as uc
            
            browser = await uc.start(headless=headless)
            page = await browser.get(url)
            await page.sleep(wait)
            
            content = await page.get_content()
            await browser.stop()
            
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
                error="nodriver 未安装，请运行: pip install nodriver",
                url=url,
            )
        except Exception as e:
            try:
                await browser.stop()
            except Exception:
                pass
            return ScrapeResult(
                success=False,
                tool_used=self.name,
                duration=time.time() - start,
                error=str(e),
                url=url,
            )
    
    async def check_availability(self) -> bool:
        try:
            import nodriver
            return True
        except ImportError:
            return False
