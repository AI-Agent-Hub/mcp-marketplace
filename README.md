## Open MCP Marketplace | AI Agent Marketplace Plugin from DeepNLP

The open source MCP Marketplace plugin is a pure web project (html/js/css), which contains the the MCP tools configs files that can be easily integrated to your AI apps and upgrade your AI Agent Tools ability.

**KEY Features**

- Agent Button: Show the Panel of MCP Tools from all the web
- Select MCP servers: Users can choose which MCP tools to perform tasks from mcp tools marketplace with similar features, such as (Map Location, Search, Fetch, Payment, etc). 
- MCP Tools Dispatcher: Your LLM/agent can also benifit from dispatching the query to the MCP tools, making decision on which tools to choose. The decision or dispatcher agent functions with more than the description text, but also the genunie user reviews score (0-5), ratings and call numbers statistics.


![Open MCP Marketplace DeepNLP Panel](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/docs/remote_mcp_server.jpg)

Demo and Websites
- [MCP Marketplace DeepNLP](http://www.deepnlp.org/store/ai-agent/mcp-server)
- [Web Demo]()
- [AI Agent Marketplace](http://www.deepnlp.org/store/ai-agent)


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

## Copy Files to Your Project

./plugin/mcp_marketplace/
./plugin/mcp_marketplace/index.html
./plugin/mcp_marketplace/scripts.js
./plugin/mcp_marketplace/styles.css

```


#### Set Endpoint of where the MCP info json is fetching

Go to file ./plugin/mcp_marketplace/scripts.js


| variable | value | description |
| --- | ---- | ---- |
| ENDPOINT_MCP_MARKETPLACE_DEENLP | http://www.deepnlp.org/api/mcp_marketplace/v1 | This endpoint is for demo and debug purpose only and may not have enough quota for production use. For production worthy endpoint please register the API keys on http://www.deepnlp.org/workspace |
| loadLocal | false | if set to true: js will load from local json mcp.json file; if set to false: load from remote endpoint|

Change loadLocal to false and the js script will fetch mcp.json and MCP SERVER Info from the remote endpoint.


#### Integration

Go to your app main project file, for example a index.html.

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



