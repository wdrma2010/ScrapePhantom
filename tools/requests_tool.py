"""Requests 工具 - 最轻量，适合静态页面"""
import time
import requests as req
from .base import BaseTool, ScrapeResult
from ..config import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT


class RequestsTool(BaseTool):
    name = "requests"
    priority = 1
    capabilities = ["fast", "lightweight", "static"]
    
    async def fetch(self, url: str, **kwargs) -> ScrapeResult:
        start = time.time()
        timeout = kwargs.get("timeout", DEFAULT_TIMEOUT)
        headers = kwargs.get("headers", {"User-Agent": DEFAULT_USER_AGENT})
        
        try:
            response = req.get(url, timeout=timeout, headers=headers, allow_redirects=True)
            duration = time.time() - start
            
            return ScrapeResult(
                success=response.status_code == 200,
                content=response.text,
                status_code=response.status_code,
                tool_used=self.name,
                duration=duration,
                headers=dict(response.headers),
                url=response.url,
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
            import requests
            return True
        except ImportError:
            return False
