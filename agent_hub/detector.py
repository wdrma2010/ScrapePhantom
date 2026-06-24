"""
Agent 检测器 - 识别内置抓取工具和 Agent 类型
"""
import os
import sys
import importlib
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class FetchToolInfo:
    """抓取工具信息"""
    name: str
    module: str
    version: str = ""
    is_async: bool = False
    capabilities: List[str] = field(default_factory=list)


@dataclass
class AgentInfo:
    """Agent 信息"""
    name: str
    type: str  # opencode, claude, gpt, custom
    config_path: str = ""
    has_skill_system: bool = False
    has_mcp: bool = False
    builtin_fetch_tools: List[FetchToolInfo] = field(default_factory=list)


# 常见抓取工具定义
FETCH_TOOLS = {
    "requests": {
        "module": "requests",
        "is_async": False,
        "capabilities": ["http", "static"],
    },
    "httpx": {
        "module": "httpx",
        "is_async": True,
        "capabilities": ["http", "static", "http2"],
    },
    "aiohttp": {
        "module": "aiohttp",
        "is_async": True,
        "capabilities": ["http", "static", "websocket"],
    },
    "curl_cffi": {
        "module": "curl_cffi",
        "is_async": True,
        "capabilities": ["http", "tls_fingerprint", "anti_bot"],
    },
    "playwright": {
        "module": "playwright",
        "is_async": True,
        "capabilities": ["browser", "js_render", "anti_bot"],
    },
    "selenium": {
        "module": "selenium",
        "is_async": False,
        "capabilities": ["browser", "js_render"],
    },
    "nodriver": {
        "module": "nodriver",
        "is_async": True,
        "capabilities": ["browser", "js_render", "anti_bot", "cloudflare"],
    },
    "axios": {
        "module": "axios",
        "is_async": True,
        "capabilities": ["http", "static"],
    },
    "got": {
        "module": "got",
        "is_async": True,
        "capabilities": ["http", "static"],
    },
    "node-fetch": {
        "module": "node-fetch",
        "is_async": True,
        "capabilities": ["http", "static"],
    },
}


def detect_fetch_tools() -> List[FetchToolInfo]:
    """检测当前环境中可用的抓取工具"""
    found_tools = []
    
    for tool_name, tool_info in FETCH_TOOLS.items():
        try:
            module = importlib.import_module(tool_info["module"])
            version = getattr(module, "__version__", "")
            found_tools.append(FetchToolInfo(
                name=tool_name,
                module=tool_info["module"],
                version=version,
                is_async=tool_info["is_async"],
                capabilities=tool_info["capabilities"],
            ))
        except ImportError:
            continue
    
    return found_tools


def detect_agent() -> AgentInfo:
    """检测当前 Agent 类型"""
    # 检测 OpenCode
    if os.path.exists(os.path.expanduser("~/.config/opencode")):
        return AgentInfo(
            name="opencode",
            type="opencode",
            config_path=os.path.expanduser("~/.config/opencode"),
            has_skill_system=True,
        )
    
    # 检测 Claude Desktop
    claude_paths = [
        os.path.expanduser("~/Library/Application Support/Claude"),
        os.path.expanduser("~/.claude"),
    ]
    for path in claude_paths:
        if os.path.exists(path):
            return AgentInfo(
                name="claude",
                type="claude",
                config_path=path,
                has_mcp=True,
            )
    
    # 检测 Cursor
    if os.path.exists(os.path.expanduser("~/.cursor")):
        return AgentInfo(
            name="cursor",
            type="cursor",
            config_path=os.path.expanduser("~/.cursor"),
            has_mcp=True,
        )
    
    # 检测 VS Code (GitHub Copilot)
    vscode_paths = [
        os.path.expanduser("~/.vscode"),
        os.path.expanduser("~/.vscode-insiders"),
    ]
    for path in vscode_paths:
        if os.path.exists(path):
            return AgentInfo(
                name="vscode",
                type="vscode",
                config_path=path,
            )
    
    # 未知 Agent
    return AgentInfo(
        name="unknown",
        type="custom",
    )


def get_agent_info() -> Dict[str, Any]:
    """获取完整的 Agent 和工具信息"""
    agent = detect_agent()
    tools = detect_fetch_tools()
    
    return {
        "agent": {
            "name": agent.name,
            "type": agent.type,
            "config_path": agent.config_path,
            "has_skill_system": agent.has_skill_system,
            "has_mcp": agent.has_mcp,
        },
        "fetch_tools": [
            {
                "name": t.name,
                "version": t.version,
                "is_async": t.is_async,
                "capabilities": t.capabilities,
            }
            for t in tools
        ],
        "scrapephantom_available": is_scrapephantom_available(),
    }


def is_scrapephantom_available() -> bool:
    """检查 ScrapePhantom 是否可用"""
    try:
        from smart_scraper import scrape
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    import json
    info = get_agent_info()
    print(json.dumps(info, indent=2, ensure_ascii=False))
