"""智能调度器 - 核心调度逻辑"""
import logging
from typing import Optional, Dict, Any, List
from ..tools.base import BaseTool, ScrapeResult
from ..tools.requests_tool import RequestsTool
from ..tools.curl_cffi_tool import CurlCffiTool
from ..tools.nodriver_tool import NodriverTool
from ..tools.scrapling_tool import ScraplingTool
from .analyzer import SiteAnalyzer
from .fallback import FallbackEngine
from ..cache.manager import CacheManager

logger = logging.getLogger(__name__)


class SmartScheduler:
    """智能调度器：分析任务 → 选择工具 → 降级兜底"""
    
    def __init__(self):
        self.tools: List[BaseTool] = [
            RequestsTool(),
            CurlCffiTool(),
            ScraplingTool(),
            NodriverTool(),
        ]
        self.analyzer = SiteAnalyzer()
        self.fallback = FallbackEngine(self.tools)
        self.cache = CacheManager()
        self.task_history: Dict[str, str] = {}
    
    async def scrape(self, url: str, **kwargs) -> ScrapeResult:
        use_cache = kwargs.pop("use_cache", True)
        force_tool = kwargs.pop("force_tool", None)
        
        if use_cache:
            cached = self.cache.get(url)
            if cached:
                logger.info(f"缓存命中: {url}")
                return cached
        
        if force_tool:
            tool = self._get_tool(force_tool)
            if tool:
                result = await tool.fetch(url, **kwargs)
                if result.success:
                    if use_cache:
                        self.cache.set(url, result)
                    self.task_history[url] = tool.name
                    return result
        
        cached_tool = self.task_history.get(url)
        if cached_tool and not force_tool:
            tool = self._get_tool(cached_tool)
            if tool:
                result = await tool.fetch(url, **kwargs)
                if result.success:
                    if use_cache:
                        self.cache.set(url, result)
                    return result
        
        profile = await self.analyzer.analyze(url)
        recommended = profile.get("recommended_tool")
        
        logger.info(f"分析结果: {url} → 推荐工具: {recommended}")
        
        result = await self.fallback.execute(
            url,
            preferred_tool=recommended,
            **kwargs
        )
        
        if result.success:
            self.task_history[url] = result.tool_used
            if use_cache:
                self.cache.set(url, result)
        
        return result
    
    def _get_tool(self, name: str) -> Optional[BaseTool]:
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取所有可用工具及其状态"""
        result = []
        for tool in self.tools:
            available = await tool.check_availability()
            result.append({
                "name": tool.name,
                "priority": tool.priority,
                "capabilities": tool.capabilities,
                "available": available,
            })
        return result
    
    def register_tool(self, tool: BaseTool):
        """注册自定义工具"""
        self.tools.append(tool)
        self.tools.sort(key=lambda t: t.priority, reverse=True)
        self.fallback = FallbackEngine(self.tools)
