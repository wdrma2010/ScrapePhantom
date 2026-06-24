"""降级策略引擎 - 主工具失败时自动切换"""
import asyncio
from typing import List, Optional
from ..tools.base import BaseTool, ScrapeResult
import logging

logger = logging.getLogger(__name__)


class FallbackEngine:
    """降级策略：并行竞争，谁先成功用谁"""
    
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
        
        if not ordered:
            return ScrapeResult(
                success=False,
                error="无可用工具",
                url=url,
            )
        
        # 并行启动所有工具
        logger.info(f"并行启动 {len(ordered)} 个工具: {[t.name for t in ordered]}")
        
        tasks = []
        for tool in ordered:
            task = asyncio.create_task(self._fetch_with_log(tool, url, **kwargs))
            tasks.append((tool.name, task))
        
        # 等待第一个成功的结果
        done = set()
        while tasks:
            # 等待任意一个任务完成
            pending = [(name, task) for name, task in tasks if name not in done]
            if not pending:
                break
            
            done_tasks, _ = await asyncio.wait(
                [task for _, task in pending],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # 检查完成的任务
            for name, task in pending:
                if task.done() and name not in done:
                    done.add(name)
                    try:
                        result = task.result()
                        if result.success:
                            # 取消其他任务
                            for _, other_task in tasks:
                                if not other_task.done():
                                    other_task.cancel()
                            logger.info(f"成功: {name} ({result.duration:.2f}s)")
                            return result
                    except Exception as e:
                        logger.warning(f"失败: {name} - {e}")
        
        return ScrapeResult(
            success=False,
            error=f"所有 {len(ordered)} 个工具均失败",
            url=url,
        )
    
    async def _fetch_with_log(self, tool: BaseTool, url: str, **kwargs) -> ScrapeResult:
        try:
            result = await tool.fetch(url, **kwargs)
            return result
        except Exception as e:
            return ScrapeResult(
                success=False,
                tool_used=tool.name,
                error=str(e),
                url=url,
            )
    
    def _get_ordered_tools(self, preferred: Optional[str], skip: List[str]) -> List[BaseTool]:
        available = [t for t in self.tools if t.name not in skip]
        
        if preferred:
            preferred_tools = [t for t in available if t.name == preferred]
            other_tools = [t for t in available if t.name != preferred]
            return preferred_tools + other_tools
        
        return available
