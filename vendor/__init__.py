"""
ScrapePhantom Vendor 包管理
自动将 vendor 目录加入 sys.path，优先使用内置版本
"""
import sys
import os
import warnings

_vendor_dir = os.path.join(os.path.dirname(__file__))

# 将 vendor 目录优先插入 sys.path（在系统包之前）
if _vendor_dir not in sys.path:
    sys.path.insert(0, _vendor_dir)

# 版本锁定：内置版本号
VENDORED_VERSIONS = {
    "requests": "2.33.0",
    "curl_cffi": "0.15.0",
    "nodriver": "0.50.3",
    "scrapling": "0.4.8",
}


def check_conflicts():
    """检测依赖冲突：检查系统中是否存在同名但不同版本的包"""
    conflicts = []
    
    check_packages = {
        "requests": "requests",
        "curl_cffi": "curl_cffi",
        "nodriver": "nodriver",
        "scrapling": "scrapling",
    }
    
    for import_name, display_name in check_packages.items():
        try:
            mod = __import__(import_name)
            sys_version = getattr(mod, "__version__", "unknown")
            vendor_version = VENDORED_VERSIONS.get(display_name, "unknown")
            
            # 检查是否加载的是 vendor 版本
            mod_file = getattr(mod, "__file__", "")
            if mod_file and _vendor_dir in mod_file:
                continue  # 使用的是 vendor 版本，无冲突
            
            if sys_version != vendor_version:
                conflicts.append({
                    "package": display_name,
                    "vendor_version": vendor_version,
                    "system_version": sys_version,
                    "location": mod_file,
                })
        except ImportError:
            pass
    
    return conflicts


def print_diagnostics():
    """打印诊断信息"""
    print("=" * 60)
    print("  ScrapePhantom 依赖诊断")
    print("=" * 60)
    
    print(f"\n  Vendor 目录: {_vendor_dir}")
    
    # 检查 vendor 包是否存在
    print("\n  内置包状态:")
    for pkg, ver in VENDORED_VERSIONS.items():
        pkg_dir = os.path.join(_vendor_dir, pkg)
        exists = os.path.isdir(pkg_dir)
        status = "OK" if exists else "MISSING"
        print(f"    {pkg}: {ver} [{status}]")
    
    # 检测冲突
    conflicts = check_conflicts()
    if conflicts:
        print("\n  冲突检测:")
        for c in conflicts:
            print(f"    WARNING: {c['package']}")
            print(f"      Vendor: {c['vendor_version']}")
            print(f"      System: {c['system_version']} ({c['location']})")
        print("\n  建议: 卸载系统版本避免冲突")
        print("    pip uninstall " + " ".join(c["package"] for c in conflicts))
    else:
        print("\n  冲突检测: 无冲突")
    
    # 测试导入
    print("\n  导入测试:")
    test_imports = ["requests", "curl_cffi", "nodriver", "scrapling"]
    for mod_name in test_imports:
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", "?")
            loc = "vendor" if _vendor_dir in getattr(mod, "__file__", "") else "system"
            print(f"    {mod_name}: v{ver} [{loc}]")
        except ImportError as e:
            print(f"    {mod_name}: FAILED ({e})")
    
    print("\n" + "=" * 60)


# 初始化时自动检测冲突（仅在调试模式下输出）
_initialized = False

def _auto_check():
    global _initialized
    if _initialized:
        return
    _initialized = True
    
    conflicts = check_conflicts()
    if conflicts:
        names = ", ".join(c["package"] for c in conflicts)
        warnings.warn(
            f"ScrapePhantom: 检测到依赖冲突 [{names}]，"
            f"请运行 smart_scraper.vendor.print_diagnostics() 查看详情",
            UserWarning,
            stacklevel=2,
        )


_auto_check()
