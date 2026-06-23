"""网站特征分析器 - 实时探测目标网站"""
import re
from typing import Dict, Any, Optional
from ..profiles.site_profiles import SiteProfiles


class SiteAnalyzer:
    """分析目标网站，判断需要什么工具"""
    
    CLOUDFLARE_MARKERS = ["cf-ray", "cf-cache-status", "cloudflare"]
    DATADOME_MARKERS = ["datadome", "dd_s"]
    IMPERVA_MARKERS = ["imperva", "incap_ses"]
    JS_INDICATORS = [
        "just a moment",
        "checking your browser",
        "verify you are human",
        "enable javascript",
        "noscript",
    ]
    
    async def analyze(self, url: str, response_headers: Optional[Dict] = None, response_body: Optional[str] = None) -> Dict[str, Any]:
        profile = {
            "url": url,
            "has_cloudflare": False,
            "has_datadome": False,
            "has_impera": False,
            "requires_login": False,
            "js_rendered": False,
            "anti_scraping": False,
            "frequently_changes": False,
            "required_capabilities": [],
            "recommended_tool": None,
            "confidence": 0.0,
        }
        
        known = SiteProfiles.get_profile(url)
        if known:
            profile.update(known)
            profile["confidence"] = 0.9
            return profile
        
        if response_headers:
            self._analyze_headers(profile, response_headers)
        if response_body:
            self._analyze_body(profile, response_body)
        
        if profile["has_cloudflare"] or profile["has_datadome"] or profile["has_impera"]:
            profile["anti_scraping"] = True
            if "anti_bot" not in profile["required_capabilities"]:
                profile["required_capabilities"].append("anti_bot")
        
        if profile["js_rendered"] and "js_render" not in profile["required_capabilities"]:
            profile["required_capabilities"].append("js_render")
        
        profile["recommended_tool"] = self._suggest_tool(profile)
        profile["confidence"] = 0.5
        
        return profile
    
    def _analyze_headers(self, profile: Dict, headers: Dict):
        headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
        
        server = headers_lower.get("server", "")
        for marker in self.CLOUDFLARE_MARKERS:
            if marker in server or marker in str(headers_lower):
                profile["has_cloudflare"] = True
                break
        
        set_cookie = headers_lower.get("set-cookie", "")
        for marker in self.DATADOME_MARKERS:
            if marker in set_cookie:
                profile["has_datadome"] = True
                break
        
        for marker in self.IMPERVA_MARKERS:
            if marker in str(headers_lower):
                profile["has_impera"] = True
                break
        
        content_type = headers_lower.get("content-type", "")
        if "text/html" not in content_type and "json" in content_type:
            profile["js_rendered"] = False
    
    def _analyze_body(self, profile: Dict, body: str):
        body_lower = body.lower()[:5000]
        for indicator in self.JS_INDICATORS:
            if indicator in body_lower:
                profile["js_rendered"] = True
                break
        
        if "window.__INITIAL_STATE__" in body or "window.__NEXT_DATA__" in body:
            profile["js_rendered"] = True
        
        if '<div id="__next">' in body or '<div id="app">' in body:
            profile["js_rendered"] = True
    
    def _suggest_tool(self, profile: Dict) -> str:
        if profile["has_cloudflare"] or profile["has_datadome"] or profile["has_impera"]:
            return "nodriver"
        if profile["js_rendered"]:
            if profile.get("frequently_changes"):
                return "scrapling"
            return "nodriver"
        if profile["anti_scraping"]:
            return "curl_cffi"
        return "requests"
