# MCP Marketplace Python SDK

MCP Marketplace Python Package is a common interface to give you access to public MCP Servers, Tools, Configurations. It supports various API endpoint (such as pulsemcp.com, deepnlp.org, etc).

[PyPI](https://www.pypi.org/project/mcp-marketplace)|[Document](http://www.deepnlp.org/doc/mcp_marketplace)|[MCP Marketplace](http://deepnlp.org/store/ai-agent/mcp-server)|

### Features

1. Search API of MCP Tools: Users can search MCP Servers Meta Info and tools fit for mcp.json by query, such as "map", "payment", "browser use"
2. List MCP Tools API: And Allow LLM and AI Apps to Find Your MCP Server
3. Registry: Allow Users to register the MCP Marketplace create, delete, update their MCP servers through various endpoints. (WIP)

### Python API

### Install

```
pip install mcp-marketplace

```

### Usage 

Example 1. Search MCP Marketplace By Query or Server ID

The server id follows the same in the github repo ${owner}/${repo}

```

import mcp_marketplace as mcpm

## endpoint: deepnlp
mcpm.set_endpoint("deepnlp")
result = mcpm.search(query="map", page_id=0, count_per_page=20, mode="dict")

print ("DEBUG: run_setup_config_deepnlp result:")
print (result)


## endpoint: pulsemcp
mcpm.set_endpoint("pulsemcp")
result2 = mcpm.search(query="map", count_per_page=20, offset=0)

print ("DEBUG: run_setup_config_pulsemcp result:")
print (result2)

```


Example 2. List Tools of MCP Servers 

Let's choose the unique id of browser use mcp "/puppeteer/puppeteer". And we can search the MCP meta and list the tools as below.

```
    import mcp_marketplace as mcpm
        
    result_q = mcpm.search(query="browser use", mode="list", page_id=0, count_per_page=100, config_name="deepnlp")
    result_id = mcpm.search(id="/puppeteer/puppeteer", mode="list", page_id=0, count_per_page=100, config_name="deepnlp")
    tools = mcpm.list_tools(id="/puppeteer/puppeteer", config_name="deepnlp_tool")

    print (f'{result_id}')
    print (f'{tools}')
```


### MCP Result

```

{
  "q": "map",
  "limit": 50,
  "items": [
    {
        "id": "",
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
}
```


## API Configuration

### Support Endpoint

| Endpoint | API |  Document  |
| ---- | ---- | ---- |
| http://www.deepnlp.org/api/mcp_marketplace/v1 | http://www.deepnlp.org/api/mcp_marketplace/v1?mode=list&query=map&page_id=0&count_per_page=100 | - |
| https://api.pulsemcp.com/v0beta/servers | https://api.pulsemcp.com/v0beta/servers?query=image&count_per_page=10 | https://www.pulsemcp.com/api |

### deepnlp.org


```

# list mode return paginated list
http://www.deepnlp.org/api/mcp_marketplace/v1?mode=list&query=map&page_id=0

http://www.deepnlp.org/api/mcp_marketplace/v1?mode=list&query=map&page_id=0&count_per_page=100

http://www.deepnlp.org/api/mcp_marketplace/v1?mode=list&query=map&offset=50&count_per_page=5


# dict mode return dict group by category

http://www.deepnlp.org/api/mcp_marketplace/v1?mode=dict&query=map&page_id=0

http://www.deepnlp.org/api/mcp_marketplace/v1?mode=dict&query=map&page_id=0&count_per_page=5

http://www.deepnlp.org/api/mcp_marketplace/v1?mode=dict&query=map&offset=50&count_per_page=5


# List Tools

http://www.deepnlp.org/api/mcp_marketplace/v1/tools/puppeteer/puppeteer

```


**Parameter**
| param | type | example |
| --- | ---- |  ---- | 
| mode |  string | "list", "dict", different use scenario |
| query |  string | e.g. query="Image" |
| page_id | integer | starting from 0 |
| count_per_page | integer |  5 |
| offset | integer | Optional, Equivalent to (page_id * count_per_page) e.g. 0 |



### pulsemcp.com

```
## query API
https://api.pulsemcp.com/v0beta/servers?query=image&count_per_page=10

## List API

https://api.pulsemcp.com/v0beta/servers
```

**Parameter**

| param | type | example |
| --- | ---- |  ---- | 
| query |  string | e.g. query="Image" |
| count_per_page | integer |  5 |
| offset | integer | Equivalent to (page_id * count_per_page) e.g. 0 |


### Related
- [MCP Marketplace DeepNLP](http://deepnlp.org/store/ai-agent/mcp-server)
- [MCP Marketplace PulseMCP](https://www.pulsemcp.com/)
- [Pypi](https://pypi.org/project/mcp-marketplace)
- [Github](https://github.com/AI-Agent-Hub/mcp-marketplace)
- [AI Agent Marketplace](http://www.deepnlp.org/store/ai-agent)


