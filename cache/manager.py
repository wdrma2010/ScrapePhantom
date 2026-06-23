"""缓存管理器 - 减少重复请求"""
import os
import json
import time
import hashlib
from typing import Optional
from ..tools.base import ScrapeResult
from ..config import CACHE_DIR, CACHE_TTL


class CacheManager:
    """基于文件系统的简单缓存"""
    
    def __init__(self, cache_dir: str = CACHE_DIR, ttl: int = CACHE_TTL):
        self.cache_dir = cache_dir
        self.ttl = ttl
        os.makedirs(cache_dir, exist_ok=True)
    
    def _key(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()
    
    def _path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, url: str) -> Optional[ScrapeResult]:
        key = self._key(url)
        path = self._path(key)
        
        if not os.path.exists(path):
            return None
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if time.time() - data.get("cached_at", 0) > self.ttl:
                os.remove(path)
                return None
            
            return ScrapeResult(
                success=data["success"],
                content=data.get("content", ""),
                status_code=data.get("status_code", 0),
                tool_used=data.get("tool_used", "cache"),
                duration=data.get("duration", 0),
                error=data.get("error", ""),
                url=data.get("url", url),
            )
        except Exception:
            return None
    
    def set(self, url: str, result: ScrapeResult):
        key = self._key(url)
        path = self._path(key)
        
        data = {
            "success": result.success,
            "content": result.content,
            "status_code": result.status_code,
            "tool_used": result.tool_used,
            "duration": result.duration,
            "error": result.error,
            "url": result.url,
            "cached_at": time.time(),
        }
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception:
            pass
    
    def clear(self):
        for f in os.listdir(self.cache_dir):
            if f.endswith(".json"):
                os.remove(os.path.join(self.cache_dir, f))
    
    def stats(self) -> dict:
        files = [f for f in os.listdir(self.cache_dir) if f.endswith(".json")]
        total_size = sum(
            os.path.getsize(os.path.join(self.cache_dir, f))
            for f in files
        )
        return {
            "entries": len(files),
            "total_size_kb": round(total_size / 1024, 2),
        }
