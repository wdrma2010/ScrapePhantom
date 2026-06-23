"""网站特征库 - 预定义已知网站的反爬特征"""
from typing import Dict, Any, Optional


class SiteProfiles:
    """管理已知网站的特征信息"""
    
    PROFILES: Dict[str, Dict[str, Any]] = {
        # === 赔率网站 ===
        "oddschecker.com": {
            "has_cloudflare": True,
            "js_rendered": True,
            "anti_scraping": True,
            "required_capabilities": ["anti_bot", "js_render"],
            "recommended_tool": "nodriver",
        },
        "odds-api.com": {
            "has_cloudflare": False,
            "js_rendered": False,
            "required_capabilities": [],
            "recommended_tool": "requests",
        },
        "bet365.com": {
            "has_cloudflare": True,
            "js_rendered": True,
            "anti_scraping": True,
            "required_capabilities": ["anti_bot", "js_render"],
            "recommended_tool": "nodriver",
        },
        
        # === 足球数据网站 ===
        "rotowire.com": {
            "has_cloudflare": False,
            "js_rendered": False,
            "required_capabilities": [],
            "recommended_tool": "requests",
        },
        "flashscore.com": {
            "has_cloudflare": False,
            "js_rendered": True,
            "anti_scraping": False,
            "required_capabilities": ["js_render"],
            "recommended_tool": "scrapling",
        },
        "sofascore.com": {
            "has_cloudflare": False,
            "js_rendered": True,
            "anti_scraping": False,
            "required_capabilities": ["js_render"],
            "recommended_tool": "scrapling",
        },
        "fbref.com": {
            "has_cloudflare": False,
            "js_rendered": False,
            "required_capabilities": [],
            "recommended_tool": "requests",
        },
        "transfermarkt.com": {
            "has_cloudflare": False,
            "js_rendered": False,
            "anti_scraping": True,
            "required_capabilities": ["tls_fingerprint"],
            "recommended_tool": "curl_cffi",
        },
        "football-data.co.uk": {
            "has_cloudflare": False,
            "js_rendered": False,
            "required_capabilities": [],
            "recommended_tool": "requests",
        },
        "understat.com": {
            "has_cloudflare": False,
            "js_rendered": True,
            "required_capabilities": ["js_render"],
            "recommended_tool": "scrapling",
        },
        
        # === ESPN (免费) ===
        "espn.com": {
            "has_cloudflare": False,
            "js_rendered": False,
            "required_capabilities": [],
            "recommended_tool": "requests",
        },
        "site.api.espn.com": {
            "has_cloudflare": False,
            "js_rendered": False,
            "required_capabilities": [],
            "recommended_tool": "requests",
        },
        
        # === 中国竞彩网站 ===
        "sporttery.cn": {
            "has_cloudflare": False,
            "js_rendered": True,
            "requires_login": False,
            "required_capabilities": ["js_render"],
            "recommended_tool": "nodriver",
        },
        "500.com": {
            "has_cloudflare": False,
            "js_rendered": True,
            "required_capabilities": ["js_render"],
            "recommended_tool": "nodriver",
        },
        "zgzcw.com": {
            "has_cloudflare": False,
            "js_rendered": True,
            "required_capabilities": ["js_render"],
            "recommended_tool": "nodriver",
        },
        "okooo.com": {
            "has_cloudflare": False,
            "js_rendered": True,
            "required_capabilities": ["js_render"],
            "recommended_tool": "nodriver",
        },
        
        # === 其他 ===
        "github.com": {
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
