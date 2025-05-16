## Open MCP Marketplace | AI Agent Marketplace Plugin from DeepNLP

The open source MCP Marketplace plugin is a pure web-based project (html/js/css), which will display available MCP tools in the frontend and fetch meta info and mcp.json from various API endpoint provider. User can choose, manage and install their preferred MCP tools in similar functionalities (such as Map, Browser Use, Payment, Fetch, etc). It can be easily integrated to your AI apps, and upgrade the tools use ability of your AI Agent .


**KEY Features**

- Pure Web-based Agent Plugin: Show the Panel of MCP Tools from available open MCP marketplace.
- Browser and Pagination: User can browser the MCP Tools by Category and use pagination to navigate.
- Support various MCP Marketplace API Endpoint: Such as pulsemcp.com, deepnlp.org, etc.
- Select and Install MCP servers: Users can choose which MCP tools to perform tasks from mcp tools marketplace with similar features, such as Map Location, Search, Fetch, Payment, etc. 
- Autonomous MCP Tools Dispatcher (TBD): Your LLM/agent can also benifit from dispatching the query/prompt of the MCP tools, making decision on which tools to choose. The decision or dispatcher agent functions with more than the description text, but also extra information such as github stars, user reviews score, ratings and call numbers statistics.
- Python and Typescript SDK to search and registry of MCP Servers and Tools

![Open MCP Marketplace DeepNLP Panel](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/docs/remote_mcp_server.jpg)

