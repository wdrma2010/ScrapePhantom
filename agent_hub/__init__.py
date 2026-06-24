"""
Agent Hub - 智能检测与自动配置
自动检测 Agent 内置抓取工具，生成对应的技能配置
"""
from .detector import detect_agent, detect_fetch_tools
from .configurator import auto_configure

__all__ = ["detect_agent", "detect_fetch_tools", "auto_configure"]
