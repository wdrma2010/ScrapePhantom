# ScrapePhantom 幽灵爬虫

> 智能爬虫调度框架 - 根据任务复杂度自动选择最优爬虫工具，绕过反爬保护

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 项目简介

**ScrapePhantom**（幽灵爬虫）是一个智能爬虫调度框架，核心解决一个痛点：

> **面对不同网站的反爬策略，手动切换爬虫工具太麻烦。**

ScrapePhantom 会自动分析目标网站特征（Cloudflare？DataDome？JS渲染？），然后：
1. 选择最优的爬虫工具
2. 执行抓取
3. 失败时自动降级到下一工具

**一行代码，搞定所有网站。**

---

## 核心功能

### 1. 智能工具调度

```
任务进入 → 分析网站特征 → 选择最优工具 → 执行 → 失败自动降级
```

内置 4 种爬虫工具，按场景自动选择：

| 工具 | 适用场景 | 安装命令 |
|------|---------|---------|
| **requests** | 静态页面、API接口 | `pip install requests` |
| **curl_cffi** | TLS指纹检测网站 | `pip install curl_cffi` |
| **scrapling** | JS渲染、页面频繁改版 | `pip install scrapling[all]` |
| **nodriver** | Cloudflare、DataDome、需登录 | `pip install nodriver` |

### 2. 反检测绕过

| 反爬系统 | 绕过方案 |
|---------|---------|
| Cloudflare | nodriver（真实浏览器引擎） |
| DataDome | nodriver |
| Imperva/Incapsula | nodriver |
| TLS指纹检测 | curl_cffi（伪装Chrome握手） |
| 行为检测 | 随机UA + 请求间隔 |

### 3. 降级策略

主工具失败时，自动切换下一工具，无需人工干预：

```python
# 自动尝试: nodriver → scrapling → curl_cffi → requests
result = await smart_scrape("https://protected-site.com")
```

### 4. 缓存管理

- 基于文件系统的本地缓存
- 可配置 TTL（默认24小时）
- 支持禁用缓存

### 5. 网站特征库

预定义 17+ 已知网站的最优抓取策略：

```python
from smart_scraper.profiles.site_profiles import SiteProfiles

# 自动识别网站并推荐工具
profile = SiteProfiles.get_profile("https://www.bet365.com")
# → {"has_cloudflare": True, "recommended_tool": "nodriver", ...}
```

---

## 快速开始

### 安装

```bash
# 基础依赖（必装）
pip install requests curl_cffi

# 可选：反检测浏览器（绕过Cloudflare）
pip install nodriver

# 可选：自适应爬虫（页面变化容忍）
pip install "scrapling[all]"
```

### 一行代码使用

```python
import asyncio
from smart_scraper import smart_scrape

async def main():
    result = await smart_scrape("https://www.rotowire.com/soccer/lineups.php")
    
    if result.success:
        print(f"成功！使用工具: {result.tool_used}")
        print(f"耗时: {result.duration:.2f}s")
        print(f"内容长度: {len(result.content)} 字节")
    else:
        print(f"失败: {result.error}")

asyncio.run(main())
```

### 自定义调度器

```python
from smart_scraper.core.scheduler import SmartScheduler

async def main():
    scheduler = SmartScheduler()
    
    # 查看可用工具
    tools = await scheduler.get_available_tools()
    for t in tools:
        print(f"{t['name']}: {'可用' if t['available'] else '不可用'}")
    
    # 抓取
    result = await scheduler.scrape("https://example.com")
    
    # 强制指定工具
    result = await scheduler.scrape(url, force_tool="curl_cffi")
    
    # 禁用缓存
    result = await scheduler.scrape(url, use_cache=False)

asyncio.run(main())
```

### 注册自定义工具

```python
from smart_scraper.tools.base import BaseTool, ScrapeResult

class MyCustomTool(BaseTool):
    name = "my_tool"
    priority = 5
    capabilities = ["custom", "anti_bot"]
    
    async def fetch(self, url, **kwargs):
        # 你的抓取逻辑
        return ScrapeResult(success=True, content="...", tool_used=self.name)

# 注册到调度器
scheduler = SmartScheduler()
scheduler.register_tool(MyCustomTool())
```

---

## 项目结构

```
smart_scraper/
├── __init__.py              # 入口：smart_scrape() 一行调用
├── config.py                # 全局配置
├── core/
│   ├── scheduler.py         # 智能调度器（核心）
│   ├── analyzer.py          # 网站特征分析器
│   └── fallback.py          # 降级策略引擎
├── tools/
│   ├── base.py              # 工具基类（统一接口）
│   ├── requests_tool.py     # 轻量级 HTTP
│   ├── curl_cffi_tool.py    # TLS 指纹伪装
│   ├── nodriver_tool.py     # 终极反爬武器
│   └── scrapling_tool.py    # 自适应爬虫
├── profiles/
│   ├── site_profiles.py     # 预定义网站特征库
│   └── user_agents.py       # 真实 UA 池
├── cache/
│   └── manager.py           # 文件缓存管理
├── proxy/
│   └── manager.py           # 代理管理
└── tests/
    └── test_all.py          # 自测脚本
```

---

## 工具选择流程图

```
任务进入
   │
   ▼
┌─────────────────────────────┐
│  1. 检查缓存                │
│  └── 命中 → 直接返回        │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  2. 分析目标网站            │
│  ├── 查询预定义特征库       │
│  ├── 检测 Cloudflare 头     │
│  ├── 检测 DataDome/Imperva  │
│  └── 判断 JS 渲染需求       │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  3. 选择最优工具            │
│  ├── 静态页 → requests      │
│  ├── TLS检测 → curl_cffi   │
│  ├── Cloudflare → nodriver  │
│  └── 动态/改版 → scrapling  │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  4. 执行 + 降级             │
│  ├── 成功 → 缓存 + 返回     │
│  └── 失败 → 自动切换下一工具 │
└─────────────────────────────┘
```

---

## 配置说明

编辑 `config.py`：

```python
# 缓存配置
CACHE_DIR = ".cache"        # 缓存目录
CACHE_TTL = 3600 * 24       # 缓存有效期（秒）

# 请求配置
DEFAULT_TIMEOUT = 15        # 默认超时（秒）

# 代理配置
PROXY_ENABLED = False       # 是否启用代理
PROXY_LIST = []             # 代理列表
```

---

## 适用场景

| 场景 | 推荐工具组合 |
|------|-------------|
| 足球赔率采集 | smart_scrape + curl_cffi/nodriver |
| 比分数据抓取 | smart_scrape + requests |
| 历史数据下载 | smart_scrape + requests |
| 需要登录的网站 | smart_scrape + nodriver |
| 大规模批量采集 | scrapling + Scrapy |

---

## 运行测试

```bash
# 设置 PYTHONPATH
export PYTHONPATH=/path/to/FOOTBALL

# 运行自测
python smart_scraper/tests/test_all.py
```

测试结果：43 通过 | 0 失败

---

## License

MIT License

---

## 作者

**ScrapePhantom** - 幽灵爬虫，让数据抓取不再困难。
