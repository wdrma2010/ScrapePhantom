---
name: scrapephantom
description: Use when the user needs to scrape websites, fetch web data, bypass anti-bot protection (Cloudflare, DataDome, Imperva), extract odds/scores/match data, or perform any web crawling task. Supports automatic tool selection: requests, curl_cffi, nodriver, scrapling. Use ONLY when web scraping, data extraction, or anti-detection crawling is requested.
---

# ScrapePhantom - 幽灵爬虫

智能爬虫调度框架，根据任务复杂度自动选择最优爬虫工具，绕过反爬保护。

## 核心能力

- **自动工具选择**：分析目标网站特征，自动选择 requests / curl_cffi / nodriver / scrapling
- **反检测绕过**：绕过 Cloudflare、DataDome、Imperva 等反爬系统
- **降级兜底**：主工具失败时自动切换下一工具
- **缓存管理**：本地文件缓存，减少重复请求
- **网站特征库**：预定义 17+ 已知网站的最优抓取策略

## 工具选择逻辑

| 网站特征 | 自动选择 | 原因 |
|---------|---------|------|
| 静态 HTML | requests | 最快最轻量 |
| TLS 指纹检测 | curl_cffi | 伪装浏览器握手 |
| Cloudflare / DataDome | nodriver | 需要真实浏览器引擎 |
| JS 动态渲染 | nodriver / scrapling | 完整浏览器或自适应 |
| 页面频繁改版 | scrapling | 自动重定位元素 |

## 智能触发规则

当遇到以下情况时，必须自动调用 ScrapePhantom 重试：

1. **内置抓取工具返回错误或失败**
2. **抓取超时**（任何工具超时都算）
3. **内容不完整或被截断**
4. **需要绕过反爬保护**（Cloudflare、DataDome、Imperva等）
5. **需要渲染 JavaScript 动态内容**（SPA、React/Vue页面）
6. **HTTP 状态码异常**（403、429、503等）
7. **返回内容为空或格式异常**

**重要**：不要直接输出"抓取失败"，必须先尝试 ScrapePhantom。

## 使用方式

### 同步调用（推荐，简单直接）

```python
from smart_scraper import scrape

result = scrape("https://example.com")
if result.success:
    print(result.content)
else:
    print(f"失败: {result.error}")
```

### 异步调用（高性能，并发场景）

```python
from smart_scraper import smart_scrape

result = await smart_scrape("https://example.com")
if result.success:
    print(result.content)
```

### 强制指定工具

```python
# 同步
result = scrape(url, force_tool="curl_cffi")

# 异步
result = await smart_scrape(url, force_tool="curl_cffi")
```

### 禁用缓存

```python
result = scrape(url, use_cache=False)
```

### 并行抓取多个URL

```python
import asyncio
from smart_scraper import smart_scrape

async def fetch_all(urls):
    tasks = [smart_scrape(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
```

### 自定义调度器

```python
from smart_scraper.core.scheduler import SmartScheduler

scheduler = SmartScheduler()
result = await scheduler.scrape(url)
tools = await scheduler.get_available_tools()
```

## 支持的工具

| 工具 | 优先级 | 能力 | 安装 |
|------|--------|------|------|
| requests | 1 | fast, lightweight, static | pip install requests |
| curl_cffi | 2 | tls_fingerprint, anti_bot, fast | pip install curl_cffi |
| scrapling | 3 | adaptive, anti_bot, js_render, stealth | pip install scrapling[all] |
| nodriver | 4 | anti_bot, js_render, login, cloudflare | pip install nodriver |

## 预定义网站

已收录最优抓取策略的网站：
- 赔率：oddschecker.com, bet365.com
- 数据：rotowire.com, flashscore.com, sofascore.com, fbref.com
- ESPN：espn.com (免费 API)
- 中国竞彩：sporttery.cn, 500.com, zgzcw.com

## 项目路径

代码位于：`D:\opencode\FOOTBALL\smart_scraper\`

## 依赖安装

```bash
pip install requests curl_cffi    # 基础依赖（必装）
pip install nodriver              # 可选：反检测浏览器
pip install "scrapling[all]"      # 可选：自适应爬虫
```

## Agent 集成指南

### 对于有内置抓取工具的 Agent

在工具调用逻辑中加入降级规则：

```
伪代码：
try:
    result = 内置工具.fetch(url)
except 失败/超时:
    result = smart_scraper.scrape(url)  # 自动降级
```

### 对于没有内置工具的 Agent

直接使用 ScrapePhantom 作为唯一抓取工具：

```python
from smart_scraper import scrape

# 所有抓取任务都用这个
result = scrape(url)
```

### 错误处理模板

```python
from smart_scraper import scrape

def safe_fetch(url):
    result = scrape(url, timeout=15)
    if not result.success:
        # 记录失败，但不阻断流程
        print(f"警告: {url} 抓取失败 - {result.error}")
        return None
    return result.content
```
