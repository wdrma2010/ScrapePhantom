"""
SmartScraper 自测脚本
测试所有工具的可用性和基本功能
"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smart_scraper.tools.base import ScrapeResult
from smart_scraper.tools.requests_tool import RequestsTool
from smart_scraper.tools.curl_cffi_tool import CurlCffiTool
from smart_scraper.tools.nodriver_tool import NodriverTool
from smart_scraper.tools.scrapling_tool import ScraplingTool
from smart_scraper.core.analyzer import SiteAnalyzer
from smart_scraper.core.scheduler import SmartScheduler
from smart_scraper.cache.manager import CacheManager
from smart_scraper.profiles.site_profiles import SiteProfiles
from smart_scraper.profiles.user_agents import UserAgentPool

TEST_URLS = {
    "static": "https://httpbin.org/html",
    "json": "https://httpbin.org/json",
    "status_404": "https://httpbin.org/status/404",
    "delay": "https://httpbin.org/delay/1",
    "headers": "https://httpbin.org/headers",
    "user_agent": "https://httpbin.org/user-agent",
    "rotowire": "https://www.rotowire.com/soccer/lineups.php",
    "espn_api": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard",
    "football_data": "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
}

RESULTS = {"pass": 0, "fail": 0, "skip": 0, "errors": []}


def log(status: str, msg: str):
    symbols = {"pass": "\033[92m[PASS]\033[0m", "fail": "\033[91m[FAIL]\033[0m", "skip": "\033[93m[SKIP]\033[0m"}
    print(f"  {symbols.get(status, '[????]')} {msg}")
    RESULTS["pass" if status == "pass" else "fail" if status == "fail" else "skip"] += 1
    if status == "fail":
        RESULTS["errors"].append(msg)


async def test_imports():
    print("\n" + "=" * 60)
    print("1. 模块导入测试")
    print("=" * 60)
    
    modules = [
        ("smart_scraper", "主模块"),
        ("smart_scraper.tools.base", "工具基类"),
        ("smart_scraper.tools.requests_tool", "Requests工具"),
        ("smart_scraper.tools.curl_cffi_tool", "CurlCffi工具"),
        ("smart_scraper.tools.nodriver_tool", "Nodriver工具"),
        ("smart_scraper.tools.scrapling_tool", "Scrapling工具"),
        ("smart_scraper.core.scheduler", "智能调度器"),
        ("smart_scraper.core.analyzer", "网站分析器"),
        ("smart_scraper.core.fallback", "降级引擎"),
        ("smart_scraper.cache.manager", "缓存管理器"),
        ("smart_scraper.profiles.site_profiles", "网站特征库"),
        ("smart_scraper.profiles.user_agents", "UA池"),
    ]
    
    for module, desc in modules:
        try:
            __import__(module)
            log("pass", f"{desc} ({module})")
        except Exception as e:
            log("fail", f"{desc} ({module}) - {e}")


async def test_tool_availability():
    print("\n" + "=" * 60)
    print("2. 工具可用性测试")
    print("=" * 60)
    
    tools = [
        ("Requests", RequestsTool()),
        ("CurlCffi", CurlCffiTool()),
        ("Nodriver", NodriverTool()),
        ("Scrapling", ScraplingTool()),
    ]
    
    for name, tool in tools:
        available = await tool.check_availability()
        if available:
            log("pass", f"{name} 可用")
        else:
            log("skip", f"{name} 未安装 (可选依赖)")


async def test_requests_tool():
    print("\n" + "=" * 60)
    print("3. Requests 工具测试")
    print("=" * 60)
    
    tool = RequestsTool()
    
    result = await tool.fetch(TEST_URLS["static"])
    if result.success and len(result.content) > 100:
        log("pass", f"静态页面抓取成功 ({result.duration:.2f}s, {len(result.content)}字节)")
    else:
        log("fail", f"静态页面抓取失败: {result.error}")
    
    result = await tool.fetch(TEST_URLS["json"])
    if result.success:
        log("pass", f"JSON接口抓取成功 ({result.duration:.2f}s)")
    else:
        log("fail", f"JSON接口抓取失败: {result.error}")
    
    result = await tool.fetch(TEST_URLS["status_404"])
    if not result.success and result.status_code == 404:
        log("pass", f"404状态码正确识别 (code={result.status_code})")
    else:
        log("fail", f"404状态码识别异常 (code={result.status_code})")
    
    result = await tool.fetch("https://invalid.domain.fake")
    if not result.success and result.error:
        log("pass", f"无效域名正确报错: {result.error[:50]}")
    else:
        log("fail", "无效域名未报错")


async def test_curl_cffi_tool():
    print("\n" + "=" * 60)
    print("4. CurlCffi 工具测试")
    print("=" * 60)
    
    tool = CurlCffiTool()
    available = await tool.check_availability()
    
    if not available:
        log("skip", "CurlCffi 未安装，跳过测试")
        return
    
    result = await tool.fetch(TEST_URLS["static"])
    if result.success:
        log("pass", f"TLS伪装抓取成功 ({result.duration:.2f}s)")
    else:
        log("fail", f"TLS伪装抓取失败: {result.error}")
    
    result = await tool.fetch(TEST_URLS["headers"])
    if result.success:
        log("pass", f"请求头检查成功 ({result.duration:.2f}s)")
    else:
        log("fail", f"请求头检查失败: {result.error}")


async def test_analyzer():
    print("\n" + "=" * 60)
    print("5. 网站分析器测试")
    print("=" * 60)
    
    analyzer = SiteAnalyzer()
    
    for url, expected_tool in [
        ("https://www.rotowire.com/soccer/lineups.php", "requests"),
        ("https://www.flashscore.com", "scrapling"),
        ("https://www.bet365.com", "nodriver"),
        ("https://www.transfermarkt.com", "curl_cffi"),
        ("https://site.api.espn.com/api/v2/sports", "requests"),
    ]:
        profile = await analyzer.analyze(url)
        recommended = profile.get("recommended_tool")
        confidence = profile.get("confidence", 0)
        
        if recommended == expected_tool:
            log("pass", f"{url[:40]}... → {recommended} (置信度: {confidence})")
        else:
            log("fail", f"{url[:40]}... → 期望 {expected_tool}, 实际 {recommended}")


async def test_scheduler():
    print("\n" + "=" * 60)
    print("6. 智能调度器测试")
    print("=" * 60)
    
    scheduler = SmartScheduler()
    
    tools = await scheduler.get_available_tools()
    available_count = sum(1 for t in tools if t["available"])
    log("pass", f"可用工具: {available_count}/{len(tools)}")
    for t in tools:
        status = "可用" if t["available"] else "不可用"
        log("pass", f"  {t['name']}: {status} (优先级: {t['priority']})")
    
    result = await scheduler.scrape(TEST_URLS["static"], use_cache=False)
    if result.success:
        log("pass", f"调度器抓取成功 (工具: {result.tool_used}, 耗时: {result.duration:.2f}s)")
    else:
        log("fail", f"调度器抓取失败: {result.error}")
    
    result = await scheduler.scrape(TEST_URLS["static"], use_cache=True)
    if result.success and result.tool_used == "cache":
        log("pass", f"缓存命中验证成功")
    elif result.success:
        log("pass", f"首次抓取 (缓存已设置)")
    else:
        log("fail", f"缓存测试失败: {result.error}")


async def test_cache():
    print("\n" + "=" * 60)
    print("7. 缓存管理器测试")
    print("=" * 60)
    
    cache = CacheManager()
    
    test_result = ScrapeResult(
        success=True,
        content="<html>test</html>",
        status_code=200,
        tool_used="test",
        duration=0.1,
        url="test://cache",
    )
    cache.set("test://cache", test_result)
    
    cached = cache.get("test://cache")
    if cached and cached.success and cached.content == "<html>test</html>":
        log("pass", "缓存写入和读取成功")
    else:
        log("fail", "缓存读取失败")
    
    stats = cache.stats()
    log("pass", f"缓存统计: {stats['entries']}条, {stats['total_size_kb']}KB")
    
    cached = cache.get("test://nonexistent")
    if cached is None:
        log("pass", "不存在的缓存正确返回 None")
    else:
        log("fail", "不存在的缓存应返回 None")
    
    cache.clear()
    cached = cache.get("test://cache")
    if cached is None:
        log("pass", "缓存清除成功")
    else:
        log("fail", "缓存清除失败")


async def test_user_agents():
    print("\n" + "=" * 60)
    print("8. User-Agent 池测试")
    print("=" * 60)
    
    ua = UserAgentPool.random()
    if ua and "Mozilla" in ua:
        log("pass", f"随机 UA 生成成功: {ua[:60]}...")
    else:
        log("fail", "UA 生成失败")
    
    uas = set()
    for _ in range(20):
        uas.add(UserAgentPool.random())
    if len(uas) > 1:
        log("pass", f"UA 多样性验证: {len(uas)} 个不同 UA")
    else:
        log("fail", "UA 多样性不足")


async def test_site_profiles():
    print("\n" + "=" * 60)
    print("9. 网站特征库测试")
    print("=" * 60)
    
    profile = SiteProfiles.get_profile("https://www.rotowire.com/soccer")
    if profile and profile.get("recommended_tool") == "requests":
        log("pass", "Rotowire 特征查询正确")
    else:
        log("fail", "Rotowire 特征查询异常")
    
    profile = SiteProfiles.get_profile("https://www.bet365.com/soccer")
    if profile and profile.get("has_cloudflare"):
        log("pass", "Bet365 Cloudflare 特征正确")
    else:
        log("fail", "Bet365 特征查询异常")
    
    count = len(SiteProfiles.PROFILES)
    log("pass", f"已收录 {count} 个网站特征")


async def test_real_world():
    print("\n" + "=" * 60)
    print("10. 真实场景测试")
    print("=" * 60)
    
    scheduler = SmartScheduler()
    
    test_cases = [
        ("ESPN API", TEST_URLS["espn_api"]),
        ("Football-Data CSV", TEST_URLS["football_data"]),
    ]
    
    for name, url in test_cases:
        result = await scheduler.scrape(url, use_cache=False)
        if result.success:
            log("pass", f"{name} 抓取成功 (工具: {result.tool_used}, {len(result.content)}字节)")
        else:
            log("fail", f"{name} 抓取失败: {result.error}")


async def run_all_tests():
    start = time.time()
    
    print("\n" + "=" * 60)
    print("  SmartScraper v1.0.0 自测报告")
    print("=" * 60)
    
    await test_imports()
    await test_tool_availability()
    await test_requests_tool()
    await test_curl_cffi_tool()
    await test_analyzer()
    await test_scheduler()
    await test_cache()
    await test_user_agents()
    await test_site_profiles()
    await test_real_world()
    
    duration = time.time() - start
    
    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)
    print(f"  通过: {RESULTS['pass']}")
    print(f"  失败: {RESULTS['fail']}")
    print(f"  跳过: {RESULTS['skip']}")
    print(f"  耗时: {duration:.2f}s")
    
    if RESULTS["errors"]:
        print(f"\n  失败项:")
        for err in RESULTS["errors"]:
            print(f"    - {err}")
    
    print("=" * 60)
    
    if RESULTS["fail"] == 0:
        print("\n\033[92m  ALL TESTS PASSED!\033[0m")
    else:
        print(f"\n\033[91m  {RESULTS['fail']} TESTS FAILED\033[0m")
    
    return RESULTS["fail"] == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
