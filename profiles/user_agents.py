"""User-Agent 池 - 随机选择真实 UA"""
import random
from typing import List


class UserAgentPool:
    """真实 User-Agent 池"""
    
    CHROME: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    ]
    
    FIREFOX: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
    ]
    
    SAFARI: List[str] = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    ]
    
    EDGE: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    ]
    
    ALL: List[str] = CHROME + FIREFOX + SAFARI + EDGE
    
    @classmethod
    def random(cls, browser: str = "all") -> str:
        """随机获取一个 UA"""
        pool_map = {
            "chrome": cls.CHROME,
            "firefox": cls.FIREFOX,
            "safari": cls.SAFARI,
            "edge": cls.EDGE,
            "all": cls.ALL,
        }
        pool = pool_map.get(browser.lower(), cls.ALL)
        return random.choice(pool)
