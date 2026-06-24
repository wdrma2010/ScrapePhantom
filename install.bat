@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   ScrapePhantom 幽灵爬虫 - 一键安装
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 安装 ScrapePhantom...
pip install -e . -q
if errorlevel 1 (
    echo [错误] 安装失败
    pause
    exit /b 1
)
echo      ✓ 安装完成

echo.
echo [2/3] 检测 Agent 环境...
python -m smart_scraper.agent_hub detect

echo.
echo [3/3] 自动配置技能...
python -m smart_scraper.agent_hub configure

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 使用方法:
echo   from smart_scraper import scrape
echo   result = scrape("https://example.com")
echo.
echo 查看状态:
echo   python -m smart_scraper.agent_hub status
echo.
pause
