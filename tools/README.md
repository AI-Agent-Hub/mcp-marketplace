# MCP Marketplace MCP Tools Schema Collection

This folder is intended to host 5000+ MCP Servers' available tools schema from Open MCP Servers listed on the marketplace (http://www.deepnlp.org/store/ai-agent/mcp-server).
The data file should follow the format <code>tool_{ownername}_{reponame}_{server_name}.json</code> file. 
And each line in each json file represent the schema of each tool

Since a lot of MCP Servers have similar server_name such as "weather_mcp", "map_mcp" or others, you should add your Github/Nodejs owner_name and repo_name for the unique_id of tools schema filename.

<code>tool_{ownername}_{reponame}_{server_name}.json</code> 

| Field | Value |
| --- | --- |
|  **github** |  https://github.com/mendableai/firecrawl-mcp-server  |
|  **owner_name** |  mendableai | 
|  **repo_name** | firecrawl-mcp-server |
|  **server_name** | mcp-server-firecrawl |
|  **file_name** | tool_mendableai_firecrawl-mcp-server_mcp-server-firecrawl.json |


### Data Format

```
./tools
./tools/schema/google-maps.json
```

Each line contains one line of json of Each tool.

```json
{"name": "maps_geocode", "description": "Convert an address into geographic coordinates", "input_schema": {"type": "object", "properties": {"address": {"type": "string", "description": "The address to geocode"}}, "required": ["address"]}}
{"name": "maps_reverse_geocode", "description": "Convert coordinates into an address", "input_schema": {"type": "object", "properties": {"latitude": {"type": "number", "description": "Latitude coordinate"}, "longitude": {"type": "number", "description": "Longitude coordinate"}}, "required": ["latitude", "longitude"]}}
{"name": "maps_search_places", "description": "Search for places using Google Places API", "input_schema": {"type": "object", "properties": {"query": {"type": "string", "description": "Search query"}, "location": {"type": "object", "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}}, "description": "Optional center point for the search"}, "radius": {"type": "number", "description": "Search radius in meters (max 50000)"}}, "required": ["query"]}}
{"name": "maps_place_details", "description": "Get detailed information about a specific place", "input_schema": {"type": "object", "properties": {"place_id": {"type": "string", "description": "The place ID to get details for"}}, "required": ["place_id"]}}
{"name": "maps_distance_matrix", "description": "Calculate travel distance and time for multiple origins and destinations", "input_schema": {"type": "object", "properties": {"origins": {"type": "array", "items": {"type": "string"}, "description": "Array of origin addresses or coordinates"}, "destinations": {"type": "array", "items": {"type": "string"}, "description": "Array of destination addresses or coordinates"}, "mode": {"type": "string", "description": "Travel mode (driving, walking, bicycling, transit)", "enum": ["driving", "walking", "bicycling", "transit"]}}, "required": ["origins", "destinations"]}}
{"name": "maps_elevation", "description": "Get elevation data for locations on the earth", "input_schema": {"type": "object", "properties": {"locations": {"type": "array", "items": {"type": "object", "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}}, "required": ["latitude", "longitude"]}, "description": "Array of locations to get elevation for"}}, "required": ["locations"]}}
{"name": "maps_directions", "description": "Get directions between two points", "input_schema": {"type": "object", "properties": {"origin": {"type": "string", "description": "Starting point address or coordinates"}, "destination": {"type": "string", "description": "Ending point address or coordinates"}, "mode": {"type": "string", "description": "Travel mode (driving, walking, bicycling, transit)", "enum": ["driving", "walking", "bicycling", "transit"]}}, "required": ["origin", "destination"]}}

```

Alternatively, file format can be like in a whole json file for several tools.

```json
{
  "tools": [
    {
      "name": "tavily-extract",
      "description": "A powerful web content extraction tool that retrieves and processes raw content from specified URLs, ideal for data collection, content analysis, and research tasks.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "urls": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "List of URLs to extract content from"
          },
          "extract_depth": {
            "type": "string",
            "enum": [
              "basic",
              "advanced"
            ],
            "description": "Depth of extraction - 'basic' or 'advanced', if usrls are linkedin use 'advanced' or if explicitly told to use advanced",
            "default": "basic"
          },
          "include_images": {
            "type": "boolean",
            "description": "Include a list of images extracted from the urls in the response",
            "default": false
          }
        },
        "required": [
          "urls"
        ]
      }
    }
  ]
}
```         

### Contributing

If you are interested in contributing to this repo of MCP Tools Schema. Please fork the repo, Create a PR add your {server_id}.json file to the ./tools/schema folder and we will review the PR.
