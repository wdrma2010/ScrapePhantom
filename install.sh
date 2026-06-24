#!/bin/bash
echo ""
echo "========================================"
echo "  ScrapePhantom 幽灵爬虫 - 一键安装"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.10+"
    echo "安装命令: sudo apt install python3 python3-pip"
    exit 1
fi

echo "[1/3] 安装 ScrapePhantom..."
pip3 install -e . -q
if [ $? -ne 0 ]; then
    echo "[错误] 安装失败"
    exit 1
fi
echo "      ✓ 安装完成"

echo ""
echo "[2/3] 检测 Agent 环境..."
python3 -m smart_scraper.agent_hub detect

echo ""
echo "[3/3] 自动配置技能..."
python3 -m smart_scraper.agent_hub configure

echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "使用方法:"
echo "  from smart_scraper import scrape"
echo '  result = scrape("https://example.com")'
echo ""
echo "查看状态:"
echo "  python3 -m smart_scraper.agent_hub status"
echo ""
