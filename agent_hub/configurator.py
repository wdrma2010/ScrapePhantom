"""
自动配置器 - 根据检测结果生成技能配置
"""
import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from .detector import detect_agent, detect_fetch_tools, is_scrapephantom_available


# 技能配置模板
SKILL_TEMPLATE = """---
name: scrapephantom
description: 智能爬虫工具，当内置抓取工具失败、超时或需要绕过反爬保护时自动触发。
---

# ScrapePhantom - 智能抓取降级

## 触发条件（满足任一即触发）

1. 内置抓取工具返回错误或失败
2. 抓取超时
3. 内容不完整或被截断
4. HTTP 状态码异常（403、429、503等）
5. 需要绕过反爬保护（Cloudflare、DataDome等）
6. 需要渲染 JavaScript 动态内容
7. 返回内容为空或格式异常

## 调用方式

```python
from smart_scraper import scrape

result = scrape("https://example.com")
if result.success:
    print(result.content)
```

## 工具选择逻辑

ScrapePhantom 会并行启动 4 个工具，谁先成功用谁：
- requests: 静态页面
- curl_cffi: TLS指纹检测
- nodriver: Cloudflare/需登录
- scrapling: JS渲染/页面改版

## 重要规则

**不要直接输出"抓取失败"，必须先尝试 ScrapePhantom。**
"""

# MCP 配置模板（用于 Claude/Cursor）
MCP_CONFIG_TEMPLATE = {
    "scrapephantom": {
        "command": "python",
        "args": ["-m", "smart_scraper.agent_hub.mcp_server"],
        "env": {}
    }
}


def auto_configure(force: bool = False) -> Dict[str, Any]:
    """
    自动配置 ScrapePhantom 技能
    
    Args:
        force: 强制重新配置
    
    Returns:
        配置结果
    """
    result = {
        "success": False,
        "agent": None,
        "config_path": None,
        "message": "",
    }
    
    # 检查 ScrapePhantom 是否可用
    if not is_scrapephantom_available():
        result["message"] = "ScrapePhantom 未安装，请先运行: pip install -e ."
        return result
    
    # 检测 Agent
    agent = detect_agent()
    result["agent"] = agent.name
    
    # 根据 Agent 类型配置
    if agent.type == "opencode":
        return _configure_opencode(agent, force)
    elif agent.type in ["claude", "cursor"]:
        return _configure_mcp(agent, force)
    else:
        return _configure_generic(agent, force)


def _configure_opencode(agent, force: bool) -> Dict[str, Any]:
    """配置 OpenCode 技能"""
    result = {
        "success": False,
        "agent": "opencode",
        "config_path": None,
        "message": "",
    }
    
    skill_dir = Path(agent.config_path) / "skills" / "scrapephantom"
    skill_file = skill_dir / "SKILL.md"
    
    # 检查是否已配置
    if skill_file.exists() and not force:
        result["success"] = True
        result["config_path"] = str(skill_file)
        result["message"] = "已配置，跳过（使用 force=True 强制重新配置）"
        return result
    
    # 创建目录
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    # 写入配置
    skill_file.write_text(SKILL_TEMPLATE, encoding="utf-8")
    
    result["success"] = True
    result["config_path"] = str(skill_file)
    result["message"] = f"已配置到: {skill_file}"
    return result


def _configure_mcp(agent, force: bool) -> Dict[str, Any]:
    """配置 MCP（用于 Claude/Cursor）"""
    result = {
        "success": False,
        "agent": agent.name,
        "config_path": None,
        "message": "",
    }
    
    # MCP 配置文件路径
    if agent.type == "claude":
        config_file = Path(agent.config_path) / "claude_desktop_config.json"
    else:
        config_file = Path(agent.config_path) / "mcp.json"
    
    result["config_path"] = str(config_file)
    
    # 读取现有配置
    existing_config = {}
    if config_file.exists():
        try:
            existing_config = json.loads(config_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    
    # 检查是否已配置
    if "mcpServers" in existing_config and "scrapephantom" in existing_config["mcpServers"]:
        if not force:
            result["success"] = True
            result["message"] = "已配置，跳过"
            return result
    
    # 添加配置
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"]["scrapephantom"] = MCP_CONFIG_TEMPLATE["scrapephantom"]
    
    # 写入配置
    config_file.write_text(json.dumps(existing_config, indent=2), encoding="utf-8")
    
    result["success"] = True
    result["message"] = f"MCP 配置已写入: {config_file}"
    return result


def _configure_generic(agent, force: bool) -> Dict[str, Any]:
    """通用配置（输出使用说明）"""
    result = {
        "success": True,
        "agent": agent.name,
        "config_path": None,
        "message": """
未知 Agent 类型，请手动集成：

1. 确保 ScrapePhantom 已安装: pip install -e .

2. 在你的 Agent 工具调用逻辑中加入降级规则:

```python
from smart_scraper import scrape

def fetch_with_fallback(url):
    try:
        return 内置工具.fetch(url)
    except:
        result = scrape(url)
        return result.content if result.success else None
```

3. 触发条件:
   - 内置工具失败/超时
   - 需要绕过反爬保护
   - 需要 JS 渲染
""",
    }
    return result


def get_status() -> Dict[str, Any]:
    """获取当前配置状态"""
    agent = detect_agent()
    tools = detect_fetch_tools()
    
    status = {
        "agent": agent.name,
        "agent_type": agent.type,
        "config_path": agent.config_path,
        "scrapephantom_installed": is_scrapephantom_available(),
        "builtin_tools": [t.name for t in tools],
        "configured": False,
        "config_file": None,
    }
    
    # 检查是否已配置
    if agent.type == "opencode":
        skill_file = Path(agent.config_path) / "skills" / "scrapephantom" / "SKILL.md"
        status["configured"] = skill_file.exists()
        status["config_file"] = str(skill_file) if skill_file.exists() else None
    elif agent.type in ["claude", "cursor"]:
        if agent.type == "claude":
            config_file = Path(agent.config_path) / "claude_desktop_config.json"
        else:
            config_file = Path(agent.config_path) / "mcp.json"
        
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text(encoding="utf-8"))
                status["configured"] = "scrapephantom" in config.get("mcpServers", {})
                status["config_file"] = str(config_file)
            except:
                pass
    
    return status


if __name__ == "__main__":
    import json
    print("=== 自动配置 ===")
    result = auto_configure()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n=== 配置状态 ===")
    status = get_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
