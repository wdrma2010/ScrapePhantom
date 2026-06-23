# ScrapePhantom 幽灵爬虫

> 智能爬虫调度框架 - 自动选择最优爬虫工具，绕过反爬保护

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 项目简介

**ScrapePhantom**（幽灵爬虫）是一个通用的智能爬虫调度框架，核心解决一个痛点：

> **面对不同网站的反爬策略，手动切换爬虫工具太麻烦。**

ScrapePhantom 会自动分析目标网站特征（Cloudflare？DataDome？JS渲染？），然后：
1. 选择最优的爬虫工具
2. 执行抓取
3. 失败时自动降级到下一工具

**一行代码，搞定所有网站。**

---

## 适用场景

| 场景 | 说明 |
|------|------|
| 数据采集 | 电商价格、新闻、社交媒体、公开API |
| 反爬绕过 | Cloudflare、DataDome、Imperva、TLS指纹检测 |
| 动态页面 | SPA、React/Vue 渲染页面、无限滚动 |
| 批量抓取 | 大规模数据采集，自动切换工具避免封禁 |
| 监控告警 | 定时抓取网页变化，触发通知 |
| SEO分析 | 搜索引擎爬虫模拟、排名监控 |
| 学术研究 | 论文数据采集、舆情分析 |

---

## 核心功能

### 1. 智能工具调度

```
任务进入 → 分析网站特征 → 选择最优工具 → 执行 → 失败自动降级
```

内置 4 种爬虫工具，按场景自动选择：

| 工具 | 适用场景 |
|------|---------|
| **requests** | 静态页面、API接口、轻量快速 |
| **curl_cffi** | TLS指纹检测网站、伪装浏览器握手 |
| **scrapling** | JS渲染、页面频繁改版、自适应解析 |
| **nodriver** | Cloudflare、DataDome、需登录、终极反爬 |

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

预定义已知网站的最优抓取策略，支持自定义扩展：

```python
from smart_scraper.profiles.site_profiles import SiteProfiles

# 自动识别网站并推荐工具
profile = SiteProfiles.get_profile("https://example.com")
# → {"has_cloudflare": True, "recommended_tool": "nodriver", ...}

# 添加自定义网站特征
SiteProfiles.add_profile("my-site.com", {
    "has_cloudflare": True,
    "js_rendered": True,
    "recommended_tool": "nodriver",
})
```

---

## 安装

### 一键安装（推荐）

```bash
pip install scrapephantom
```

### 手动安装

```bash
# 克隆仓库
git clone https://github.com/wdrma2010/ScrapePhantom.git
cd ScrapePhantom

# 安装（包含所有依赖）
pip install -e .

# 或仅安装核心依赖
pip install -e ".[core]"
```

### 依赖说明

| 依赖 | 版本 | 说明 |
|------|------|------|
| requests | >=2.28.0 | HTTP基础库（必装） |
| curl_cffi | >=0.5.0 | TLS指纹伪装（必装） |
| nodriver | >=0.30 | 反检测浏览器（必装） |
| scrapling | >=0.2.0 | 自适应爬虫（必装） |

安装 ScrapePhantom 时，以上四个依赖会自动安装。

---

## 快速开始

### 一行代码使用

```python
import asyncio
from smart_scraper import smart_scrape

async def main():
    result = await smart_scrape("https://example.com")
    
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
scrapephantom/
├── __init__.py              # 入口：smart_scrape() 一行调用
├── config.py                # 全局配置
├── pyproject.toml           # 打包配置
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

## 运行测试

```bash
# 安装后运行自测
python -m smart_scraper.tests.test_all

# 或直接运行
python smart_scraper/tests/test_all.py
```

---

## 常见问题

### Q: 安装 scrapling 报错？

scrapling 依赖较多，如果安装失败可以尝试：

```bash
pip install "scrapling[all]" --no-build-isolation
```

### Q: nodriver 需要 Chrome 浏览器？

是的，nodriver 基于 Chromium 内核。确保系统已安装 Chrome/Chromium。

### Q: 如何添加代理？

```python
from smart_scraper.core.scheduler import SmartScheduler

scheduler = SmartScheduler(proxy="http://ip:port")
result = await scheduler.scrape(url)
```

---

## License

MIT License

---

## 作者

**ScrapePhantom** - 幽灵爬虫，让数据抓取不再困难。
