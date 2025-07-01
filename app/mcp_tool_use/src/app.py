import logging
import json
import time
import asyncio
from typing import Dict, List, Any
import uvicorn

import os
import aiofiles

from fastapi import FastAPI
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi import Path as APIPath
from fastapi import HTTPException

from pydantic import BaseModel
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from .constants import *
from .core import workflow
from .utils import read_file

from .global_variables import MCPClient
from .mcp_servers import init_mcp_servers, init_mcp_servers_tools, init_mcp_config_local_cache, start_mcp_server_process, stop_mcp_server_process, init_start_mcp_server_local
from . import global_variables as gv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


STATIC_DIR = "web/static"
TEMPLATES_DIR = "web/templates"
PLUGIN_DIR = "web/plugin"


load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    await startup_event()
    yield
    print("Application shutdown...")

    await shutdown_event()

from .mcp_servers import router as mcp_server_router
routers = [mcp_server_router]

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/plugin", StaticFiles(directory=PLUGIN_DIR), name="plugin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)

templates = Jinja2Templates(directory=TEMPLATES_DIR)

plugins = Jinja2Templates(directory=PLUGIN_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """
    """
    mcp_marketplace_servers = {}
    try:
        item_map = gv._global_mcp_marketplace_preinstall_servers["item_map"] if "item_map" in gv._global_mcp_marketplace_preinstall_servers else {}
        display_servers_onload = item_map["Map"] if "Map" in item_map else []
        mcp_marketplace_servers["Map"] = display_servers_onload
        print (f"DEBUG: mcp_marketplace_servers {mcp_marketplace_servers}")

    except Exception as e:
        logger.error(e)
    finally:
        print ("Ending...")

    return templates.TemplateResponse("index.html", {"request": request, "mcp_marketplace_servers": mcp_marketplace_servers})

@app.get("/mcp", response_class=HTMLResponse)
async def mcp_page(request: Request):
    """
        MCP_CONFIG_FOLDER = DATA_DIR/ "mcp/config/category"
        "./data/mcp/config"
    """
    items = []
    try:
        # BASE_DIR = MCP_CONFIG_FOLDER
        # path = ""
        subfolder = ""
        target_path = os.path.join(MCP_CONFIG_FOLDER, subfolder)
        if not os.path.exists(target_path):
            raise HTTPException(status_code=404, detail="path not exists")
        for item in os.listdir(target_path):
            item_path = os.path.join(target_path, item)
            # skipped item not for display
            item_split_tuples = item.split(".")
            item_extension = ""
            if len(item_split_tuples) >= 2:
                item_extension = item_split_tuples[-1].lower()
            else:
                item_extension = ""
            print (f"DEBUG: mcp_subfolder_view Skipped Item {item}")
            print (f"DEBUG: mcp_page item_extension {item_extension}")

            if item_extension in MCP_FOLDER_SKIPPED_EXTENSION:
                continue
            is_dir = os.path.isdir(item_path)
            items.append({
                "name": item,
                "path": os.path.join(subfolder, item),
                "uri": MCP_BASE_CONFIG_URI + "/" + os.path.join(subfolder, item),            
                "is_dir": is_dir,
                "size": os.path.getsize(item_path) if not is_dir else 0
            })
        print (f"DEBUG: Output Items {items}")
    except Exception as e:
        print (f"mcp_page failed {e}")
    
    return plugins.TemplateResponse("mcp_local_admin/templates/index.html", 
        {
            "request": request, 
            "items": items, 
            "tab_id": "admin"
        })

@app.get("/mcp/{tab_id}", response_class=HTMLResponse)
async def mcp_page_tab(request: Request, tab_id: str = ""):
    """
        MCP_CONFIG_FOLDER = DATA_DIR/ "mcp/config/category"
        "./data/mcp/config"
    """
    items = []
    try:
        # BASE_DIR = MCP_CONFIG_FOLDER
        # path = ""
        subfolder = ""
        target_path = os.path.join(MCP_CONFIG_FOLDER, subfolder)
        if not os.path.exists(target_path):
            raise HTTPException(status_code=404, detail="path not exists")
        for item in os.listdir(target_path):
            item_path = os.path.join(target_path, item)
            # skipped item not for display
            item_split_tuples = item.split(".")
            item_extension = ""
            if len(item_split_tuples) >= 2:
                item_extension = item_split_tuples[-1].lower()
            else:
                item_extension = ""
            print (f"DEBUG: mcp_subfolder_view Skipped Item {item}")
            print (f"DEBUG: mcp_page item_extension {item_extension}")

            if item_extension in MCP_FOLDER_SKIPPED_EXTENSION:
                continue
            is_dir = os.path.isdir(item_path)
            items.append({
                "name": item,
                "path": os.path.join(subfolder, item),
                "uri": MCP_BASE_CONFIG_URI + "/" + os.path.join(subfolder, item),            
                "is_dir": is_dir,
                "size": os.path.getsize(item_path) if not is_dir else 0
            })
        print (f"DEBUG: Output Items {items}")
    except Exception as e:
        print (f"mcp_page failed {e}")
    
    return plugins.TemplateResponse("mcp_local_admin/templates/index.html", 
        {
            "request": request, 
            "items": items,
            "tab_id": tab_id
        })

@app.get("/mcp/config/{sub_path:path}")
async def mcp_subfolder_view(request: Request, sub_path: str = APIPath(..., regex=r"^[\w\-./]+$")):
    if ".." in sub_path:
        raise HTTPException(400, "Invalid path")
    
    target_path = os.path.join(MCP_CONFIG_FOLDER, sub_path)
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="path not exists")
    items = []
    for item in os.listdir(target_path):
        item_path = os.path.join(target_path, item)

        item_split_tuples = item.split(".")
        item_extension = ""
        if len(item_split_tuples) >= 2:
            item_extension = item_split_tuples[-1].lower()
        else:
            item_extension = ""
        print (f"DEBUG: mcp_page item_extension {item_extension}")
        if item_extension != "" and item_extension in MCP_FOLDER_SKIPPED_EXTENSION:
            print (f"DEBUG: mcp_subfolder_view Skipped Item {item}")
            continue
        is_dir = os.path.isdir(item_path)
        items.append({
            "name": item,
            "path": os.path.join(sub_path, item),
            "uri": MCP_BASE_CONFIG_URI + "/" + os.path.join(sub_path, item),
            "is_dir": is_dir,
            "size": os.path.getsize(item_path) if not is_dir else 0
        })
    
    print (f"mcp_subfolder_view {items}")

    return plugins.TemplateResponse("mcp_local_admin/templates/index.html", 
        {
            "request": request,
            "items": items,
            "tab_id": "config",
            "current_path": sub_path
        })

