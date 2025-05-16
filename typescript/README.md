# MCP Marketplace Typescript NPM SDK

MCP Marketplace Python Package is a common interface to give you access to public MCP Servers, Tools, Configurations. It supports various API endpoint (such as pulsemcp.com, deepnlp.org, etc).


This is the official repo for npm package https://www.npmjs.com/package/mcp_marketplace

[Github](https://github.com/AI-Agent-Hub/mcp-marketplace)


### Features

1. API to Search MCP Tools: Users can search MCP Servers Meta Info and tools fit for mcp.json by query, such as "map", "payment", "browser use"
2. Registry: Allow Users to register the MCP Marketplace create, delete, update their MCP servers through various endpoints. (WIP)

### NPM API

### Install

```
npm install @modelcontextprotocol/mcp_marketplace


```

### Usage 

```

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

### Related
- [MCP Marketplace DeepNLP](http://www.deepnlp.org/store/ai-agent/mcp-server)
- [MCP Marketplace PulseMCP](https://www.pulsemcp.com/)
- [Pypi](https://pypi.org/project/mcp-marketplace)
- [Github](https://github.com/AI-Agent-Hub/mcp-marketplace)
- [AI Agent Marketplace](http://www.deepnlp.org/store/ai-agent)




