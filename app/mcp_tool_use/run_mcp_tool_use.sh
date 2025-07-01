## start the server
uvicorn src.app:app --port 5000


## curl to test Tool Use Chat API
curl -X POST -H "Content-Type: application/json" -d '{ "messages": [{"role":"user", "content": "Weather in Hangzhou"}] , "kwargs": {}}' http://127.0.0.1:5000/api/chat

## Choose model
curl -X POST -H "Content-Type: application/json" -d '{ "messages": [{"role":"user", "content": "Weather in Hangzhou"}] , "kwargs": {"model_selection": "qwen-plus"}}' http://127.0.0.1:5000/api/chat

## Curl An MCP Server
curl -X POST -H "Content-Type: application/json" -d '{
    "server_id": "google-search",
    "tool_name": "search",
    "tool_input": {
        "query": "2025 NBA Draft",
        "num": 5
    }
}' http://127.0.0.1:5000/api/query

""" Result
{"success":true,"data":["[\n  {\n    \"title\": \"2025 NBA Draft Results: Picks 1-59 | NBA.com\",\n    \"link\": \"https://www.nba.com/news/2025-nba-draft-order\",\n    \"snippet\": \"4 days ago ... 2025 NBA Draft Results: Picks 1-59 · 1. Mavericks draft Cooper Flagg (Duke) · 2. Spurs draft Dylan Harper (Rutgers) · 3. 76ers draft VJ ...\"\n  },\n  {\n    \"title\": \"2025 NBA draft - Wikipedia\",\n    \"link\": \"https://en.wikipedia.org/wiki/2025_NBA_draft\",\n    \"snippet\": \"The 2025 NBA draft was the 79th edition of the National Basketball Association's (NBA) annual draft. Like the 2024 draft, this draft took place over two ...\"\n  },\n  {\n    \"title\": \"2025 NBA Draft\",\n    \"link\": \"https://www.nba.com/draft/2025\",\n    \"snippet\": \"The official site of the 2025 NBA Draft to be held on June 25-26 in Brooklyn, NY. Prospect profiles, mock drafts, team needs, features and news on the NBA ...\"\n  },\n  {\n    \"title\": \"2025 NBA mock draft: Debating 30 Round 1 picks, need, value - ESPN\",\n    \"link\": \"https://www.espn.com/nba/story/_/id/45470775/2025-nba-mock-draft-debating-30-round-1-picks-need-value-cooper-flagg\",\n    \"snippet\": \"Jun 10, 2025 ... 2025 NBA mock draft: Debating 30 Round 1 picks, need, value · 1. Dallas Mavericks · 2. San Antonio Spurs · 3. Philadelphia 76ers · 4. Charlotte ...\"\n  },\n  {\n    \"title\": \"2025 NBA Draft Big Board 8.0 - Countdown To The Draft! - NBA ...\",\n    \"link\": \"https://nbadraftroom.com/2025-nba-draft-big-board-8-0-countdown-to-the-draft/\",\n    \"snippet\": \"Jun 10, 2025 ... A long-form edition of my 2025 NBA Draft big board ranking the top 70 prospects for the 2025 NBA draft. I have 8 Tiers of players.\"\n  }\n]"],"error":null}
"""
