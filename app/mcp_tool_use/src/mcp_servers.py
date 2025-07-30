import logging
import codecs
import json
import asyncio
import sys
import os
from contextlib import AsyncExitStack
from typing import Optional, List, Dict, Any
import httpx

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

import mcp_marketplace as mcpm

from fastapi import APIRouter
from fastapi import Path, HTTPException
from pydantic import BaseModel

import uuid
import time

import subprocess
import httpx

from .constants import *
from .global_variables import MCPClient
from . import global_variables as gv
from .utils import *

# Set up basic logging (optional, but good for debugging)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


router = APIRouter()

env = os.environ.copy()

def load_available_mcp_servers(input_file):
    """
        Args:
            input_file: str, "./mcp.json"
        output:
            {"server1": "", "server2": ""}
    """
    mcp_config_files = read_file(input_file)
    mcp_config_str = "".join(mcp_config_files)
    mcp_config = {}
    try:
        mcp_config = json.loads(mcp_config_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {input_file}: {e}")
        return {}
    
    mcp_servers_config_map = mcp_config.get(KEY_MCP_JSON_SERVERS, {})
    # No need for mcp_servers_config_map_valid if we handle errors during connection
    return mcp_servers_config_map

def load_available_mcp_servers_folder(input_folder):
    file_path_list = []
    for root, dirs, files in os.walk(input_folder):
        if files:
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_path_list.append(file_path)
    mcp_config_merge = {}
    for file in file_path_list:
        mcp_config = load_available_mcp_servers(file)
        mcp_config_merge.update(mcp_config)
    # print (f"load_available_mcp_servers_folder mcp_config_merge {mcp_config_merge}")
    return mcp_config_merge

def load_available_tools(folder, skip_ext: List[str] = [".DS_Store"]):
    """
    Load available tools from folder
    """
    server_tools_dict = {}
    try:
        if not os.path.isdir(folder):
            logger.warning(f"Tools folder '{folder}' not found or is not a directory.")
            return {}
            
        for file_name in os.listdir(folder):
            if file_name in skip_ext:
                continue        
            abs_file_path = os.path.join(folder, file_name)
            lines = read_file(abs_file_path)
            server_name = file_name.replace(".json", "")
            
            json_str = "".join(lines)
            json_str = json_str.replace("\n", "")
            tool_dict = {}
            try:
                tool_dict = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from tool file {abs_file_path}: {e}")
                continue
            tools_list = tool_dict.get("tools", [])      
            server_tools_dict[server_name] = tools_list
    except Exception as e:
        logger.error(f"Error loading available tools from {folder}: {e}")
    return server_tools_dict

def load_mcp_registry_json(mcp_servers_map):
    server_registry: Dict[str, Dict[str, Any]] = {}
    if len(mcp_servers_map) > 0:
        try:

            print (f"load_mcp_json input_file mcp_config {mcp_servers_map}")
            for server_name, server_config in mcp_servers_map.items():
                server_id = server_name
                if server_id not in server_registry: # Avoid overwriting runtime state on simple reload
                    server_registry[server_id] = {"config": server_config, 
                        "process": None, 
                        "status": "Off",
                        "tools": []
                    }
                else: 
                    server_registry[server_id]["config"] = server_config
            print (f"load_mcp_json server_registry {server_registry}")

        except json.JSONDecodeError:
            print(f"Error: {input_file} contains invalid JSON.")
        except Exception as e:
            print(f"Error loading {input_file}: {e}")
            traceback.print_exc()
    else:
        print(f"Warning: {mcp_config} empty...")
    return server_registry

def save_mcp_registry_json(output_file_path):
    mcp_config_servers_dict = {name: (data["config"] if "config" in data else {}) for name, data in server_registry.values()}
    mcp_config = {}
    mcp_config[KEY_MCP_JSON_SERVERS] = mcp_config_servers_dict
    print (f"DEBUG: save_mcp_json {mcp_config}")

async def send_mcp_message(writer: asyncio.StreamWriter, message: dict):
    """
    Sends an MCP message (JSON-RPC) over the given stream writer.
    Assumes Content-Length header is required.
    """
    json_message = json.dumps(message) + "\n"
    content_length = len(json_message.encode('utf-8')) # Get byte length

    # Construct the header and body
    full_message = (
        f"Content-Length: {content_length}\r\n"
        f"Content-Type: application/json\r\n\r\n" # Often needed
        f"{json_message}"
    )

    writer.write(full_message.encode('utf-8'))
    await writer.drain()

def server_type_mcp_server_id(server_id: str):
    """
        MCP_TYPE_SSE: SEE
        MCP_TYPE_STDIO: STDIO
    """
    try:
        mcp_type = None
        if server_id not in gv._global_server_registry:
            return False, "Server ID not found."
        config = gv._global_server_registry[server_id]["config"] if "config" in gv._global_server_registry[server_id] else {}
        command_base = config.get("command")
        args = config.get("args", []) # list
        env_local = config.get("env", {})   # dict
        if not command_base:
            url = config.get("url", None)
            if url:
                mcp_type = MCP_TYPE_SSE
        else:
            mcp_type = MCP_TYPE_STDIO
        return mcp_type
    except Exception as e:
        logger.error(e)
        logger.error("Failed to server_type_mcp_server_id")
        return None

async def start_mcp_server_process(server_id: str):

    global env

    if server_id not in gv._global_server_registry:
        return False, "Server ID not found."
    if gv._global_server_registry[server_id]["status"] == "On":
        return True, "Server already running."

    config = gv._global_server_registry[server_id]["config"]
    mcp_server_type = server_type_mcp_server_id(server_id)
    if mcp_server_type is None:
        logger.error(f"start_mcp_server_process {server_id} mcp_server_type is None..")
        return False, f"{server_id} mcp_server_type is None..."

    if mcp_server_type == MCP_TYPE_SSE:
        ## SSE Client
        url = config.get("url", None)
        if url is not None:
            print (f"DEBUG: Starting SSE Server with url {url} and config {config}")
            # start an SSE Server
            client = MCPClient(name=server_id)
            try:
                # We don't need the tools returned here if we're just storing the client
                tools = await client.connect_to_server_config(config)

                gv._global_mcp_client_dict[server_id] = client
                # display in the server tools section
                gv._global_server_registry[server_id]["tools"] = tools

                logger.info(f"MCPClient for '{server_id}' initialized and connected.")

            except Exception as e:
                logger.error(f"Server Connection Error for '{server_id}': {e}")
                # Ensure cleanup for failed connections too
                await client.cleanup() 

            gv._global_server_registry[server_id]["status"] = "On"
            return True, f"Server SSE Started successfully {url}"
        else:
            gv._global_server_registry[server_id]["status"] = "Error"
            return False, "Server url not configured."
    elif mcp_server_type == MCP_TYPE_STDIO:
        ## staring stdio server
        try:

            command_base = config.get("command")
            args = config.get("args", []) 
            env_local = config.get("env", {})
            command = [command_base] + args
            for key, value in env_local.items():
                env[key] = value
            print (f"Staring Server {server_id} with command {command} and env {env}")

            cwd = config.get("cwd", None) # Potentially add 'cwd' to mcp.json if servers are in subdirs
            if cwd and not os.path.isabs(cwd):
                cwd = os.path.join(INSTALLED_SERVERS_DIR, server_id, cwd) # Example convention

            command_line = " ".join(command)
            process = await asyncio.create_subprocess_shell(
                command_line,
                env=env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE  # Capture stderr as well
            )

            print (f"DEBUG: Start of Sleeping Waiting for Request")
            await asyncio.sleep(1)

            initialized_notification_message = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            await send_mcp_message(process.stdin, initialized_notification_message)

            print (f"DEBUG: start_mcp_server_process End of Sleeping Waiting for Request")

            query_response = await list_tools_stdio_server(process, server_id)

            print (f"DEBUG: start_mcp_server_process  End of Sleeping Waiting for query_response {query_response}")

            tools = query_response.data if query_response.success else []

            gv._global_server_registry[server_id]["process"] = process
            gv._global_server_registry[server_id]["status"] = "On"
            gv._global_server_registry[server_id]["tools"] = tools

            print(f"MCP Server '{server_id}' PID: {process.pid}, Command {command}, Tools {tools}")
            
            return True, "Server started successfully."
        except Exception as e:
            gv._global_server_registry[server_id]["status"] = "Error"
            print(f"Failed to start server {server_id}: {e}")
            return False, str(e)
    else:
        return False, f"{server_id} mcp_server_type {mcp_server_type} is None..."


def tool_mapper_json(tools):
    """
        tools: List[Dict]
        name
        description
        inputSchema -> input_schema
    """
    try:
        tools_mapped = [{
            "name": tool["name"] if "name" in tool else "",
            "description": tool["description"] if "description" in tool else "",
            "input_schema": tool["inputSchema"] if "inputSchema" in tool else {},
        } for tool in tools]
        return tools_mapped
    except Exception as e:
        logging.error(f"json_tool_mapper failed with error {e}")
        return tools

async def list_tools_stdio_server(process, server_id):
    """
        Args:
            process: (proc)
            server_id: (str)
        Return:
            https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview
        ## modification, add consuming non json rpc like text
    """
    if process is None:
        return QueryResponse(success=False, error="No process from server found...")
    try:
        mcp_request = {
            "jsonrpc": "2.0", 
            "id": str(uuid.uuid4()),
            "method": "tools/list",
            "params": {}
        }
        await send_mcp_message(process.stdin, mcp_request)
        print(f"DEBUG: Data written to stdin and drained. {mcp_request}")
        print("DEBUG: Waiting for response from stdout...")

        response_data = None
        stderr_output = b'' # Accumulate stderr output
        total_timeout = 15.0 # Total time to wait for the actual JSON response
        start_time = asyncio.get_event_loop().time()

        while response_data is None and (asyncio.get_event_loop().time() - start_time < total_timeout):
            try:
                current_line_bytes = await asyncio.wait_for(process.stdout.readline(), timeout=0.5)

                # Concurrently check for stderr output
                try:
                    current_stderr_chunk = await asyncio.wait_for(process.stderr.read(1024), timeout=0.01)
                    if current_stderr_chunk:
                        stderr_output += current_stderr_chunk
                        print(f"DEBUG: Stderr captured concurrently: {current_stderr_chunk.decode().strip()}")
                except asyncio.TimeoutError:
                    pass # No stderr chunk ready

                if not current_line_bytes:
                    # If stdout stream closes, server likely exited
                    print("DEBUG: Server stdout stream closed unexpectedly while waiting for response.")
                    break

                decoded_line = current_line_bytes.decode('utf-8').strip()
                print(f"DEBUG: Received raw response line: {decoded_line!r}")

                try:
                    parsed_json = json.loads(decoded_line)
                    # Check if it's a JSON-RPC response and if the ID matches our request
                    if "jsonrpc" in parsed_json and parsed_json.get("id") == mcp_request["id"]:
                        response_data = parsed_json # Found our response!
                        print(f"DEBUG: Successfully parsed and matched response for ID {mcp_request['id']}: {response_data}")
                        break # Exit the loop, we found what we're looking for
                    else:
                        print(f"DEBUG: Received JSON but ID does not match request ID ({parsed_json.get('id')}). Continuing to read.")
                        # This could be a notification or a response to an old/untracked request.
                        # We continue reading until we find *our* response.
                except json.JSONDecodeError as e:
                    print(f"DEBUG: Not Valid Json '{decoded_line}' with error {e}. Discarding and continuing to read.")
                except UnicodeDecodeError as e:
                    print(f"DEBUG: UnicodeDecodeError: {e} for line {current_line_bytes!r}. Discarding and continuing to read.")

            except asyncio.TimeoutError:
                # This specific timeout (0.5s) means no line was read within this small window.
                # The outer while loop continues until the total_timeout is hit.
                print("DEBUG: No stdout line received within 0.5s. Retrying...")
                
            # Crucial: Check if the process has exited at each iteration
            if process.returncode is not None:
                print(f"ERROR: Server process exited with code: {process.returncode} while waiting for response.")
                # Read any remaining stderr output before returning
                try:
                    remaining_stderr = await asyncio.wait_for(process.stderr.read(), timeout=1.0)
                    if remaining_stderr:
                        stderr_output += remaining_stderr
                        print(f"ERROR: Remaining stderr: {remaining_stderr.decode().strip()}")
                except asyncio.TimeoutError:
                    pass
                return QueryResponse(success=False, error=f"Server '{server_id}' process exited with code {process.returncode} and no response. Stderr: {stderr_output.decode().strip()}")

        if response_data is None:
            # This block is reached if the loop completes without finding a matching response
            print(f"ERROR: Timeout after {total_timeout} seconds waiting for response for ID '{mcp_request['id']}'.")
            # Final check for stderr if we timed out
            try:
                final_stderr = await asyncio.wait_for(process.stderr.read(), timeout=1.0)
                if final_stderr:
                    stderr_output += final_stderr
                    print(f"ERROR: Final stderr upon timeout: {final_stderr.decode().strip()}")
            except asyncio.TimeoutError:
                pass
            return QueryResponse(success=False, error=f"Server '{server_id}' did not respond within {total_timeout} seconds. Stderr: {stderr_output.decode().strip()}")

        result = response_data["result"] if "result" in response_data else {}
        tools = result["tools"] if "tools" in result else []
        tools = tool_mapper_json(tools)
        print (f"Available Tools From Server {server_id} tools {tools}")
        return QueryResponse(success=True, data=tools)
    except Exception as e:
        logger.error(e)
        return QueryResponse(success=False, error=f"Failed to process list_tools_stdio_server {e}")

async def list_tools_stdio_server_v0(process, server_id):
    """
        Args:
            process: (proc)
            server_id: (str)
        Return:
            https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview
    """
    if process is None:
        return QueryResponse(success=False, error="No process from server found...")
    try:
        mcp_request = {
            "jsonrpc": "2.0", 
            "id": str(uuid.uuid4()),
            "method": "tools/list",
            "params": {}
        }
        await send_mcp_message(process.stdin, mcp_request)
        print(f"DEBUG: Data written to stdin and drained. {mcp_request}")
        print("DEBUG: Waiting for response from stdout...")

        response_line = b''
        stderr_output = b'' # Initialize stderr_output
        try:
            response_line = await asyncio.wait_for(process.stdout.readline(), timeout=15.0)
            print(f"DEBUG: Received raw response line: {response_line!r}")
            try:
                stderr_output = await asyncio.wait_for(process.stderr.read(), timeout=0.1)
                if stderr_output:
                    print(f"DEBUG: Stderr captured concurrently: {stderr_output.decode().strip()}")
            except asyncio.TimeoutError:
                pass

        except asyncio.TimeoutError:
            print(f"ERROR: Timeout after {15.0} seconds waiting for stdout response from server '{server_id}'.")
          
            try:
                print("DEBUG: Checking stderr for error messages after stdout timeout...")
                stderr_output = await asyncio.wait_for(process.stderr.read(), timeout=2.0) # Give stderr more time to produce output
                if stderr_output:
                    print(f"ERROR: Stderr from '{server_id}': {stderr_output.decode().strip()}")
                    return QueryResponse(success=False, error=f"Server '{server_id}' did not respond in time. Stderr: {stderr_output.decode().strip()}")
            except asyncio.TimeoutError:
                print("DEBUG: No stderr output either within timeout.")
            
            if process.returncode is not None:
                print(f"DEBUG: Server process exited with code: {process.returncode} after timeout.")
                return QueryResponse(success=False, error=f"Server '{server_id}' process exited with code {process.returncode} and no response.")

            return QueryResponse(success=False, error=f"Server '{server_id}' did not respond within {15.0} seconds.")
        
        if stderr_output: # This will catch concurrent stderr from above, or if you move the check later
            print(f"Stderr from '{server_id}': {stderr_output.decode().strip()}")

        if not response_line:
            print("ERROR: Received empty response line from server's stdout.")
            try:
                stderr_output = await asyncio.wait_for(process.stderr.read(), timeout=1.0)
                if stderr_output:
                    print(f"ERROR: Stderr when stdout was empty: {stderr_output.decode().strip()}")
                    return QueryResponse(success=False, error=f"No response from server. Stderr: {stderr_output.decode().strip()}")
            except asyncio.TimeoutError:
                pass # No stderr either
            return QueryResponse(success=False, error="No response from server.")

        response_line_decode = response_line.decode().replace("\n", "")
        print (f"response_line_decode is {response_line_decode}")
        response_data = {}
        try:
            response_data = json.loads(response_line_decode)
            print(f"DEBUG: list_tools_stdio_server response_data {response_data}")
        except Exception as e:
            print (f"DEBUG: Not Valid Json '{response_line_decode}' with error {e}")
        result = response_data["result"] if "result" in response_data else {}
        tools = result["tools"] if "tools" in result else []
        tools = tool_mapper_json(tools)
        print (f"Available Tools From Server {server_id} tools {tools}")
        return QueryResponse(success=True, data=tools)
    except Exception as e:
        logger.error(e)
        return QueryResponse(success=False, error=f"Failed to process list_tools_stdio_server {e}")

async def robust_call_tool(client, tool_name, tool_arguments, retry_attempts=3):
    """
        Standard Output:
        content = result["content"] if "content" in result else []
        isError = result["isError"] if "isError" in result else False
    """
    result = None
    for attempt in range(retry_attempts):
        try:
            if not client.is_session_active: # Assuming a method to check connection status
                print(f"Attempting to reconnect (attempt {attempt + 1}/{retry_attempts})...")
                await client.reconnect()
            else:
                print (f"DEBUG: Client {client.name} is Session Active")
            result = await client.session.call_tool(tool_name, tool_arguments)
            print (f"DEBUG: robust_call_tool result {result}")
            break
        except Exception as e:
            logging.error(f"robust_call_tool failed with error {e}")
    return result

async def call_tools_base(server_id: str, tool_name: str, tool_arguments: Dict):
    """
       Base Call Tools Method, Supporting Both Stdio Server and SSE Servers
        
        Output: dict
            output["success"] = True 
            output["content"] = tool_results_text
            output["message"] = ""
    """
    global env
    # global _global_server_registry
    output = {}
    try:
        mcp_server_type = server_type_mcp_server_id(server_id)
        if mcp_server_type is None:
            logger.error(f"start_mcp_server_process {server_id} mcp_server_type is None..")
            return tools_result
        if mcp_server_type == MCP_TYPE_SSE:
            ## fetch MCP Server Client from global variables
            client = gv._global_mcp_client_dict[server_id] if server_id in gv._global_mcp_client_dict else None 
            if client is None:
                logger.error(f'Server {server_id} is not start in gv._global_mcp_client_dict, Started Servers {gv._global_mcp_client_dict.keys()}')            
            ## call tools with retries
            tool_result = await robust_call_tool(client, tool_name, tool_arguments)
            if tool_result is not None and not tool_result.isError:
                tool_results_text = tool_result.content[0].text if len(tool_result.content) > 0 else ""
                tool_results_text = str(tool_results_text)
                output[KEY_SUCCESS] = True 
                output[KEY_CONTENT] = tool_results_text
                output[KEY_MESSAGE] = ""
            else:
                output[KEY_SUCCESS] = False 
                output[KEY_CONTENT] = ""
                output[KEY_MESSAGE] = str(tool_result.content)
                print (f"DEBUG: After tool_result.content type {type(tool_result.content)} and tool_results_text {tool_result.content}")

        elif mcp_server_type == MCP_TYPE_STDIO:
            ## fetch MCP Server from Process List
            output = await call_tools_mcp_stdio(server_id, tool_name, tool_arguments)
        else:
            print (f"DEBUG: server_id {server_id} mcp_server_type {mcp_server_type} not supported...")
        print (f"DEBUG: server_id {server_id} mcp_server_type {mcp_server_type} output {output}...")            
        return output
    except Exception as e:
        logger.error(f"call_tools_base failed {e}")
        return output

async def stop_mcp_server_process(server_id: str):
    # global _global_server_registry
    
    if server_id not in gv._global_server_registry:
        return False, "Server ID not found."
    server_data = gv._global_server_registry[server_id]
    if server_data["status"] == "Off":
        return True, "Server already stopped."

    ## Close SSE Client
    if server_id in gv._global_mcp_client_dict:
         client = gv._global_mcp_client_dict[server_id]
         try:
             await client.cleanup()
             print (f"Stopping SSE Client {server_id} successfully...")
             server_data["status"] = "Off"
             return True, f"Server {server_id} stopped."
         except Exception as e:
             print (f"stop_mcp_server_process {e}")
             return False, f"Server {server_id} failed to stop."
    ## Close Local Stdio Server
    process = server_data["process"]
    if process:
        try:
            process.terminate() # Send SIGTERM
            # await asyncio.to_thread(process.wait, timeout=5) # Wait for graceful shutdown
            await process.wait()
            print(f"MCP Server '{server_id}' terminated.")
        except subprocess.TimeoutExpired:
            print(f"MCP Server '{server_id}' did not terminate gracefully, sending SIGKILL.")
            process.kill() # Force kill
            await asyncio.to_thread(process.wait) # Ensure it's killed
        except Exception as e:
            print(f"Error stopping server {server_id}: {e}")
            server_data["status"] = "Error" # Keep as error if stop failed unexpectedly
            return False, str(e)
        finally:
            if process.stdin: 
                process.stdin.close() 
                await process.stdin.wait_closed()
            server_data["process"] = None
    
    server_data["status"] = "Off"
    return True, "Server stopped."

async def init_mcp_servers_main_process(mcp_configs):
    """
        init mcp_servers from config file in the main process
    """
    connected_mcp_clients: Dict[str, MCPClient] = {}
    
    for name, config in mcp_configs.items():
        client = MCPClient(name=name)
        try:
            # We don't need the tools returned here if we're just storing the client
            await client.connect_to_server_config(config) 
            connected_mcp_clients[name] = client
            logger.info(f"MCPClient for '{name}' initialized and connected.")
        except Exception as e:
            logger.error(f"Server Connection Error for '{name}': {e}")
            # Ensure cleanup for failed connections too
            await client.cleanup() 

    mcp_server_cnt = len(connected_mcp_clients)
    mcp_server_names = list(connected_mcp_clients.keys())
    logger.info(f"Initialized MCP Server Size: {mcp_server_cnt}, Servers: {mcp_server_names}")

    return connected_mcp_clients

async def init_mcp_servers():
    """
    Initializes MCPClient instances and connects to servers based on configuration.
    Returns: Tuple[Dict[str, MCPClient], Dict[str, List[Any]]]
    """
    logger.info("Starting MCP server initialization...")

    ## 1.0 Load MCP Config
    print (f"DEBUG: Initializating MCP Server From mcp.json local file {MCP_CONFIG_LOCAL_JSON_PATH} and marketplace {MCP_CONFIG_MARKETPLACE_JSON_PATH}")
    mcp_configs_local = load_available_mcp_servers(MCP_CONFIG_LOCAL_JSON_PATH)
    mcp_configs_category_local = load_available_mcp_servers_folder(MCP_CONFIG_LOCAL_CATEGORY_JSON_PATH)
    mcp_configs_remote = load_available_mcp_servers(MCP_CONFIG_MARKETPLACE_JSON_PATH)

    print (f"DEBUG: mcp_configs_local {mcp_configs_local}")
    print (f"DEBUG: mcp_configs_category_local {mcp_configs_category_local}")
    print (f"DEBUG: mcp_configs_remote {mcp_configs_remote}")

    ## merge local and remoate
    mcp_configs_merge = {}
    mcp_configs_merge.update(mcp_configs_local)
    for config_batch in [mcp_configs_category_local, mcp_configs_remote]:
        for key, value in config_batch.items():
            if key not in mcp_configs_merge:
                mcp_configs_merge[key] = value
            else:
                continue
    ## 2.0 Load MCP Server Registry Status/On/Off
    server_registry = load_mcp_registry_json(mcp_configs_merge)
    print (f"DEBUG: init_mcp_servers from mcp_config.json server_registry {server_registry}")
    return server_registry

async def init_mcp_servers_tools():
    # Use local dictionaries within the async function, then return them
    
    print (f"DEBUG: Initializating Loading Tools Defination from file {MCP_TOOLS_FOLDER_PATH}")
    local_tools = load_available_tools(MCP_TOOLS_FOLDER_PATH)
    local_tools_size = len(local_tools)
    local_tools_keys = local_tools.keys()
    logger.info(f"Server tools from local server size: {local_tools_size}, from servers: {local_tools_keys}")

    return local_tools


async def init_start_mcp_server_local():
    """
    """
    if len(gv._global_server_registry) == 0:
        return
    result_log = {}
    for server_id, registry in gv._global_server_registry.items():
        config = registry["config"] if "config" in registry else {}
        process = registry["process"] if "process" in registry else None
        status = registry["status"] if "status" in registry else "Off"
        tools = registry["tools"] if "tools" in registry else []
        if status == "Off":
            success, message = await start_mcp_server_process(server_id)
            result_log[server_id] = {"success": success, "message": message}
        else:
            continue
    logger.info(f"init_start_mcp_server_local result_log {result_log}")

async def init_mcp_config_local_cache():
    """
        Inputs: Local Cache File ./mcp_config/files
    """
    # key: server_id, value: list of json
    mcp_config_json_dict = {}
    file_paths = read_file_traverse(MCP_CONFIG_LOCAL_CACHE_FOLDER, ".json")
    logging.info(f"init_mcp_config_local_cache Input File file_paths size {len(file_paths)}")
    for file_path in file_paths:
        fullname = file_path.split("/")[-1]
        filename_list = fullname.split(".")
        if len(filename_list) == 2:
            filename = filename_list[0]
            server_id_prefix = filename.replace("mcp_config_", "")
            # parse server_name
            server_name_items = server_id_prefix.split("_")
            server_id = ""
            if len(server_name_items) == 2:
                server_id = server_name_items[0] + "/" + server_name_items[1]
            elif len(server_name_items) > 2:
                server_id = server_name_items[0] + "/" + server_name_items[1]
            else:
                ## more than 1 "_" in username or repo_name
                continue
            if server_id != "":
                lines = read_file(filename)
                mcp_config = {}
                try:
                    mcp_config = json.loads("".join(lines))
                except Exception as e:
                    mcp_config = {}
                    #logger.error(f" Input mcp_config not valid json {e}")
                if server_id in mcp_config_json_dict:
                    cur_list = mcp_config_json_dict[server_id]
                    cur_list.append(mcp_config)
                    mcp_config_json_dict[server_id] = cur_list
                else:
                    mcp_config_json_dict[server_id] = [mcp_config]
    logging.info(f"init_mcp_config_local_cache mcp_config_json_dict size {len(mcp_config_json_dict)}")                    
    return mcp_config_json_dict

async def main_async(): # Renamed to avoid confusion with the synchronous main()
    # global _global_mcp_client_dict
    # global _global_server_tools_dict_local

    try:
        gv._global_mcp_client_dict, gv._global_server_tools_dict_local = await init_mcp_servers()
        
        logger.info(f"Final MCP Client Dict: {list(gv._global_mcp_client_dict.keys())}")
        logger.info(f"Final Server Tools Dict Local: {list(gv._global_server_tools_dict_local.keys())}")

        # You would typically do more work here, e.g., interact with the clients
        # For demonstration, let's keep the clients active for a bit before cleanup
        # await asyncio.sleep(5) 

    except Exception as e:
        logger.critical(f"An error occurred during main_async execution: {e}", exc_info=True)

# --- Pydantic Models for API ---
class ServerActionResponse(BaseModel):
    success: bool
    message: str
    server_id: str
    status: Optional[str] = None

class ServerMetaResponse(BaseModel):
    success: bool
    message: str
    server_id: str 
    schema: Dict

class InstallRequest(BaseModel):
    server_id: str # From marketplace, will become local ID
    name: str
    github_url: str
    install_command: str
    start_command: List[str] # e.g., ["python", "server.py"]
    tool_definitions_path: Optional[str] = None # Relative path within cloned repo, or URL

class QueryRequest(BaseModel):
    server_id: str
    tool_name: str
    tool_input: Dict

class QueryResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

@router.get("/api/servers/local")
async def list_local_servers():
    response_servers = []
    ## append meta information
    # global _global_server_registry

    try:
        print ("DEBUG: list_local_servers _global_server_registry size %d" % len(gv._global_server_registry))
        for sid, data in gv._global_server_registry.items():

            try:
                data_config = data["config"]
                process = data.get("process", None)
                status = data.get("status", "Off")
                tools = data.get("tools", [])

                name = data_config.get("name", sid)
                command = data_config.get("command", "")
                args = data_config.get("args", [])
                arguments = data_config.get("env", {})

                command_line = " ".join([command] + args)
                description = ""
                # status = "Off"
                tool_definitions_path = ""
                github_url = ""
                install_command_template = ""

                response_servers.append({
                    "id": sid,
                    "name": name, 
                    "description": install_command_template,
                    "status": status,
                    "command": command_line,
                    "tool_definitions_path": tool_definitions_path,
                    "tools": tools,
                    "github_url": github_url,
                    "install_command_template": install_command_template
                })
            except Exception as e2:
                logger.error(e2)

        return response_servers

    except Exception as e:
        logger.error(e)
        return []

@router.post("/api/server/{server_id}/enable", response_model=ServerActionResponse)
async def enable_server(server_id: str):
    # global _global_server_registry
    if server_id not in gv._global_server_registry:
        raise HTTPException(status_code=404, detail="Server not found")
    
    success, message = await start_mcp_server_process(server_id)


    server_dict = gv._global_server_registry[server_id] if server_id in gv._global_server_registry else {}
    status = server_dict["status"] if "status" in server_dict else ""

    return ServerActionResponse(
        success=success,
        message=message,
        server_id=server_id,
        status=status
    )

@router.post("/api/server/{server_id}/export", response_model=ServerMetaResponse)
async def export_server(server_id: str):
    # global _global_server_registry
    """
        server_dict schema:
        
        gv._global_server_registry[server_id]["process"] = process
        gv._global_server_registry[server_id]["status"] = "On"
        gv._global_server_registry[server_id]["tools"] = tools
    """
    if server_id not in gv._global_server_registry:
        raise HTTPException(status_code=404, detail="Server not found")
    
    server_dict = gv._global_server_registry[server_id] if server_id in gv._global_server_registry else {}
    status = server_dict["status"] if "status" in server_dict else ""
    tools = server_dict["tools"] if "tools" in server_dict else []
    config = server_dict["config"] if "config" in server_dict else {}
    
    success = True
    message = ""

    server_meta = {}
    server_meta["id"] = server_id
    server_meta["tools"] = tools
    server_meta["config"] = config

    return ServerMetaResponse(
        success=success,
        message=message,
        server_id=server_id,
        schema=server_meta,
    )

@router.post("/api/server/{server_id}/disable", response_model=ServerActionResponse)
async def disable_server(server_id: str):
    # global _global_server_registry

    if server_id not in gv._global_server_registry:
        raise HTTPException(status_code=404, detail="Server not found")

    server_dict = gv._global_server_registry[server_id] if server_id in gv._global_server_registry else {}
    status = server_dict["status"] if "status" in server_dict else ""

    success, message = await stop_mcp_server_process(server_id)
    return ServerActionResponse(
        success=success,
        message=message,
        server_id=server_id,
        status=status
    )

@router.post("/api/server/{server_id}/restart", response_model=ServerActionResponse)
async def restart_server(server_id: str):
    # global _global_server_registry

    if server_id not in gv._global_server_registry:
        raise HTTPException(status_code=404, detail="Server not found")

    await stop_mcp_server_process(server_id) # Ensure it's stopped first
    await asyncio.sleep(0.5) # Brief pause
    success, message = await start_mcp_server_process(server_id)
    
    server_dict = gv._global_server_registry[server_id] if server_id in gv._global_server_registry else {}
    status = server_dict["status"] if "status" in server_dict else ""

    return ServerActionResponse(
        success=success,
        message=message,
        server_id=server_id,
        status=status
    )

@router.post("/api/server/install", response_model=ServerActionResponse)
async def install_server_from_marketplace(req: InstallRequest):

    # global _global_server_registry

    server_id = req.server_id
    print(f"Received install request for server: {server_id} from {req.github_url}")
    print(f"Install command: {req.install_command}")
    print(f"Start command: {req.start_command}")
  
    # Simulate successful installation for now
    await asyncio.sleep(1) # Simulate work

    # Add to local mcp.json / server_registry
    if server_id in gv._global_server_registry:
        # Update existing config if it was somehow already there
        print(f"Server {server_id} already exists locally. Updating configuration.")
    
    new_server_config = {
        "id": server_id,
        "name": req.name,
        "description": f"Installed from marketplace: {req.github_url}",
        "command": req.start_command, # This command should be runnable after cd-ing into the server's dir
        "tool_definitions_path": req.tool_definitions_path, # Might be relative to cloned repo
        "github_url": req.github_url,
        "install_command_template": req.install_command, # Store what was used
        "cwd": os.path.join(INSTALLED_SERVERS_DIR, server_id, "repo_subdir") # Example: assumes cloned into 'repo_subdir'
    }
    _global_server_registry[server_id] = {
        "config": new_server_config,
        "process": None,
        "status": "Off",
        "tools": []
    }
    save_mcp_json(MCP_JSON_PATH) # Persist the new server configuration
    
    message = f"Server '{server_id}' installation simulated. Configuration added to local mcp.json."
    print(message)
    return ServerActionResponse(success=True, message=message, server_id=server_id, status="Off")

async def call_tools_mcp_stdio(server_id: str, tool_name: str, tool_input: Dict):
    """
        Wraper and MCP RPC of STDIO Server
    """
    output = {}
    output[KEY_SUCCESS] = False 
    output[KEY_CONTENT] = ""
    output[KEY_MESSAGE] = ""
    try:
        if server_id not in gv._global_server_registry:
            print (f"call_tool_mcp_stdio server_id {server_id} not in gv._global_server_registry keys|{gv._global_server_registry.keys()}")
            return result
        
        server_data = gv._global_server_registry[server_id]
        if server_data["status"] != "On" or not server_data["process"]:
            print (f"call_tool_mcp_stdio server_id {server_id} server status Off or process is none|{server_data}")
            return result

        mcp_server_type = server_type_mcp_server_id(server_id)
        if mcp_server_type is None or mcp_server_type != MCP_TYPE_STDIO:
            print (f"call_tool_mcp_stdio server_id {server_id} mcp_server_type {mcp_server_type} not supported, only MCP_TYPE_STDIO supported...")
            return result

        message = ""

        try:
            proc = server_data["process"]
            if not proc or not proc.stdin or not proc.stdout:
                print (f"call_tool_mcp_stdio server_id {server_id} process {proc} not found...")
                return result

            mcp_style_request = {
                "jsonrpc": "2.0",        # REQUIRED: Specifies the JSON-RPC version
                "id": str(uuid.uuid4()), # REQUIRED: A unique request identifier. Use uuid.uuid4() for uniqueness.
                "method": "tools/call",
                "params": {
                    "name": tool_name,      
                    "arguments": tool_input, 
                    "_meta": {
                        "progressToken": 1
                    }
                }
            }

            request_json_str = json.dumps(mcp_style_request) + "\n"
            
            print (f"DEBUG: request_json_str input {request_json_str} and proc {proc}")

            config = server_data.get("config", {})
            command = [config.get("command")] + config.get("args", [])
            command_line = " ".join(command)
            env_local = config.get("env", {})

            for key, value in env_local.items():
                env[key] = value

            proc.stdin.write(request_json_str.encode())
            await proc.stdin.drain()
            print("DEBUG: Data written to stdin and drained.")

            print("DEBUG: Waiting for response from stdout...")

            response_line = b''
            stderr_output = b'' # Initialize stderr_output

            try:
                # Set a reasonable timeout for the server response
                response_line = await asyncio.wait_for(proc.stdout.readline(), timeout=15.0) # Increased timeout for safety
                print(f"DEBUG: Received raw response line: {response_line!r}")

                # Even if stdout is received, check stderr for any concurrent warnings/errors
                try:
                    # Use read() with a very short timeout for stderr as it might not be a "line"
                    stderr_output = await asyncio.wait_for(proc.stderr.read(), timeout=0.1)
                    if stderr_output:
                        print(f"DEBUG: Stderr captured concurrently: {stderr_output.decode().strip()}")
                except asyncio.TimeoutError:
                    pass # No concurrent stderr to read within short timeout

            except asyncio.TimeoutError:
                print(f"ERROR: Timeout after {15.0} seconds waiting for stdout response from server '{server_id}'.")
                
                # If stdout times out, definitely check stderr to see if the server reported an error
                try:
                    print("DEBUG: Checking stderr for error messages after stdout timeout...")
                    stderr_output = await asyncio.wait_for(proc.stderr.read(), timeout=MCP_CALL_TOOL_TIMEOUT) # Give stderr more time to produce output
                    if stderr_output:
                        message = f"ERROR: Stderr from '{server_id}': {stderr_output.decode().strip()}"
                except asyncio.TimeoutError:
                    message = "DEBUG: No stderr output either within timeout."
                
                # Check if the process itself has terminated with an error code
                if proc.returncode is not None:
                    message = f"DEBUG: Server process exited with code: {proc.returncode} after timeout."

                message = f"Server '{server_id}' did not respond within {MCP_CALL_TOOL_TIMEOUT} seconds."
            
            # After attempting to read stdout, check for stderr in case there were issues during processing
            if stderr_output: # This will catch concurrent stderr from above, or if you move the check later
                # print(f"Stderr from '{server_id}': {stderr_output.decode().strip()}")

                message = f"Stderr from '{server_id}': {stderr_output.decode().strip()}"

            if not response_line:
                message = "ERROR: Received empty response line from server's stdout."
                try:
                    stderr_output = await asyncio.wait_for(proc.stderr.read(), timeout=1.0)
                    if stderr_output:
                        # print(f"ERROR: Stderr when stdout was empty: {stderr_output.decode().strip()}")
                        message = f"No response from server. Stderr: {stderr_output.decode().strip()}"
                        # return QueryResponse(success=False, error=f"No response from server. Stderr: {stderr_output.decode().strip()}")
                except asyncio.TimeoutError:
                    pass # No stderr either
                message = "No response from server."

            response_line_decode = response_line.decode().replace("\n", "")
            print (f"response_line_decode is {response_line_decode}")
            response_data = {}
            try:
                response_data = json.loads(response_line_decode)
                print(f"DEBUG: response_data {response_data}")
            except Exception as e:
                logger.error(e)

            ## process, list json
            result = response_data["result"] if "result" in response_data else {}

            content = result["content"] if "content" in result else []
            isError = result["isError"] if "isError" in result else False
            print (f"DEBUG: call_tools_mcp_stdio content type {type(content)} and content {content}")            

            # print (f"response line result {result} content {content}, isError {isError}")
            result_lines = []
            if not isError:
                for item_json in content:
                    if item_json['type'] == "text":
                        result_line = item_json['text'] if "text" in item_json else ""
                        result_lines.append(result_line)
                response_line = " ".join(result_lines)
                
                ## construct output
                message = "success"
                output[KEY_SUCCESS] = True 
                output[KEY_CONTENT] = response_line
                output[KEY_MESSAGE] = message
            else:
                output[KEY_SUCCESS] = False 
                output[KEY_CONTENT] = str(content)
                output[KEY_MESSAGE] = str(content)
        except json.JSONDecodeError:
            output[KEY_SUCCESS] = False 
            output[KEY_CONTENT] = ""
            output[KEY_MESSAGE] = "Failed to decode server response."

        except ConnectionError as e: # From MCPInteractionClient if used
            output[KEY_SUCCESS] = False 
            output[KEY_CONTENT] = ""
            output[KEY_MESSAGE] = f"Connection error: {e}"
        except RuntimeError as e: # From MCPInteractionClient or manual interaction
            output[KEY_SUCCESS] = False 
            output[KEY_CONTENT] = ""
            output[KEY_MESSAGE] = f"Runtime error: {e}"

        except Exception as e:
            # print(f"Error during query to {server_id}: {e}")
            output[KEY_SUCCESS] = False 
            output[KEY_CONTENT] = ""
            output[KEY_MESSAGE] = f"Error during query to {server_id}: {e}"
        print (f"DEBUG: call_tools_mcp_stdio {output}")

        return output
    except Exception as e:
        logger.error(f"call_tool_mcp_stdio with error {e}")
        return output

def check_tool_input(tool_input):
    if tool_input is None:
        return False, "check_tool_input Tool Input is Empty..."
    missing_fields = []
    for key, value in tool_input.items():
        if value is None:
            missing_fields.append(key)
        elif isinstance(value, str) and value.strip() == "":
            missing_fields.append(key)
        else:
            continue
    # all parameters are empty return
    if len(missing_fields) == len(tool_input):
        return False, f"check_tool_input tool_input {tool_input} all values empty, missing values {missing_fields} "
    return True, "check_tool_input Pass..."

def preprocess_tool_input(tool_input):
    if tool_input is None:
        return False, "check_tool_input Tool Input is Empty..."

    ## convert input params from int str, e.g. "2" to int 2
    tool_input_clean = {}
    for key, value in tool_input.items():
        if isinstance(value, str) and value.isdigit():
            value_clean = int(value)
            tool_input_clean[key] = value_clean
        else:
            tool_input_clean[key] = value
    return tool_input_clean

@router.post("/api/query", response_model=QueryResponse)
async def query_mcp_server(request: QueryRequest):
    """
        server_id type <class 'str'> and value amap-amap-sse
        tool_name type <class 'str'> and value maps_weather
        tool_input type <class 'dict'> and value {'city': 'New York', radius: 1000}
    """
    try:
        server_id = request.server_id 
        tool_name = request.tool_name
        tool_input_raw = request.tool_input
        print (f"DEBUG: Input server_id {server_id}|tool_name {tool_name} | tool_input {tool_input_raw}")

        if tool_name is None or tool_name == "":
            return QueryResponse(success=False, error=f"Server {server_id} tool_name is empty {tool_name}")
        
        tool_input = preprocess_tool_input(tool_input_raw)
        print (f"DEBUG: tool_input after preprocess_tool_input is {tool_input}")

        check, check_msg = check_tool_input(tool_input)
        if not check:
            return QueryResponse(success=False, error=check_msg)

        print (f"DEBUG: tool_input is {tool_input}")
        output = await call_tools_base(server_id, tool_name, tool_input)
        success = output[KEY_SUCCESS] if KEY_SUCCESS in output else False 
        content = output[KEY_CONTENT] if KEY_CONTENT in output else ""
        message = output[KEY_MESSAGE] if KEY_MESSAGE in output else ""
        if success:
            return QueryResponse(success=success, data=[content])
        else:
            return QueryResponse(success=False, error=message)
    except Exception as e:
        message = f"query_mcp_server server_id {request.server_id} failed with error {e}"
        return QueryResponse(success=False, error=message)

def update_local_file(file_folder, file_name, result):
    """
        ${file_folder}/file_name
        ${file_folder}/{timestamp}/file_name # for revision tracking
    """
    import os
    import time
    try:
        if not os.path.exists(file_folder):
            os.mkdir(file_folder)
        main_file = os.path.join(file_folder, file_name)

        timestamp = get_current_timestamp()
        temp_folder = os.path.join(file_folder, str(timestamp))
        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)
        temp_file = os.path.join(temp_folder, file_name)
        save_file(main_file, [json.dumps(result)])
        save_file(temp_file, [json.dumps(result)])
    except Exception as e:
        logger.error(e)
        logger.error("update_local_file failed...")

