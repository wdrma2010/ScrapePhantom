# ScrapePhantom 幽灵爬虫

> 智能爬虫调度框架 - 四工具并行竞争，谁先成功用谁

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 一句话定位

**ScrapePhantom 是什么？**

> 当你的 Agent 内置抓取工具失败时，ScrapePhantom 自动接管，四个工具并行竞争，谁先抓到用谁。

---

## 一键安装（30秒完成）

### Windows

```cmd
git clone https://github.com/wdrma2010/ScrapePhantom.git
cd ScrapePhantom
install.bat
```

或 PowerShell：
```powershell
git clone https://github.com/wdrma2010/ScrapePhantom.git
cd ScrapePhantom
.\install.ps1
```

### Linux / Mac

```bash
git clone https://github.com/wdrma2010/ScrapePhantom.git
cd ScrapePhantom
chmod +x install.sh
./install.sh
```

**安装脚本会自动：**
1. ✅ 检查 Python 环境
2. ✅ 安装 ScrapePhantom 和所有依赖
3. ✅ 检测你的 Agent 类型
4. ✅ 自动配置技能到正确位置

---

## 核心特色

### 1. 并行竞争（不是串行降级）

```
传统方式: requests 失败 → curl_cffi 失败 → nodriver 失败 → scrapling 失败
            ↓              ↓                ↓              ↓
          等待            等待              等待            等待
          10s             20s               30s            40s

ScrapePhantom: requests ─┐
             curl_cffi ──┼──→ 谁先成功 → 立即采纳 → 取消其他
             nodriver  ──┤
             scrapling ──┘
                         ↓
                       0.5s
```

**效率提升 10 倍以上。**

### 2. Agent Hub（一键集成任何 Agent）

```bash
# 自动检测你的 Agent 类型
python -m smart_scraper.agent_hub detect

# 自动配置技能
python -m smart_scraper.agent_hub configure
```

**支持的 Agent：**
- OpenCode（自动写入 SKILL.md）
- Claude Desktop（自动修改 MCP 配置）
- Cursor（自动修改 MCP 配置）
- 任何其他 Agent（输出通用集成模板）

### 3. 智能触发（无需手动调用）

当你的 Agent 内置工具遇到以下情况时，ScrapePhantom 自动接管：

| 触发条件 | 说明 |
|---------|------|
| 抓取失败 | 内置工具返回错误 |
| 抓取超时 | 响应时间过长 |
| 内容截断 | HTML 不完整 |
| 反爬拦截 | Cloudflare/DataDome/Imperva |
| JS 渲染 | SPA/React/Vue 页面 |
| 状态码异常 | 403/429/503 等 |

### 4. 四工具协同

| 工具 | 优先级 | 核心能力 |
|------|--------|---------|
| **requests** | 1 | 最快，静态页面 |
| **curl_cffi** | 2 | TLS 指纹伪装 |
| **scrapling** | 3 | JS 渲染，自适应解析 |
| **nodriver** | 4 | 真实浏览器，终极反爬 |

---

## 快速开始

### 安装

```bash
git clone https://github.com/wdrma2010/ScrapePhantom.git
cd ScrapePhantom
pip install -e .
```

### 一行代码使用

```python
from smart_scraper import scrape

result = scrape("https://example.com")
print(result.content)  # 成功返回内容，失败返回错误
```

### 自动配置 Agent

```bash
# 检测并自动配置
python -m smart_scraper.agent_hub configure
```

---

## 工作原理

```
┌─────────────────────────────────────────────────────────────┐
│                     你的 Agent                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ 内置工具 A  │    │ 内置工具 B  │    │ 内置工具 C  │      │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                            ▼                                 │
│                    ┌───────────────┐                         │
│                    │   智能检测    │                         │
│                    │ 失败/超时/反爬│                         │
│                    └───────┬───────┘                         │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   ScrapePhantom                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │requests │ │curl_cffi│ │nodriver │ │scrapling│           │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           │
│       │           │           │           │                  │
│       └───────────┼───────────┼───────────┘                  │
│                   │           │                              │
│                   ▼           ▼                              │
│            ┌─────────────────────────┐                      │
│            │     并行竞争引擎        │                      │
│            │  谁先成功 → 立即采纳    │                      │
│            └─────────────────────────┘                      │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ▼
                    ┌───────────────┐
                    │  返回结果     │
                    └───────────────┘
```

---

## 适用场景

### 金融数据采集

