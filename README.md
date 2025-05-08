## Open MCP Marketplace | AI Agent Marketplace Plugin from DeepNLP

The open source MCP Marketplace plugin is a pure web project (html/js/css), which will display available MCP tools meta and config files in the frontend, so that user can choose, manage and install their preferred MCP tools in similar functions (Map, Payment, Fetch). Itcan be easily integrated to your AI apps, and upgrade your AI Agent tools use ability (LLM).

**KEY Features**

- Html-Based Agent Button: Show the Panel of MCP Tools from all the open web directory MCP marketplace (e.g. deepnlp, pulsemcp).
- Browser and Pagination: User can browser the MCP Tools by Category and use pagination to navigate
- Select and Install MCP servers: Users can choose which MCP tools to perform tasks from mcp tools marketplace with similar features, such as Map Location, Search, Fetch, Payment, etc. 
- Autonomous MCP Tools Dispatcher: Your LLM/agent can also benifit from dispatching the query/prompt to the MCP tools, making decision on which tools to choose. The decision or dispatcher agent functions with more than the description text, but also the genunie user reviews score (0-5), ratings and call numbers statistics.

![Open MCP Marketplace DeepNLP Panel](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/docs/remote_mcp_server.jpg)

Related
- [MCP Marketplace DeepNLP](http://www.deepnlp.org/store/ai-agent/mcp-server)
- [MCP Marketplace PulseMCP](https://www.pulsemcp.com/)
- [AI Agent Marketplace](http://www.deepnlp.org/store/ai-agent)

## Update: Support Marketplace and API

| Source | value | description |
| --- | ---- | ---- |
| deepnlp.org | http://www.deepnlp.org/api/mcp_marketplace/v1 | http://www.deepnlp.org/workspace, This endpoint is for demo and debug purpose only and may not have enough quota for production use. For production worthy endpoint please register the API keys |
| pulsemcp.com | https://api.pulsemcp.com/v0beta/servers | Website: https://www.pulsemcp.com/api |


## 1. Integration 

If you have a chatbot or ai search engine box and you want to integrate the MCP tools integration plugin to your app, you can follow the below step and an AI Search Engine Demo

#### Demo: AI Search with MCP Marketplace Plugin 

Go to file ./app/ai_search/index.html and open the index.html with your browser.

**Step 1**. Integrate AI Search Engine Demo with MCP Marketplace Plugin
![Open MCP Marketplace DeepNLP Panel](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/docs/remote_mcp_server.jpg)

**Step 2**. Choose the Tools and Test the Tools Choosen

![Open MCP Marketplace DeepNLP System Prompt](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/docs/remote_mcp_server_system_prompt.jpg)


## 2. Install

#### Clone Project and Copy The MCP Marketplace Plugin Folder

```
git clone https://github.com/AI-Agent-Hub/mcp-marketplace.git
cd ./open_mcp_marketplace

## Project Structure and Copy Files to Your Project

./plugin/mcp_marketplace/
./plugin/mcp_marketplace/index.html
./plugin/mcp_marketplace/scripts.js
./plugin/mcp_marketplace/styles.css

```


#### Set Endpoint of the MCP Plugin info json is fetching

Go to file ./plugin/mcp_marketplace/scripts.js and change the endpoint provider by config

```

// API: deepnlp
const config = getConfigByName("deepnlp");

// API: pulsemcp
const config = getConfigByName("pulsemcp");


```

#### DeepNLP Endpoint

Demo URL: http://www.deepnlp.org/api/mcp_marketplace/v1?field=MCP%20Server

| key | value | 
| --- | ---- | 
| endpoint | http://www.deepnlp.org/api/mcp_marketplace/v1 |
| inputParams | {"field": "MCP SERVER"} |
| loadLocal | false |
| loadLocalData | - | 
| timeout | 5000 |


#### PulseMCP Endpoint

API URL: https://api.pulsemcp.com/v0beta/servers?query=image&count_per_page=10
Plugin Demo:

![PulseMCP Demo](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/docs/pulsemcp_demo.jpg)

Change loadLocal to false and the js script will fetch mcp.json and MCP SERVER Info from the remote endpoint.


| key | value | 
| --- | ---- | 
| endpoint | https://api.pulsemcp.com/v0beta/servers | 
| inputParams | {"query": "image", "count_per_page": 10} |
| loadLocal | false |
| loadLocalData | - |
| timeout | 5000 |

#### Integration

Go to your app main project file, for example in the ./app/ai_search folder, find the main page index.html.

```

<head>

  <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
  <script src="../../plugin/mcp_marketplace/scripts.js"></script>
  <link rel="stylesheet" href="../../plugin/mcp_marketplace/styles.css">
<head>

<body>


    <!-- add agent marketplace plugin -->
    <div class="agent-plugin">
        <button class="agent-button agent-button-base agent-button-close" data-testid="composer-button-agent" aria-pressed="false" aria-label="agent">
            <div class="[display:var(--force-hide-label)] ps-1 pe-1 whitespace-nowrap">Agent</div>
        </button>
        <div class="panel hidden">
            <div class="panel_section">
                <h3>MCP Tools</h3>
                <div class="grid-container" id="items-grid"></div>
            </div>
        </div>
    </div>

</body>

```

#### Get User Selected Tools

In javascript, access the global variables `selectedItems` to get user selected tools and configs

```
    ## ../../plugin/mcp_marketplace/scripts.js
    ## global variable of js module
    window.agent_selected_items = selectedItems;

    ## get access
    var your_variable = window.agent_selected_items

```

### Use Cases