@router.get("/api/marketplace/config")
async def get_marketplace_config(server_ids: str):
    """
        /api/mcp_marketplace/v1/server/${owner_id}/${repo_name}
        ${owner_id}/${repo_name}

        # mcp_config_server
        {'puppeteer/puppeteer': {},
         'google-maps/google-maps': {},
         'mendableai/firecrawl-mcp-server': {'mcpServers': {'firecrawl-mcp': {'command': 'npx',
            'args': ['-y', 'firecrawl-mcp'],
            'env': {'FIRECRAWL_API_KEY': 'YOUR-API-KEY'}}}}}
    """
    if server_ids is None:
        logger.error("")
        return
    try:
        server_id_list = server_ids.split(",")
        server_id_cnt = len(server_id_list)
        logging.info(f"get_servers_marketplace_config input server_ids count {server_id_cnt} and server_ids {server_ids}")

        # key: config_name, value: config
        mcp_config_merge = {}
        server_config_available = {}

        # load from local cache
        server_id_hit_cache = []
        server_id_miss_cache = []
        for server_id in server_id_list:
            if server_id in gv._global_mcp_config_local_cache:
                server_id_hit_cache.append(server_id)
                mcp_config_list = gv._global_mcp_config_local_cache[server_id]
                # suitable environment: npx, docker, etc.
                if len(mcp_config_list) > 0:
                    mcp_config = mcp_config_list[0]
                    mcp_config_server = mcp_config[KEY_MCP_JSON_SERVERS] if KEY_MCP_JSON_SERVERS in mcp_config else {}
                    for key, config in mcp_config_server.items():
                        if key not in mcp_config_merge:
                            mcp_config_merge[key] = config
                            server_config_available[server_id]= 1
                        else:
                            # duplicate name
                            server_config_available[server_id]= 0
                            logger.error(f"Server found duplicate {key}, config {config}")
            else:
                server_id_miss_cache.append(server_id)
        logger.info(f"Server server_id_hit_cache {server_id_hit_cache}, server_id_miss_cache {server_id_miss_cache}")

        mcp_config_result = mcpm.load_config_batch(server_id_miss_cache, config_name="deepnlp_server")        
        for server_id, mcp_config in mcp_config_result.items():
            if len(mcp_config) > 0:
                mcp_config_server = mcp_config[KEY_MCP_JSON_SERVERS] if KEY_MCP_JSON_SERVERS in mcp_config else {}
                # key: e.g. firecrawl-mcp
                for key, config in mcp_config_server.items():
                    if key not in mcp_config_merge:
                        mcp_config_merge[key] = config
                        server_config_available[server_id]= 1
                    else:
                        # duplicate name
                        server_config_available[server_id]= 0
                        logger.error(f"Server found duplicate {key}, config {config}")
            else:
                server_config_available[server_id]= 0

        logging.info(f"get_servers_marketplace_config server_config_available {server_config_available}")    
        mcp_config_json = {}
        mcp_config_json[KEY_MCP_JSON_SERVERS] = mcp_config_merge
        update_local_file(MCP_MARKETPLACE_MCP_CONFIG_FOLDER, MCP_MARKETPLACE_MCP_CONFIG_NAME, mcp_config_json)
        logging.info(f"get_marketplace_config update_local_file {MCP_MARKETPLACE_MCP_CONFIG_FOLDER}/{MCP_MARKETPLACE_MCP_CONFIG_NAME}")
        return mcp_config_json

    except httpx.RequestError as e:
        print(f"Error fetching marketplace servers: {e}")
        logging.error(e)
        return {}
    except json.JSONDecodeError:
        logging.error(e)
        return {}
    except Exception as e:
        print(f"An unexpected error occurred while fetching marketplace servers: {e}")
        logging.error(e)
        return {}