@app.get("/file-content")
async def get_file_content(path: str):
    """"""
    try:
        file_path = os.path.join(MCP_CONFIG_FOLDER, path)
        
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="File Not Found...")
        
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
        
        # print (f"DEBUG: get_file_content path {path} and content {content}")
        return {"content": content, "path": path}
    except Exception as e:
        print (f"get_file_content failed {e}")
        return {"content": "", "path": ""}

@app.post("/save-file")
async def save_file(request: Request):
    """"""
    try:
        data = await request.json()
        file_path = os.path.join(MCP_CONFIG_FOLDER, data['path'])
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="File Not Found...")
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(data['content'])
        
        return {"status": "success", "path": data['path']}

    except Exception as e:
        print (f"Failed to save_file {e}")
        return {"status": "fail", "path": ""}

CHUNK_JS_SEPARATOR = "\n"

@app.post('/api/chat')
async def chat(messages: list = Body(...), kwargs: dict = Body(...)): 
    try:
        logger.info(f"/api/chat Received messages: {messages} and kwargs {kwargs}")        
        if (len(messages)) == 0:
            logging.error("Input messages is Empty and len is 0 ...")            
            return StreamingResponse(content=None, media_type="text/event-stream", status_code=204)

        message = messages[len(messages)-1]
        query = message["content"] if "content" in message else ""
        role = message["role"] if "role" in message else ""
        if query == "":
            logging.error("Input Query is Empty...")
            return StreamingResponse(content=None, media_type="text/event-stream", status_code=204)

        response_type = kwargs["response_type"] if "response_type" in kwargs else RESPONSE_TYPE_TEXT
        logger.info(f"Received kwargs Input Response Route: {response_type}")

        kwargs["mcp_client_dict"] = gv._global_mcp_client_dict
        kwargs["server_tools_dict_local"] = gv._global_server_tools_dict_local
        
        response_generator = main_entry(messages, kwargs)
        return StreamingResponse(response_generator, media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Error in /api/chat: {e}", exc_info=True)
        return StreamingResponse(json.dumps({"type": "system", "message": f"Internal server error: {str(e)}"}) + CHUNK_JS_SEPARATOR, media_type="text/event-stream")

async def main_entry(messages: List[Dict[str, Any]], kwargs: Dict[str, Any]):
    """
    Asynchronous generator for streaming chat responses.
    """
    try:
        logger.info(f"main_entry input: {messages}")
        async for chunk in deep_tool_use_agent(messages, kwargs):
            yield chunk + CHUNK_JS_SEPARATOR

    except Exception as e:
        logger.error(f"Error in main_entry: {e}", exc_info=True)
        yield json.dumps({"type": "system", "message": f"Error during processing: {str(e)}"}) + CHUNK_JS_SEPARATOR
    finally:
        # Final empty chunk or closing message for the stream
        yield json.dumps({"type": "system", "message": "Stream finished."}) + CHUNK_JS_SEPARATOR

async def deep_tool_use_agent(messages: List[Dict[str, Any]], kwargs: Dict[str, Any]):
    """
    Asynchronous generator for Claude tool use agent.
    """
    try:
        logger.info(f"deep_tool_use_agent_claude input: {messages}")

        # Ensure client_claude.claude_tooluse_loop is an async generator
        async for chunk in workflow.tooluse_loop_with_confirmation(messages, kwargs):
            yield chunk

    except Exception as e:
        logger.error(f"Error in deep_tool_use_agent_claude: {e}", exc_info=True)
        yield json.dumps({"type": "system", "message": f"Error in tool use agent: {str(e)}"})

# Mock Claude API streaming generator (synchronous for demonstration)
def mock_claude_stream(messages: List[Dict[str, Any]]):
    yield json.dumps({"type": "system", "message": "Processing your request..."}) + "\n"
    time.sleep(0.1) # Shorter sleep for faster testing
    for chunk_text in ["Hello! ", "This is a ", "streamed response from Claude (mock)."]:
        yield json.dumps({"type": "assistant", "format": "text", "content": chunk_text}) + "\n"
        time.sleep(0.1)
    yield json.dumps({"type": "system", "message": "Response complete (mock)."}) + "\n"

def init_global_config():
    """
        Loading MCP config Path
    """
    lines = read_file(MCP_MARKETPLACE_MCP_SERVER_META_PATH)
    servers_json = {}
    try:
        servers_json = json.loads("".join(lines))
    except Exception as e:
        logger.error(e)
    return servers_json

async def startup_event():
    """
    Uvicorn startup hook to initialize MCP clients.
    This runs once when the Uvicorn worker process starts.
    """
    logger.info("Uvicorn: Running startup event - Initializing MCP servers...")
    try:
        gv._global_server_registry = await init_mcp_servers()
        gv._global_server_tools_dict_local = await init_mcp_servers_tools()
        gv._global_mcp_config_local_cache = await init_mcp_config_local_cache()

        logger.info(f"Uvicorn: Server Registry Config populated with: {list(gv._global_server_registry.keys())}")
        logger.info(f"Uvicorn: Server Tools Dict Local populated with: {list(gv._global_server_tools_dict_local.keys())}")
        logger.info(f"Uvicorn: Server MCP Config Local Cache with Size: {len(gv._global_mcp_config_local_cache.keys())}")

        gv._global_mcp_marketplace_preinstall_servers = init_global_config()
        logger.info(f"init_global_config gv._global_mcp_marketplace_preinstall_servers size {len(gv._global_mcp_marketplace_preinstall_servers)}")

        if MCP_INIT_AUTO_ENABLE:     
            logger.info(f"init_start_mcp_server_local MCP_INIT_AUTO_ENABLE true")
            await init_start_mcp_server_local()
        else:
            logger.info(f"MCP_INIT_AUTO_ENABLE false")

    except Exception as e:
        logger.critical(f"Uvicorn: Failed to initialize MCP servers at startup: {e}", exc_info=True)

async def shutdown_event():
    """
    Uvicorn shutdown hook to clean up MCP clients.
    This runs once when the Uvicorn worker process shuts down.
    """
    logger.info("Uvicorn: Running shutdown event - Cleaning up MCP clients...")
    # clean up registry
    print("Application shutdown...")
    for server_id in list(gv._global_server_registry.keys()): # list keys because stop modifies registry status
        if gv._global_server_registry[server_id]["status"] == "On":
            print(f"Stopping server {server_id} on shutdown...")
            await stop_mcp_server_process(server_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
