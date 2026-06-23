"""降级策略引擎 - 主工具失败时自动切换"""
from typing import List, Optional
from ..tools.base import BaseTool, ScrapeResult
import logging

logger = logging.getLogger(__name__)


class FallbackEngine:
    """降级策略：按优先级依次尝试工具"""
    
    def __init__(self, tools: List[BaseTool]):
        self.tools = sorted(tools, key=lambda t: t.priority, reverse=True)
    
    async def execute(
        self,
        url: str,
        preferred_tool: Optional[str] = None,
        skip_tools: Optional[List[str]] = None,
        **kwargs
    ) -> ScrapeResult:
        skip_tools = skip_tools or []
        ordered = self._get_ordered_tools(preferred_tool, skip_tools)
        
        last_error = None
        for tool in ordered:
            logger.info(f"尝试工具: {tool.name}")
            result = await tool.fetch(url, **kwargs)
            
            if result.success:
                logger.info(f"成功: {tool.name} ({result.duration:.2f}s)")
                return result
            
            last_error = result.error
            logger.warning(f"失败: {tool.name} - {result.error}")
        
        return ScrapeResult(
            success=False,
            error=f"所有工具均失败。最后错误: {last_error}",
            url=url,
        )
    
    def _get_ordered_tools(self, preferred: Optional[str], skip: List[str]) -> List[BaseTool]:
        available = [t for t in self.tools if t.name not in skip]
        
        if preferred:
            preferred_tools = [t for t in available if t.name == preferred]
            other_tools = [t for t in available if t.name != preferred]
            return preferred_tools + other_tools
        
        return available
