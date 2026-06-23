"""代理管理器"""
import random
from typing import List, Optional
from ..config import PROXY_ENABLED, PROXY_LIST


class ProxyManager:
    def __init__(self, proxies: Optional[List[str]] = None):
        self.proxies = proxies or PROXY_LIST
        self.enabled = PROXY_ENABLED and bool(self.proxies)
    
    def get_proxy(self) -> Optional[str]:
        if not self.enabled or not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def add_proxy(self, proxy: str):
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.enabled = True
    
    def remove_proxy(self, proxy: str):
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            if not self.proxies:
                self.enabled = False
    
    def stats(self) -> dict:
        return {
            "enabled": self.enabled,
            "count": len(self.proxies),
        }
