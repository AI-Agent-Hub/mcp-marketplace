## MCP Config Files A-Z Repo
This folder is to index and arxiv the mcp_config.json or mcp.json configuration file for AI client such as Cursor, Claude, etc.

The mcpjsonfile is organized in a-z folders according to the <code>${owner}/${repo}</code> name. 


For example ,for the fetch firecrawl mcp, the uniqueid follows the github repo: https://github.com/mendableai/firecrawl-mcp-server

And the [mcp_config.json](https://github.com/AI-Agent-Hub/mcp-marketplace/blob/main/data/config/file/m/mcp_config_mendableai_firecrawl-mcp-server_0.json) file can be found in folder
with file name as <code>mcp_config_${owner}_${repo}_0.json</code>. And the ending index denotes different configs for different platforms.

```
./data/config/file/m/mcp_config_mendableai_firecrawl-mcp-server_0.json
./data/config/file/m/mcp_config_mendableai_firecrawl-mcp-server_1.json
./data/config/file/m/mcp_config_mendableai_firecrawl-mcp-server_2.json

```

Each file represents a configuration for different platforms (Claude, Cursor, VSCode, etc.)

```
{
  "mcpServers": {
    "firecrawl-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "firecrawl-mcp"
      ],
      "env": {
        "FIRECRAWL_API_KEY": "YOUR-API-KEY"
      }
    }
  }
}
```

## Usage 

To fetch the MCP Config Files You can Visit the MCP Marketplace (http://www.deepnlp.org/store/ai-agent/mcp-server/pub-mendableai/firecrawl-mcp-server) or using the python/node API. Please install
the package as "pip install mcp-marketplace". 

```python
    import mcp_marketplace as mcpm
    server_ids = ["mendableai/firecrawl-mcp-server", "puppeteer/puppeteer", "mendableai/firecrawl-mcp-server", "google-maps/google-maps"]
    mcp_config_result = mcpm.load_config_batch(server_ids, config_name="deepnlp_server")
```
