# ScrapePhantom 幽灵爬虫 - 一键安装脚本 (PowerShell)
# 用法: irm https://raw.githubusercontent.com/wdrma2010/ScrapePhantom/master/install.ps1 | iex

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ScrapePhantom 幽灵爬虫 - 一键安装" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "检测到 Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] 未检测到 Python，请先安装 Python 3.10+" -ForegroundColor Red
    Write-Host "下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[1/3] 安装 ScrapePhantom..." -ForegroundColor Yellow
pip install -e . -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 安装失败" -ForegroundColor Red
    exit 1
}
Write-Host "      ✓ 安装完成" -ForegroundColor Green

Write-Host ""
Write-Host "[2/3] 检测 Agent 环境..." -ForegroundColor Yellow
python -m smart_scraper.agent_hub detect

Write-Host ""
Write-Host "[3/3] 自动配置技能..." -ForegroundColor Yellow
python -m smart_scraper.agent_hub configure

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "使用方法:" -ForegroundColor White
Write-Host '  from smart_scraper import scrape' -ForegroundColor Gray
Write-Host '  result = scrape("https://example.com")' -ForegroundColor Gray
Write-Host ""
Write-Host "查看状态:" -ForegroundColor White
Write-Host "  python -m smart_scraper.agent_hub status" -ForegroundColor Gray
Write-Host ""