Related
- [MCP Marketplace DeepNLP](http://www.deepnlp.org/store/ai-agent/mcp-server)
- [MCP Marketplace PulseMCP](https://www.pulsemcp.com/)
- [AI Agent Marketplace](http://www.deepnlp.org/store/ai-agent)

## Update: Supported MCP Marketplace API Provider


| Endpoint | value | description |
| --- | ---- | ---- |
| deepnlp.org | http://www.deepnlp.org/api/mcp_marketplace/v1 | http://www.deepnlp.org/store/ai-agent/mcp-server |
| pulsemcp.com | https://api.pulsemcp.com/v0beta/servers | https://www.pulsemcp.com/api |



## Frontend Web-Based Plugin

**1. Integration**

If you have a chatbot or ai search engine box and you want to integrate the MCP marketplace plugin to your app, you can follow the below step and see example of an AI Search Engine Demo

**Example: AI Search with MCP Marketplace Plugin**

**Step 1**. 
Go to file ./app/ai_search/index.html and open the index.html with your browser.

Integrate AI Search Engine Demo with MCP Marketplace Plugin
![Open MCP Marketplace DeepNLP Panel](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/docs/remote_mcp_server.jpg)

**Step 2**.

Choose the Tools and click the Go button, you can see the System Prompt of user choosen plugins

![Open MCP Marketplace DeepNLP System Prompt](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/docs/remote_mcp_server_system_prompt.jpg)


**2. Install**

Clone Project and Copy The MCP Marketplace Plugin Folder

```
git clone https://github.com/AI-Agent-Hub/mcp-marketplace.git
cd ./open_mcp_marketplace

## Project Structure and Copy Files to Your Project

./plugin/mcp_marketplace/
./plugin/mcp_marketplace/index.html
./plugin/mcp_marketplace/scripts.js
./plugin/mcp_marketplace/styles.css

```

## Python and Typescript SDK

```
pip install mcp-marketplace

```
**Usage**

```

import mcp_marketplace as mcpm

## endpoint: deepnlp
mcpm.set_endpoint("deepnlp")
result = mcpm.search(query="map", page_id=0, count_per_page=20, mode="dict")

print ("DEBUG: run_setup_config_deepnlp result:")
print (result)

```



### FrontEnd Plugin
**Set Endpoint of the MCP Plugin**

Go to file ./plugin/mcp_marketplace/scripts.js and change the endpoint provider by config

```

// API: deepnlp
const config = getConfigByName("deepnlp");

// API: pulsemcp
const config = getConfigByName("pulsemcp");


```

**2.1 DeepNLP Endpoint**

Demo API URL: http://www.deepnlp.org/api/mcp_marketplace/v1?field=MCP%20Server

| key | value | 
| --- | ---- | 
| endpoint | http://www.deepnlp.org/api/mcp_marketplace/v1 |
| inputParams | {"field": "MCP SERVER", "page_id": 0, "page_size": 20} |
| inputParams.query | e.g. payment/map |
| inputParams.page_id | starting from 0|
| inputParams.count_per_page | e.g. default 20 |
| inputParams.offset | - equal to page_id * count_per_page, we use pageid to go to next page instead|
| paginationParams | {"query": "MCP SERVER", "count_per_page": 20, "page_id": 0} |
| extraParams | {"field": "MCP SERVER", "subfield": ""} |
| mapper | function, map meta data in result json |
| paginationParamsMapper | function, map meta data, merge the required paginationParams and extraParams |
| loadLocal | false |
| loadLocalData | - | 
| timeout | 5000 |

Note: field and subfield refers to the category and sub-category of MCP Servers.


```
{
  "item_map": {
    "MCP SERVER": [
      {
        "content_name": "PayPal",
        "publisher_id": "pub-paypal",
        "website": "https://mcp.paypal.com",
        "review_cnt": "1",
        "subfield": "PAYMENT",
        "field": "MCP SERVER",
        "rating": "5.0",
        "description": "",
        "content_tag_list": "official",
        "thumbnail_picture": "https://www.paypalobjects.com/webstatic/icon/favicon.ico"
      },
      {
        "content_name": "Google Maps",
        "publisher_id": "pub-google-maps",
        "website": "https://github.com/modelcontextprotocol/servers/tree/main/src/google-maps",
        "review_cnt": "1",
        "subfield": "MAP",
        "field": "MCP SERVER",
        "rating": "5.0",
        "description": "",
        "content_tag_list": "official",
        "thumbnail_picture": "http://118.190.154.215/scripts/img/ai_service_content/b7fe82a3ab985ce1a953f7b4ad9c5e01.jpeg"
      },
    ]
  },
  "page_id_map": {
    "MCP SERVER": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ]
  },
  "group_cnt": {
    "MCP SERVER": 20
  },
  "group_total": {
    "MCP SERVER": 289
  }
}


```


#### 2.2 PulseMCP Endpoint

URL: https://api.pulsemcp.com/v0beta/servers?query=image&count_per_page=10

Plugin Demo:

![PulseMCP Demo](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/docs/pulsemcp_demo.jpg)


Pagination Demo:

![PulseMCP Pagination Demo](https://raw.githubusercontent.com/AI-Agent-Hub/mcp-marketplace/refs/heads/main/docs/pulsemcp_pagination_demo.jpg)

Change loadLocal to false and the js script will fetch mcp.json and MCP SERVER Info from the remote endpoint.


| key | value | 
| --- | ---- | 
| endpoint | https://api.pulsemcp.com/v0beta/servers | 
| inputParams | {"query": "image", "count_per_page": 10} |
| paginationParams | e.g. {"query": image, "count_per_page": 10, "page_id": 0} |
| extraParams | e.g. { "offset": 10 } |
| mapper | function, map meta data in result json |
| paginationParamsMapper | function, map meta data, merge the required paginationParams and extraParams |
| loadLocal | false |
| loadLocalData | - |
| timeout | 5000 |


https://api.pulsemcp.com/v0beta/servers?query=image&count_per_page=10&offset=30

```
{
  "servers": [
    {
      "name": "example-mcp",
      "url": "https://example-mcp.com",
      "external_url": "https://example-mcp.com/landing",
      "short_description": "A powerful MCP server for example use cases",
      "source_code_url": "https://github.com/example/example-mcp",
      "github_stars": 1200,
      "package_registry": "npm",
      "package_name": "example-mcp",
      "package_download_count": 50000,
      "EXPERIMENTAL_ai_generated_description": "An AI-generated description of the server capabilities"
    }
  ],
  "next": "https://api.pulsemcp.com/v0beta/servers?offset=50",
  "total_count": 1
}
```


## 3. Development

#### 3.1 Web Integration

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


#### 3.2 Get User Selected Tools

In javascript, access the global variables `selectedItems` to get user selected tools and configs

```
    ## ../../plugin/mcp_marketplace/scripts.js
    ## global variable of js module
    window.agent_selected_items = selectedItems;

    ## get access
    var your_variable = window.agent_selected_items

```

#### 3.2 Pagination 

The params for pagination rest API can be user defined for different endpoint. Since different API provider have differnt keys of parameters, will leave a 
mapper function to allow customized and mapping.


| key | type |description  |
| --- | ---- | ---- | 
| query | required | Used to filter the meta by query, serve as the section name also. | 
| count_per_page | required | e.g. 20 | 
| page_id | required | Used as the page selector (page 0 - n) at the bottom of each section, Starting from 0 | 
| offset | optional | The index of items to skip, which is equivalent to (page_id * count_per_page). | 


## 4. Contribution


## 5. Resources






