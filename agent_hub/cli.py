"""
Agent Hub CLI - 一键检测和配置
"""
import sys
import json
from .detector import get_agent_info
from .configurator import auto_configure, get_status


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1]
    
    if command == "detect":
        cmd_detect()
    elif command == "configure":
        force = "--force" in sys.argv
        cmd_configure(force)
    elif command == "status":
        cmd_status()
    elif command == "install":
        cmd_install()
    else:
        print_usage()


def print_usage():
    """打印使用说明"""
    print("""
ScrapePhantom Agent Hub

用法:
    python -m smart_scraper.agent_hub <command>

命令:
    detect      检测当前 Agent 和内置抓取工具
    configure   自动配置技能（--force 强制重新配置）
    status      查看配置状态
    install     安装 ScrapePhantom（pip install -e .）
""")


def cmd_detect():
    """检测命令"""
    info = get_agent_info()
    print(json.dumps(info, indent=2, ensure_ascii=False))


def cmd_configure(force: bool = False):
    """配置命令"""
    result = auto_configure(force=force)
    
    if result["success"]:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ {result['message']}")
        sys.exit(1)


def cmd_status():
    """状态命令"""
    status = get_status()
    
    print(f"Agent: {status['agent']} ({status['agent_type']})")
    print(f"配置路径: {status['config_path']}")
    print(f"ScrapePhantom: {'已安装' if status['scrapephantom_installed'] else '未安装'}")
    print(f"内置工具: {', '.join(status['builtin_tools']) or '无'}")
    print(f"技能配置: {'已配置' if status['configured'] else '未配置'}")
    
    if status['config_file']:
        print(f"配置文件: {status['config_file']}")


def cmd_install():
    """安装命令"""
    import subprocess
    import os
    
    # 获取 smart_scraper 目录
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"安装 ScrapePhantom 到: {current_dir}")
    
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", "."],
        cwd=current_dir,
        capture_output=True,
        text=True,
    )
    
    if result.returncode == 0:
        print("✓ 安装成功")
    else:
        print(f"✗ 安装失败:\n{result.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    main()
