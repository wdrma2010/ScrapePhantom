from .base import BaseTool, ScrapeResult
from .requests_tool import RequestsTool
from .curl_cffi_tool import CurlCffiTool
from .nodriver_tool import NodriverTool
from .scrapling_tool import ScraplingTool

ALL_TOOLS = [RequestsTool, CurlCffiTool, ScraplingTool, NodriverTool]
