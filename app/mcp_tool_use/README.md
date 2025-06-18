## MCP Tool Use App with MCP Marketplace Integration

This demo contains a web page of MCP Tools Admin of (Start/Disable/Export) MCP servers of SSE and Stdio Server. And a front end ChatGPT style chatbot for
you to test your queries.


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


