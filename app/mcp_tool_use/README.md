## MCP Tool Use Agent of Open MCP Marketplace

Try our AI Agent MCP Tool Use App at [https://agent.deepnlp.org/agent/mcp_tool_use](https://agent.deepnlp.org/agent/mcp_tool_use)

Use Map/Finance/Browser/Search and many other tools with LLM support.

## Weather Demo
q = What's the weather like in Shanghai?

## Trip Planning Demo
q = Find route from JFK Aiport to Time Square
![Route Planning](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/app/mcp_tool_use/docs/route_planning_mcp_v2.jpg)

## Web Search Demo
q = NBA 2025 Draft
![Search MCP](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/app/mcp_tool_use/docs/search_mcp.jpg)


This app is an open-source MCP Tool Use Agent (equivalent to MCP features of Cline, Cursor, Claude Desktop, etc), which contain a ChatGPT/Claude/Gemini Style Chatbot UI and MCP client integration (Management/Start/Disable/Export servers) of various MCP servers and tools. To get MCP configs and tools schema files from DeepNLP MCP Marketplace, please Visit at: https://www.deepnlp.org/store/ai-agent/mcp-server


**Features**
1. **Chatbot/AI search Web App**: Production-ready app which supports various models chat completion and function calling API, including Claude, GPT, Qwen, Gemini, etc. 
2. **MCP Client Integration**: MCP Servers Management, Installation from mcp_config.json file, MCP Server Tool inspector and MCP playground to help you can debug MCP servers.
3. **Explore MCP Servers from Open MCP Marketplace**: Search relevant MCP servers configs, tools meta using keywords of dispatching agent.


**Demo: Route Planning using Google Map MCP**

![Route Planning](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/app/mcp_tool_use/docs/route_planning_mcp_v2.jpg)

**MCP Admin and Playground**
![MCP Marketplace Tool Use](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/app/mcp_tool_use/docs/marketplace_mcp_admin.jpg?raw=true)

To Get MCP Configs and Tools Please Visit MCP Marketplace at: https://www.deepnlp.org/store/ai-agent/mcp-server

### 1. Quick Start

**Install Requirements**
```
pip install fastapi pydantic dotenv asyncio httpx mcp_marketplace uuid 
```
or 
```
pip install -r requirements.txt
```

**Start Service**

Under the root folder of the app ./mcp_tool_use, run below command:

```
uvicorn src.app:app --port 5000
```

Open browser and visit http://localhost:5000/mcp, and you will see a MCP admin page to enable, disable, restart and export available tools.

**Config Management mcp_config.json**

Go to <a>http://localhost:5000/mcp/config</a> and you can find the local config file of MCP servers <code>mcp_config.json</code>. You can click edit button and save your latest change. Remember to restart the servers.

<code>mcp_config.json</code> file is located in the path "./data/mcp/config/mcp_config.json".

```
{
    "mcpServers": {
        "google-maps": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-google-maps"],
            "env": {
                "GOOGLE_MAPS_API_KEY": "<YOUR_API_KEY>"
            }
        },
        .,,
    }
}
```

**Start a Few MCP Servers**
For example, you can start google-maps,amap-amap-sse,baidu-map in the default config file. Without the Keys the agent can still decide the tools and parameters.
To make the MCP work, you need to setup the keys as in the mcp introduction.

![MCP Marketplace Tool Use](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/app/mcp_tool_use/docs/marketplace_mcp_admin.jpg?raw=true)


**environment settings**

Manage and Config the API keys in .env file

```
QWEN_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
CLAUDE_API_KEY=your_key_here
```

### 2. Usage 
#### 2.1 UI to Run MCP Tool Use Function Call

**Tool Example 1: Route Planning**

```
prompt: Find the best route from JFK Airport to Times Square in New York
Tools: Google Map/maps_directions
```

![Route Planning](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/app/mcp_tool_use/docs/route_planning_mcp_v2.jpg)


Tools Parameters
```
{
    "destination": "Times Square, New York",
    "mode": "driving",
    "origin": "JFK Airport, New York"
}
```


**Tool Example 2: Realtime Financial Data API Calling**


```
prompt: Tesla and Microsoft Which one has higher stock price change today?
Tools: get_stock_price_global_market
```

Tool Calling 
![Financial Data](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/app/mcp_tool_use/docs/financial_mcp_1.jpg)

Generated Response
![Financial Data](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/app/mcp_tool_use/docs/financial_mcp_2.jpg)


**Tool Example 3: Browser Use of Navigation and Screenshot**

```
prompt: Please navigate to this webpage https://arxiv.org/list/cs/new and take a screen shot
Tools: puppeteer_navigate -> puppeteer_screenshot
```

![Browser Use](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/app/mcp_tool_use/docs/browser_user_mcp.jpg)



**Tool Example 4: Search**

```
Prompt: Use Google Custom Search to search for the most recent news of NBA drafts in 2025.
Tools: search
```


![Search MCP](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/app/mcp_tool_use/docs/search_mcp.jpg)



#### 2.2 Programmable way to run MCP Tool Use Function Call

**CURL**

Once you started the service and run the target mcp server, you can run the tools calls through the REST API.

Let's say you want to post to server: <code>puppeteer</code> and test tools: <code>puppeteer_navigate</code> to navigate chrome to a webpage.

Endpoint: http://127.0.0.1:5000/api/query


```

curl -X POST -H "Content-Type: application/json" -d '{
    "server_id": "puppeteer",
    "tool_name": "puppeteer_navigate",
    "tool_input": {
        "url": "https://arxiv.org/list/cs/new"
    }
}' http://127.0.0.1:5000/api/query

```

Result 
```
{"success":true,"data":["Navigated to https://arxiv.org/list/cs/new"],"error":null}%
```


**REST GET/POST Request By Python/Typescript/etc**

For example, post request to MCP: amap-amap-sse, Tool: Get Weather and get local weather. You need to start mcp server 'amap-amap-sse' before running command line.

cd ./tests

```
python run_mcp_request.py

## define input_params
        input_params = {
            "server_id": "amap-amap-sse", 
            "tool_name": 'maps_weather',
            "tool_input": {
                "city": "乌鲁木齐"
            }
        }

```

Result
```
{'success': True, 'data': ['{"city":"乌鲁木齐市","forecasts":[{"date":"2025-06-30","week":"1","dayweather":"多云","nightweather":"多云","daytemp":"31","nighttemp":"20","daywind":"西北","nightwind":"西北","daypower":"1-3","nightpower":"1-3","daytemp_float":"31.0","nighttemp_float":"20.0"},{"date":"2025-07-01","week":"2","dayweather":"多云","nightweather":"多云","daytemp":"28","nighttemp":"20","daywind":"西北","nightwind":"西北","daypower":"1-3","nightpower":"1-3","daytemp_float":"28.0","nighttemp_float":"20.0"},{"date":"2025-07-02","week":"3","dayweather":"多云","nightweather":"多云","daytemp":"28","nighttemp":"20","daywind":"西北","nightwind":"西北","daypower":"1-3","nightpower":"1-3","daytemp_float":"28.0","nighttemp_float":"20.0"},{"date":"2025-07-03","week":"4","dayweather":"多云","nightweather":"晴","daytemp":"30","nighttemp":"21","daywind":"西北","nightwind":"西北","daypower":"1-3","nightpower":"1-3","daytemp_float":"30.0","nighttemp_float":"21.0"}]}'], 'error': None}
```

### 3. Contributing

Please commit issue or create PR to this app.
Integration of your MCP servers/tools are welcomed.



