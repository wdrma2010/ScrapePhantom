"""全局配置"""
import os

# 缓存配置
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
CACHE_TTL = 3600 * 24  # 24小时

# 请求配置
DEFAULT_TIMEOUT = 15
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# 代理配置
PROXY_ENABLED = False
PROXY_LIST = []  # ["http://ip:port", ...]

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 1  # 秒

# 日志配置
LOG_LEVEL = "INFO"
