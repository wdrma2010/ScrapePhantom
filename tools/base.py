"""工具基类 - 统一接口"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time


@dataclass
class ScrapeResult:
    """统一返回结果"""
    success: bool
    content: str = ""
    status_code: int = 0
    tool_used: str = ""
    duration: float = 0.0
    error: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    url: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """所有爬虫工具的统一基类"""
    
    name: str = "base"
    priority: int = 0
    capabilities: List[str] = []
    is_available: Optional[bool] = None
    
    @abstractmethod
    async def fetch(self, url: str, **kwargs) -> ScrapeResult:
        """抓取页面，返回统一结果"""
        pass
    
    async def check_availability(self) -> bool:
        """检查工具是否可用（依赖是否安装）"""
        return True
    
    def matches_task(self, task_requirements: Dict[str, Any]) -> float:
        """
        返回工具与任务的匹配度分数 0.0 ~ 1.0
        分数越高越适合该任务
        """
        required = task_requirements.get("required_capabilities", [])
        if not required:
            return 0.5  # 无特殊要求，给基础分
        
        matched = sum(1 for cap in required if cap in self.capabilities)
        return matched / len(required) if required else 0.5
    
    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} priority={self.priority}>"
