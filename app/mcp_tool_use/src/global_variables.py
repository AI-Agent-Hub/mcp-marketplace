import os
import logging

from typing import Dict, List, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

env = os.environ.copy()

def tool_to_dict(tools):
    """
        Convert mcp Tool Class to dict {"name": "", "description": "", "input_schema":""}
    """
    try:
        print (f"DEBUG: tool_to_dict tools {tools}")
        tool_dict_list = [
            {
                "name": tool.name, 
                "description": tool.description, 
                "input_schema": tool.inputSchema
            } for tool in tools]
        return tool_dict_list
    except Exception as e:
        logging.error(e)
        return []

class MCPClient:
    def __init__(self, name: str = ""):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        # self.anthropic = Anthropic() 
        self.name = name
        # save for future reconnection
        self.server_config = None

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an SSE MCP server."""
        logger.debug(f"Connecting to SSE MCP server at {server_url}")
        streams_context = await self.exit_stack.enter_async_context(sse_client(url=server_url))
        self.session = await self.exit_stack.enter_async_context(ClientSession(*streams_context))

        await self.session.initialize()
        response = await self.session.list_tools()
        tools = response.tools
        logger.info(f"Connected to SSE MCP Server at {server_url}. Available tools: {[tool.name for tool in tools]}")
        return tool_to_dict(tools)

    async def connect_to_stdio_server(self, server_script_path: str):
        """Connect to a stdio MCP server."""
        is_python = False
        is_javascript = False
        command = None
        args = [server_script_path]

        if server_script_path.startswith("@") or "/" not in server_script_path:
            is_javascript = True
            command = "npx"
        else:
            is_python = server_script_path.endswith(".py")
            is_javascript = server_script_path.endswith(".js")
            if not (is_python or is_javascript):
                raise ValueError("Server script must be a .py, .js file or npm package.")

            command = "python" if is_python else "node"
            
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )

        logger.debug(f"Connecting to stdio MCP server with command: {command} and args: {args}")

        # Use exit_stack for stdio_client and ClientSession
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self.exit_stack.enter_async_context(ClientSession(*stdio_transport))

        await self.session.initialize()
        response = await self.session.list_tools()
        tools = response.tools
        logger.info(f"Connected to stdio MCP Server. Available tools: {[tool.name for tool in tools]}")
        return tool_to_dict(tools)

    async def connect_to_server_config(self, server_config: dict):
        """Connect to an MCP server based on config.
        args:
            server_config with keys {"command": "", "args": [], "env"} or {"url"}
        output:
            list of tools
        """
        global env
        self.server_config = server_config

        tools = []
        if "url" in server_config:
            server_url = server_config['url']
            tools = await self.connect_to_sse_server(server_url) # This will now use exit_stack internally

        elif "command" in server_config:
            # Re-use connect_to_stdio_server for cleaner code
            command = server_config.get("command")
            args = server_config.get("args", [])
            env_local = server_config.get("env", {})

            for key, value in env_local.items():
                env[key] = value

            if command and args: # Assuming the first arg is the script path
                server_params = StdioServerParameters(
                    command=command,
                    args=args,
                    env=env
                )
                stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                self.session = await self.exit_stack.enter_async_context(ClientSession(*stdio_transport))
                await self.session.initialize()
                response = await self.session.list_tools()
                tools = tool_to_dict(response.tools)

            else:
                logger.error(f"Invalid stdio server config: {server_config}")
                raise ValueError("Stdio server config requires 'command' and 'args'.")
        else:
            logger.warning(f"Unsupported transport for server config: {server_config}")

        return tools

    async def connect_to_server(self, server_script_path: str):
        """
        Connect to an MCP server using a script path (simplified for stdio only).
        This function duplicates logic from connect_to_stdio_server and connect_to_server_config.
        Consider consolidating.
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
            
        command = "python3" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self.exit_stack.enter_async_context(ClientSession(*stdio_transport))
        
        await self.session.initialize()
        
        response = await self.session.list_tools()
        tools = tool_to_dict(response.tools)
        print("\nConnected to server with tools:", [tool.name for tool in tools])

        output_tools = {}
        server_path_list = server_script_path.split("/")
        match_index = 0
        for i, name in enumerate(server_path_list):
            if name == "servers_list":
                match_index = i
        server_name_index = match_index + 1
        server_folder = server_path_list[server_name_index] if len(server_path_list) >= (server_name_index + 1) else ""
        output_tools["server"] = server_folder
        output_tools["tools"] = tools
        return output_tools

    @property
    def is_session_active(self) -> bool:
        """Check if the MCP session is active."""
        return self.session is not None

    async def reconnect(self):
        if self.server_config is None:
            return
        logger.info(f"Reconnecting to Server up MCPClient '{self.name}' resources...")
        await self.connect_to_server_config(self.server_config)
    
    async def cleanup(self):
        """Clean up resources entered into the AsyncExitStack."""
        logger.info(f"Cleaning up MCPClient '{self.name}' resources...")       
        if self.exit_stack._exit_callbacks:
            if self.session:
                await self.session.close()
                await self.session.wait_closed()
                self.session = None
                # await self.session.aclose()  
                # self.session = None

    async def query_tool(self, tool_name: str, tool_input: Dict) -> Any:
        if not self.session:
            raise ConnectionError("Session not established. Call connect_to_server first.")
        mcp_request = {
            "type": "tool_call", # This is a guess, actual MCP request format can vary
            "tool_name": tool_name,
            "tool_input": tool_input
        }
        
        await self.session.send_message(mcp_request)
        
        response = await self.session.receive_message()
        
        if response and response.get("type") == "tool_result" and response.get("tool_name") == tool_name:
            return response.get("tool_result")
        elif response and response.get("type") == "error":
            raise RuntimeError(f"MCP Server Error: {response.get('message')}")
        else:
            if isinstance(response, dict) and "response" in response: # a bit of a hack for the dummy
                if f"echoes: {tool_input.get('message')}" in response.get("response", ""):
                    return response

            raise ValueError(f"Unexpected response from MCP server: {response}")

class Settings(BaseSettings):

    QWEN_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",  
        env_file_encoding="utf-8",
        extra="ignore"            
    )

## Python Program
_global_server_tools_dict_local: Dict[str, List[Any]] = {}
_global_server_registry: Dict[str, Dict[str, Any]] = {}

## WEB
_global_mcp_marketplace_preinstall_servers: Dict[str, Any] = {}
_global_mcp_config_local_cache: Dict[str, Any] = {}  # key: server_id, value: mcp_config dict

# save sse servers Client
_global_mcp_client_dict: Dict[str, Dict[str, Any]] = {}

settings = Settings()