def list_files_recursively_pathlib(top):
    file_path_all = []
    for file_path in Path(top).rglob('*'):
        file_path_all.append(file_path)
    return file_path_all

def get_all_mcp_server_config(folder_path):
    """
        folder_path: string, e.g. "./servers_list"
    """
    content_path_dict = {}
    for sub_folder in os.listdir(folder_path):
        sub_folder_path = os.path.join(folder_path, sub_folder)

        ## find serve file, walk through
        filepath_list = list_files_recursively_pathlib(sub_folder_path)
        server_file_path = ""
        server_file_name = ""
        for filepath_iter in filepath_list:
            filepath = str(filepath_iter)
            if "server.ts" in str(filepath) or "server.py" in str(filepath) or "mcp.js" in str(filepath) or "mcp.py" in str(filepath):
                server_file_path = filepath
                server_file_name = filepath.split("/")[len(filepath.split("/")) - 1]
                is_python = server_file_name.endswith('.py')
                is_js = server_file_name.endswith('.js')
                is_ts = server_file_name.endswith('.ts')

        if server_file_path != "":
            content_path_dict[sub_folder] = server_file_path
    return content_path_dict


async def initialize_and_run_mcp_clients_parallel(server_map: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Connects to a list of MCP servers in parallel using the mock mcp client
    and lists their tools.

    Args:
        server_map: A list of dictionaries, where each dictionary contains
                     server configuration details (name, command/url, args/etc.).

    Returns:
        server_tools_map, A dictionary where keys are server names and values are lists of tools.
    """
    tasks = []
    server_id_list = []
    for server_id, server_config in server_map.items():
        server_id_list.append(server_id)
        tasks.append(asyncio.wait_for(process_mcp_server(server_id, server_config), timeout= MCP_CONNECTION_TIMEOUT ))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    server_tools_map = {}
    for result in results:
        if isinstance(result, Exception):
            print(f"Error: {result}")
        else:
            server_name, tools = result
            tools_dict_list = [{ 
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in tools]
            server_tools_map[server_name] = tools_dict_list
    return server_tools_map


async def process_mcp_server(server_name, server_config: Dict[str, Any]) -> tuple[str, List[str]]:
    """
    Connects to a single MCP server using the mock mcp client,
    lists its tools, and disconnects.

    Args:
        server_config: Dictionary containing server configuration,
                       e.g., {'name': 'Server A', 'command': 'python', 'args': ['server_a.py']}
                       or {'name': 'Server X', 'url': 'http://localhost:8000'}

    Returns:
        A tuple containing the server name and a list of its tools.
    """
    tools: List[str] = []

    try:

        client = MCPClient(name=server_name)
        try:
            tools = await client.connect_to_server_config(server_config)
        except Exception as e2:
            print (f"DEBUG: Server Connection Error {server_name} {e2}")
    except Exception as e:
        print(f"An error occurred while processing {server_name}: {e}")
        tools = [] # Ensure tools is an empty list on error

    ## tempfile
    tools_json_list = [json.dumps({ 
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema
    }) for tool in tools]

    print (f"## process_mcp_server output server_name {server_name}, tools {tools}" )

    return server_name, tools

def run_search_tools_marketplace_pulsemcp():

    ## PulseMAP
    import mcp_marketplace
    mcp_marketplace.set_endpoint("pulsemcp")

    ## search by single query
    query = "map"
    result_query = mcp_marketplace.search(query=query, offset=0, count_per_page=100)

    total_count = result_query["total_count"] if "total_count" in result_query else []
    servers = result_query["servers"] if "servers" in result_query else []

    servers_source = [server["source_code_url"] for server in servers]
    servers_names = [server["name"] for server in servers]

    print (f"DEBUG: Marketplace Search Query '{query}', total_count {total_count}, Result names {servers_names}")

    ## parallel calling
    ## batch process, search by querys
    query_list = ["map", "chart"]
    params_list = [{"query": query, "offset":0, "count_per_page":20} for query in query_list]
    results = mcp_marketplace.search_batch(params_list)
    for (params, result) in results:
        query = params["query"] if "query" in params else ""
        items = result["servers"] if "servers" in result else []
        item_names = [item["name"] for item in items]
        item_cnt = len(items)
        print (f"DEBUG: Mcp Marketplace Search Query {query}, Get Item Count {item_cnt}, Get Names {item_names}")

def run_search_tools_marketplace_deepnlp():

    ## PulseMAP
    import mcp_marketplace as mcpm
    mcpm.set_endpoint("deepnlp")
    
    ## search by query
    query = "map"
    result_query = mcpm.search(query=query, mode="dict", page_id=0, count_per_page=100)

    item_map = result_query["item_map"] if "item_map" in result_query else {}
    servers = []
    for key, values in item_map.items():
        servers.extend(values)

    servers_source = [server["website"] for server in servers]
    servers_ids = [server["id"] for server in servers]
    servers_names = [server["content_name"] for server in servers]
    group_cnt_map = result_query["group_cnt"] if "group_cnt" in result_query else {}
    group_total_map = result_query["group_total"] if "group_total" in result_query else {}
    print (f"DEBUG: Search Query '{query}', group_cnt_map {group_cnt_map}, group_total_map {group_total_map}, servers_ids {servers_ids}")

    ## search by id
    unique_id = "google-maps/google-maps"
    result_id = mcpm.search(id=unique_id, mode="list")
    print (f"DEBUG: Search By ID '{unique_id}', Result {result_id}")

    ## search by category
    category = "map"
    result_cate = mcpm.search(category=category, mode="list")
    print (f"DEBUG: Search By ID '{category}', Result {result_cate}")

    ## batch process, search by querys
    query_list = ["map", "chart"]
    params_list = [{"query": query, "page_id":0, "count_per_page":50} for query in query_list]
    results = mcpm.search_batch(params_list)
    for (params, result) in results:
        query = params["query"] if "query" in params else ""
        items = result["items"] if "items" in result else []
        item_names = [item["content_name"] for item in items]
        item_cnt = len(items)
        print (f"DEBUG: Mcp Marketplace Search Query {query}, Get Item Count {item_cnt}, Get Names {item_names}")

def run_search_tools_marketplace():
    """
    """

    ## PulseMAP
    run_search_tools_marketplace_pulsemcp()
    
    ## DeepNLP Endpoint
    run_search_tools_marketplace_deepnlp()



def execute_llm_tool_call(tool_call_request, mcp_config):
    """
        args:
            tool_call_request
            mcp_config: dict
                method: get the server_name and tool_fuction
        return:
            response: response
    """
    method = tool_call_request.get("method")
    params = tool_call_request.get("params", {})
    request_id = tool_call_request.get("id")

    if not method:
        print("Error: Tool call method missing.")
        return None
    try:
        server_name, tool_function = method.split("/", 1)
    except ValueError:
        print(f"Error: Invalid method format: {method}")
        return None

    server_config = mcp_config.get(KEY_MCP_JSON_SERVERS, {}).get(server_name)

    if not server_config:
        print(f"Error: MCP server '{server_name}' not found in configuration.")
        return None

    server_is_command = True if server_config.get("command") is not None else False
    server_is_url = True if server_config.get("url") is not None else False
    ## local
    server_type = ""
    if server_is_command:
        server_type = "command"
    elif (not server_is_command and server_is_url):
        server_type = "sse"
    else:
        server_type = "command"

    # run command
    if server_type == "command":
        command_template = server_config.get("command")
        args = server_config.get("args")
        env_vars = server_config.get("env", {})

        if not command_template:
            print(f"Error: Command not specified for server '{server_name}'.")
            return None

        command_to_run = [command_template]

        for arg in args:
            command_to_run.append(arg)

        # Append parameters from the LLM call (simplified approach)
        for key, value in params.items():
            command_to_run.append(f"--{key}={value}") # Example: --param1=value1

        print(f"Executing command: {' '.join(command_to_run)}")

        try:
            process_env = os.environ.copy()
            process_env.update(env_vars)
            result = subprocess.run(command_to_run, capture_output=True, text=True, env=process_env, check=True)
            print("Command stdout:", result.stdout)
            print("Command stderr:", result.stderr)

            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "output": result.stdout # Or a structured result based on tool output
                }
            }
            return response

        except FileNotFoundError:
            print(f"Error: Command not found: {command_to_run[0]}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601, # Method not found in JSON-RPC spec
                    "message": f"Tool command not found: {command_to_run[0]}"
                }
            }
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": 1, # Generic error code
                    "message": f"Tool execution failed: {e.stderr}"
                }
            }
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603, # Internal error in JSON-RPC spec
                    "message": f"An internal error occurred during tool execution: {e}"
                }
            }

    else:
        print(f"Error: Unsupported server type '{server_type}' for server '{server_name}'.")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601, # Method not found
                "message": f"Unsupported MCP server type: {server_type}"
            }
        }

def main():
    try:
        import anyio
        anyio.run(main_async)
        print (f"DEBUG: _global_mcp_client_dict size {_global_mcp_client_dict}")
        print (f"DEBUG: _global_server_tools_dict_local size {_global_server_tools_dict_local}")

    except ImportError:
        logger.warning("anyio not found, falling back to asyncio.run(). "
                       "Consider installing anyio (`pip install anyio`) for better "
                       "compatibility with mcp and robust async cancellation.")
        asyncio.run(main_async())
    except Exception as e:
        logger.critical(f"Unhandled exception in main execution: {e}", exc_info=True)

if __name__ == '__main__':
    main()
