from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
SRC_DIR = ROOT_DIR / "src"

## local managed mcp config
MCP_CONFIG_LOCAL_JSON_PATH = DATA_DIR/ "mcp/config/mcp_config.json"
MCP_CONFIG_LOCAL_CATEGORY_JSON_PATH = DATA_DIR/ "mcp/config/category"
MCP_CONFIG_FOLDER = DATA_DIR/ "mcp/config"
MCP_BASE_URI = "/mcp"
MCP_BASE_CONFIG_URI = "/mcp/config"
MCP_FOLDER_SKIPPED_EXTENSION = ["ds_store"]

## Marketplace Web-Based MCP Config
MCP_CONFIG_MARKETPLACE_JSON_PATH = DATA_DIR/ "mcp/mcp_marketplace/mcp_config.json"
MCP_CONFIG_LOCAL_CACHE_FOLDER = DATA_DIR/ "mcp/mcp_marketplace/files"
MCP_TOOLS_FOLDER_PATH = DATA_DIR/ "mcp/tools/schema"

## MCP Marketplace Config
MCP_MARKETPLACE_MCP_CONFIG_FOLDER = DATA_DIR/ "mcp/mcp_marketplace"
MCP_MARKETPLACE_MCP_CONFIG_NAME = "mcp_config.json"
MCP_MARKETPLACE_MCP_SERVER_META_PATH = DATA_DIR/ "mcp/mcp_marketplace/preinstall_mcp_servers_meta.json"

OUTPUT_FORMAT_SWITCH = "html"
KEY_RESPONSE_TYPE = "response_type"
RESPONSE_TYPE_TEXT = "text"
RESPONSE_TYPE_HTML = "html"
OUTPUT_FORMAT_HTML = "html"
OUTPUT_FORMAT_MARKDOWN = "markdown"
OUTPUT_FORMAT_TEXT = "text"
MOCK_RESPONSE_SWITCH = False
MCP_INIT_AUTO_ENABLE = False

BRANCH_NORMAL = 0
BRANCH_AGENT_ACTION = 1

KEY_CONTEXT = "context"
KEY_THINK ="think"
KEY_TOOL_ID = "tool_id"
KEY_TOOL_NAME = "tool_name"
KEY_TOOL_ARGUMENTS = "tool_arguments"
KEY_TOOLNAME_TO_SERVER_DICT = "toolname_to_server_dict"

SECTION_THINK = "think"
SECTION_ANSWER = "answer"
SECTION_TOOL = "tool"
SECTION_SYSTEM_MSG = "system_msg"
SECTION_CONTEXT = "context"

KEY_MODEL_SELECTION = "model_selection"
MODEL_SELECTION_CLAUDE_OPUS_4 = "claude-opus-4"
MODEL_SELECTION_CLAUDE_37 =  "claude-3.7"
MODEL_SELECTION_GPT4O =  "gpt-4o"
MODEL_SELECTION_GEMINI_25_FLASH = "gemini-2.5-flash"
MODEL_SELECTION_QWEN3_MAX = "qwen3-max"
MODEL_SELECTION_QWEN3_PLUS = "qwen3-plus"
MODEL_SELECTION_DEEPSEEK_R1 = "deepseek-r1"
MODEL_SELECTION_DEFAULT = MODEL_SELECTION_QWEN3_PLUS


KEY_MCP_JSON_SERVERS = "mcpServers"
MCP_TYPE_SSE = "SSE"
MCP_TYPE_STDIO = "STDIO"
MCP_CALL_TOOL_TIMEOUT = 15.0

KEY_SUCCESS = "success"
KEY_CONTENT = "content" 
KEY_MESSAGE = "message"

## timeout for MCP servers to start and connect
MCP_CONNECTION_TIMEOUT = 2.5


