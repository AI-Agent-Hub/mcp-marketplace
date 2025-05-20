# MCP Marketplace Tools Schema Collection
This folder is intended to host the realtime tools schema from Open MCP Servers from Marketplace.
The data file should follow the format {server_name}.json file. And each line in each json file represent the schema of each tool


### Data Format

Server File Name: {server_id}.json. The {server_id} should be the same the the keys in the mcp.json config file of each client.

```
./tools
./tools/schema/google-maps.json
```

Data format of each tool in the server
```json
{"name": "maps_geocode", "description": "Convert an address into geographic coordinates", "input_schema": {"type": "object", "properties": {"address": {"type": "string", "description": "The address to geocode"}}, "required": ["address"]}}
{"name": "maps_reverse_geocode", "description": "Convert coordinates into an address", "input_schema": {"type": "object", "properties": {"latitude": {"type": "number", "description": "Latitude coordinate"}, "longitude": {"type": "number", "description": "Longitude coordinate"}}, "required": ["latitude", "longitude"]}}
{"name": "maps_search_places", "description": "Search for places using Google Places API", "input_schema": {"type": "object", "properties": {"query": {"type": "string", "description": "Search query"}, "location": {"type": "object", "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}}, "description": "Optional center point for the search"}, "radius": {"type": "number", "description": "Search radius in meters (max 50000)"}}, "required": ["query"]}}
{"name": "maps_place_details", "description": "Get detailed information about a specific place", "input_schema": {"type": "object", "properties": {"place_id": {"type": "string", "description": "The place ID to get details for"}}, "required": ["place_id"]}}
{"name": "maps_distance_matrix", "description": "Calculate travel distance and time for multiple origins and destinations", "input_schema": {"type": "object", "properties": {"origins": {"type": "array", "items": {"type": "string"}, "description": "Array of origin addresses or coordinates"}, "destinations": {"type": "array", "items": {"type": "string"}, "description": "Array of destination addresses or coordinates"}, "mode": {"type": "string", "description": "Travel mode (driving, walking, bicycling, transit)", "enum": ["driving", "walking", "bicycling", "transit"]}}, "required": ["origins", "destinations"]}}
{"name": "maps_elevation", "description": "Get elevation data for locations on the earth", "input_schema": {"type": "object", "properties": {"locations": {"type": "array", "items": {"type": "object", "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}}, "required": ["latitude", "longitude"]}, "description": "Array of locations to get elevation for"}}, "required": ["locations"]}}
{"name": "maps_directions", "description": "Get directions between two points", "input_schema": {"type": "object", "properties": {"origin": {"type": "string", "description": "Starting point address or coordinates"}, "destination": {"type": "string", "description": "Ending point address or coordinates"}, "mode": {"type": "string", "description": "Travel mode (driving, walking, bicycling, transit)", "enum": ["driving", "walking", "bicycling", "transit"]}}, "required": ["origin", "destination"]}}

```

### Contributing

If you are interested in contributing to this repo of MCP Tools Schema. Please fork the repo, Create a PR add your {server_id}.json file to the ./tools/schema folder and we will review the PR.






