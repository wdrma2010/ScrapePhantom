"""网站特征库 - 预定义已知网站的反爬特征"""
from typing import Dict, Any, Optional


class SiteProfiles:
    """管理已知网站的特征信息"""
    
    PROFILES: Dict[str, Dict[str, Any]] = {
        # === 通用网站 ===
        "github.com": {
            "has_cloudflare": False,
            "js_rendered": False,
            "required_capabilities": [],
            "recommended_tool": "requests",
        },
        "stackoverflow.com": {
            "has_cloudflare": False,
            "js_rendered": False,
            "required_capabilities": [],
            "recommended_tool": "requests",
        },
        "wikipedia.org": {
            "has_cloudflare": False,
            "js_rendered": False,
            "required_capabilities": [],
            "recommended_tool": "requests",
        },
        
        # === Cloudflare 保护站点 ===
        "cloudflare.com": {
            "has_cloudflare": True,
            "js_rendered": True,
            "anti_scraping": True,
            "required_capabilities": ["anti_bot", "js_render"],
            "recommended_tool": "nodriver",
        },
        
        # === 数据 API ===
        "api.github.com": {
            "has_cloudflare": False,
            "js_rendered": False,
            "required_capabilities": [],
            "recommended_tool": "requests",
        },
    }
    
    @classmethod
    def get_profile(cls, url: str) -> Optional[Dict[str, Any]]:
        """根据 URL 获取网站特征"""
        url_lower = url.lower()
        for domain, profile in cls.PROFILES.items():
            if domain in url_lower:
                return profile.copy()
        return None
    
    @classmethod
    def add_profile(cls, domain: str, profile: Dict[str, Any]):
        """添加新的网站特征"""
        cls.PROFILES[domain] = profile
    
    @classmethod
    def get_recommended_tool(cls, url: str) -> Optional[str]:
        """获取推荐工具名"""
        profile = cls.get_profile(url)
        if profile:
            return profile.get("recommended_tool")
        return None