| 场景 | 痛点 | ScrapePhantom 方案 |
|------|------|-------------------|
| 实时赔率监控 | bet365/Pinnacle 强反爬 | curl_cffi TLS 伪装 + nodriver 兜底 |
| 亚盘水位追踪 | 频繁触发风控 | 并行竞争 + 缓存 + 随机 UA |
| 交易所数据 | WebSocket + JS 渲染 | nodriver 完整浏览器环境 |
| 量化因子挖掘 | 大规模历史数据 | 高并发 + 智能调度 |

### 电商与价格情报

| 场景 | 痛点 | ScrapePhantom 方案 |
|------|------|-------------------|
| 跨平台比价 | 多站点反爬策略不同 | 四工具自动适配 |
| 价格历史追踪 | 动态渲染 + 登录态 | nodriver 保持 Session |
| 库存监控 | 高频请求封禁 | 并行分散 + 降级策略 |
| 优惠券抓取 | Cloudflare 拦截 | 真实浏览器引擎绕过 |

### 内容与舆情分析

| 场景 | 痛点 | ScrapePhantom 方案 |
|------|------|-------------------|
| 社交媒体监控 | 反爬 + JS 渲染 | scrapling 自适应解析 |
| 新闻聚合 | 多源异构数据 | 智能工具选择 |
| 评论情感分析 | 大规模采集 | 高效并行 + 缓存 |
| SEO 排名追踪 | 搜索引擎反爬 | TLS 指纹伪装 |

### 学术与研究

| 场景 | 痛点 | ScrapePhantom 方案 |
|------|------|-------------------|
| 论文数据采集 | 知网/SciHub 反爬 | 多工具协同突破 |
| 公开数据集获取 | 格式混乱 + 验证码 | 自适应解析 + 降级 |
| 舆情分析 | 海量网页抓取 | 高并发 + 智能调度 |

### 企业级应用

| 场景 | 痛点 | ScrapePhantom 方案 |
|------|------|-------------------|
| 竞品监控 | 定时 + 稳定性 | 缓存 + 失败重试 |
| 市场调研 | 多维度数据整合 | 统一接口 + 并行采集 |
| 合规审查 | 需要完整证据链 | 全量抓取 + 日志记录 |
| API 数据补充 | 第三方 API 限制 | 爬虫 + API 混合策略 |

### 为什么选择 ScrapePhantom

| 对比维度 | 单一工具 | ScrapePhantom |
|---------|---------|---------------|
| 反爬绕过 | 需手动适配 | 自动分析 + 并行竞争 |
| 失败恢复 | 需人工干预 | 自动降级 + 智能切换 |
| Agent 集成 | 无 | 一键配置 + 全局生效 |
| 性能 | 串行等待 | 并行竞争 10x 提速 |
| 覆盖范围 | 部分场景 | 全场景覆盖 |

---

## 配置状态

```bash
python -m smart_scraper.agent_hub status
```

输出示例：
```
Agent: opencode (opencode)
配置路径: C:\Users\xxx/.config/opencode
ScrapePhantom: 已安装
内置工具: requests, httpx, aiohttp, curl_cffi, nodriver
技能配置: 已配置
配置文件: C:\Users\xxx/.config/opencode/skills/scrapephantom/SKILL.md
```

---

## 项目结构

```
scrapephantom/
├── __init__.py              # 入口：scrape() / smart_scrape()
├── core/
│   ├── scheduler.py         # 智能调度器
│   ├── analyzer.py          # 网站特征分析器
│   └── fallback.py          # 并行竞争引擎
├── tools/
│   ├── requests_tool.py     # 轻量级 HTTP
│   ├── curl_cffi_tool.py    # TLS 指纹伪装
│   ├── nodriver_tool.py     # 终极反爬武器
│   └── scrapling_tool.py    # 自适应爬虫
├── agent_hub/               # Agent 智能集成
│   ├── detector.py          # 检测 Agent 和内置工具
│   ├── configurator.py      # 自动配置技能
│   └── cli.py               # 命令行工具
├── profiles/                # 网站特征库
├── cache/                   # 缓存管理
└── SKILL.md                 # OpenCode 技能配置
```

---

## 常见问题

### Q: 和其他爬虫工具有什么区别？

| 对比项 | ScrapePhantom | 单一工具 |
|--------|---------------|---------|
| 工具数量 | 4 个并行 | 1 个 |
| 失败处理 | 自动竞争 | 手动切换 |
| Agent 集成 | 自动配置 | 无 |
| 反爬绕过 | 全覆盖 | 部分 |

### Q: 如何集成到我的 Agent？

```bash
# 一键配置
python -m smart_scraper.agent_hub configure
```

### Q: 支持哪些 Agent？

OpenCode、Claude Desktop、Cursor，以及任何支持 Python 的 Agent。

---

## License

MIT License
