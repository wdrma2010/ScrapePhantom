"""CurlCffi 工具 - TLS指纹伪装，绕过基础反爬"""
import time
from .base import BaseTool, ScrapeResult
from ..config import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT


class CurlCffiTool(BaseTool):
    name = "curl_cffi"
    priority = 2
    capabilities = ["tls_fingerprint", "anti_bot", "fast", "static"]
    
    async def fetch(self, url: str, **kwargs) -> ScrapeResult:
        start = time.time()
        timeout = kwargs.get("timeout", DEFAULT_TIMEOUT)
        impersonate = kwargs.get("impersonate", "chrome120")
        
        try:
            from curl_cffi import requests as curl_requests
            
            session = curl_requests.Session()
            response = session.get(
                url,
                impersonate=impersonate,
                timeout=timeout,
                headers=kwargs.get("headers", {"User-Agent": DEFAULT_USER_AGENT}),
            )
            duration = time.time() - start
            
            return ScrapeResult(
                success=response.status_code == 200,
                content=response.text,
                status_code=response.status_code,
                tool_used=self.name,
                duration=duration,
                headers=dict(response.headers) if hasattr(response, 'headers') else {},
                url=str(response.url) if hasattr(response, 'url') else url,
            )
        except ImportError:
            return ScrapeResult(
                success=False,
                tool_used=self.name,
                duration=time.time() - start,
                error="curl_cffi 未安装，请运行: pip install curl_cffi",
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
            from curl_cffi import requests
            return True
        except ImportError:
            return False
