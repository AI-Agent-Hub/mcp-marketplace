## MCP Tool Use App with MCP Marketplace Integration

This app is an AI client supports MCP Admin of (Start/Disable/Export) MCP servers of SSE and Stdio Server. And a front end ChatGPT style chatbot for
you to test your queries.

![MCP Marketplace Tool Use](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/app/mcp_tool_use/docs/marketplace_mcp_admin.jpg?raw=true)

To Get MCP Configs and Tools Please Visit MCP Marketplace at: https://www.deepnlp.org/store/ai-agent/mcp-server


### Quick Start

**Start Service**

Under the root folder of the app mcp_tool_use, run below command

root_folder: ./mcp_tool_use

```
uvicorn src.app:app --port 5000

```

Visit http://localhost:5000/mcp, And you will see a MCP admin page to start, disable and export available tools.


### Chat with MCPs

**prompt**
- What's the weather like in New York?
- Please help me get the stock price of Microsoft and Tesla today and compare which one has the larger increase or decrease?



**API to Call MCP Tools**

Post request to local API and get result

cd ./tests

```
python run_mcp_request.py

```


