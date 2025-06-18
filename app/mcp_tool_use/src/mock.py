import json

def mock_dispatcher_agent_query_plan(query):
    """
        output_json
    """
    output_json = {}
    output_json["query"] = [query]
    return output_json

def mock_call_claude_37_sonnet_tools():

    function_arguments = {"city": "杭州"}
    accumulated_data = {
        'function_name': 'maps_weather',
        'function_arguments': json.dumps(function_arguments),
        'is_function_call': True, 
        'id': ''
    }
    return accumulated_data, "", ""

def mock_call_claude_37_sonnet_tools_result():


    messages = []
    tool_results_text = "Hangzhou Weather is Good, 39 degrees, Raining Result of MCP Tool Calling Result Text"

    tool_id = "xxxxxx"
    tool_name = "maps_weather"
    tool_arguments = {"city": "杭州"}

    tool_calls = []
    tool_calls.append({
                                    "id": tool_id,
                                    "type": "tool_use",
                                    "function": {
                                        "name": tool_name,
                                        "arguments": json.dumps(tool_arguments)
                                    }
    })

    ## add tool result to chat history
    messages.extend([
                                    {
                                        "role": "assistant",
                                        "content": "",
                                        "tool_calls": tool_calls
                                    },
                                    {
                                        "role": "tool",
                                        "tool_call_id": tool_id,
                                        "name": tool_name,
                                        "content": tool_results_text
                                    }
                                ])
    
    return tool_calls, messages
