import json
import requests
import logging

import uuid

from src.constants import *
from src.utils import *
from src.global_variables import settings

def call_qwen_max_user_prompt(user_prompt):
    """
        select different model max/plus/turbo using the same Qwen API endpoint
    """
    return call_qwen_user_prompt_model_selection(user_prompt, "qwen-max")

def call_qwen_plus_user_prompt(user_prompt):
    """
        select different model using the same API endpoint
    """
    return call_qwen_user_prompt_model_selection(user_prompt, "qwen-plus")

def call_qwen_user_prompt_model_selection(user_prompt, model):
    """
        Reference doc: https://help.aliyun.com/zh/model-studio/use-qwen-by-calling-api#b30677f6e9437
    """
    try:
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        api_key = settings.QWEN_API_KEY
        if api_key is None:
            raise ValueError("qwen_general_api.py call_qwen_max_user_prompt api_key not found, please check .env file key QWEN_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        data = json.dumps(data).encode("utf-8")
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("Qwen Response:", result["choices"][0]["message"]["content"])
        else:
            print(f"API Return Failed with Status (Status Code: {response.status_code}): {response.text}")
        return response
    except Exception as e:
        logging.error(e)
        return None

def call_qwen_plus_user_prompt_openai(user_prompt):
    """
        Reference doc: https://help.aliyun.com/zh/model-studio/use-qwen-by-calling-api#b30677f6e9437
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_prompt},
            ],
        )
        response_json = completion.model_dump_json()
        return response_json
    except Exception as e:
        logging.error(e)
        return {}

def post_process_qwen_max_response(response):
    """
    """
    return post_process_qwen_response(response)

def post_process_qwen_plus_response(response):
    return post_process_qwen_response(response)

def post_process_qwen_response(response):
    if response is None:
        return {}
    tools, completion,reasoningContent  = {}, "", ""

    res_json = {}      
    try:
        print (f"post_process_function_call_qwen_base input response {response} and type {type(response)}")
        res_json = json.loads(response.content)
    except json.decoder.JSONDecodeError:
        print("Not Valid Json Format")
        return ''
    try:
        # x = res_json["data"]["values"]["data"]
        completion = res_json["choices"][0]["message"]["content"]
        usage = res_json["usage"] if "usage" in res_json else {}
    except Exception as e:
        logging.error(e)
    return tools, completion, reasoningContent


def call_qwen_max_tool_calls(messages, tools):
    return call_qwen_tool_calls_model_selection(messages, tools, "qwen-max")

def call_qwen_plus_tool_calls(messages, tools):
    return call_qwen_tool_calls_model_selection(messages, tools, "qwen-plus")

def call_qwen_tool_calls_model_selection(messages, tools, model):
    """
        Args:
            messages: list of dict 
            tools: list of dict
        return:
            {"choices":[{"message":{"content":"","role":"assistant","tool_calls":[{"index":0,"id":"call_f8d9f219ee034156985f6a","type":"function","function":{"name":"get_current_weather","arguments":"{\"location\": \"上海\"}"}}]},"finish_reason":"tool_calls","index":0,"logprobs":null}],"object":"chat.completion","usage":{"prompt_tokens":266,"completion_tokens":20,"total_tokens":286,"prompt_tokens_details":{"cached_tokens":0}},"created":1750987730,"system_fingerprint":null,"model":"qwen-plus","id":"chatcmpl-3bd1954c-8594-98e1-957b-9fda39ac73fc"}
        doc: https://help.aliyun.com/zh/model-studio/qwen-function-calling
    """
    try:
        api_key = settings.QWEN_API_KEY
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {api_key}",
        }
        data = {
                "stream": False,
                "model": model,
                "messages": messages,
                "tools": tools
        }
        data = json.dumps(data).encode("utf-8")
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            result = response.json()
            print("Qwen Response:", result["choices"][0]["message"]["content"])
        else:
            print(f"API Return Failed with Status (Status Code: {response.status_code}): {response.text}")
        return response
    except Exception as e:
        print (e)
        return None

def call_qwen_max_tool_calls_openai(messages, tools):
    """
        messages: list of dict 
        tools: list of dict
        doc: https://help.aliyun.com/zh/model-studio/qwen-function-calling
    """
    try:
        completion = client.chat.completions.create(
            model="qwen-max", 
            messages=messages,
            tools=tools
        )
        response_json = completion.model_dump_json()
        return response_json
    except Exception as e:
        print (e)
        return {}


def post_process_function_call_qwen_max(response):
    return post_process_function_call_qwen_common(response)

def post_process_function_call_qwen_plus(response):
    return post_process_function_call_qwen_common(response)

def post_process_function_call_qwen_common(response):
    """
        response:
            {
                "id": "call_6fcd208b442c4c12b1b419",
                "function": {
                  "arguments": "{\"location\": \"\u4e0a\u6d77\u5e02\"}",
                  "name": "get_current_weather"
                },
                "type": "function",
                "index": 0
            }
    """
    if response is None:
        return {}

    tools = {}
    completion = ""
    reasoningContent = ""  

    res_json = {}      
    try:
        content = response.content
        logging.info(f"post_process_function_call_qwen_base content {content}")
        res_json = json.loads(content)

    except json.decoder.JSONDecodeError:
        print("Not Valid Json Format" + content)
        return {}
    try:
        choice = res_json["choices"][0] if len(res_json["choices"]) > 0 else {}
        finish_reason = choice["finish_reason"] if "finish_reason" in choice else "" # tool_calls
        message = choice["message"] if "message" in choice else {}
        tool_calls = message["tool_calls"] if "tool_calls" in message else []
        tool_call = tool_calls[0] if len(tool_calls) > 0 else {}
        return tool_call
    except Exception as e:
        logging.error(e)
        return {}

def tool_result_to_claude_mapper(tool_call):
    if tool_call is None or len(tool_call) == 0:
        return {}, "", ""

    tools_choice_response = {
            'function_name': '',
            'function_arguments': '',
            'is_function_call': False, 
            'id': ''
    }
    completion = ""
    reasoningContent = ""
    try:
        tool_id = tool_call["id"] if "id" in tool_call else ""
        function = tool_call["function"] if "function" in tool_call else {}
        function_arguments = function["arguments"] if "arguments" in function else {}
        function_name = function["name"] if "name" in function else ""

        tools_choice_response["is_function_call"] = True 
        tools_choice_response["function_name"] = function_name
        tools_choice_response["function_arguments"] = function_arguments
        tools_choice_response["id"] = tool_id
    except Exception as e:
        logging.error(e)
    return tools_choice_response, completion, reasoningContent

def call_response_generation_qwen_max(messages):
    return call_response_generation_qwen_model_selection(messages, "qwen-max")

def call_response_generation_qwen_plus(messages):

    return call_response_generation_qwen_model_selection(messages, "qwen-plus")

def call_response_generation_qwen_model_selection(messages, model):
    """
        input: 
            messages
        output: 
            generator
    """
    output_format = OUTPUT_FORMAT_SWITCH
    outputMessageId = str(uuid.uuid4())
    user_prompt = f""" 
                ### You are a helpful text summarization assistant. Your task is to generate a response based on users' original query and tools call results.
                ### Chat History
                {messages}
    """
    final_messages = [{"role": "user", "content": user_prompt}]

    toolsResult, completion, reasoningContent = {}, "", ""
    if model == "qwen-plus":
        final_response = call_qwen_plus_user_prompt(json.dumps(final_messages))
        toolsResult, completion, reasoningContent = post_process_qwen_plus_response(final_response)

    elif model == "qwen-max":
        final_response = call_qwen_max_user_prompt(json.dumps(final_messages))
        toolsResult, completion, reasoningContent = post_process_qwen_max_response(final_response)
    else:
        final_response = call_qwen_plus_user_prompt(json.dumps(final_messages))
        toolsResult, completion, reasoningContent = post_process_qwen_plus_response(final_response)

    # toolsResult, completion, reasoningContent = post_process_qwen_base_response(final_response)
    print (f"Assistant: {completion}")

    # merging streaming text chunks
    completion_list = []
    reasoningContent_list = []

    # yield back whole response, need modificagtion
    output_message = assembly_message("assistant", output_format, completion, section=SECTION_ANSWER, message_id=outputMessageId)
    yield json.dumps(output_message)

def run_qwen_function_call():

    tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get Current Time of the day",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get current weather of the day",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or Counties",
                    }
                },
                "required": ["location"]
            }
        }
    }
    ]
    tool_name = [tool["function"]["name"] for tool in tools]
    print(f"Created {len(tools)} Tools，为：{tool_name}\n")

    messages = [
        {
            "role": "system",
            "content": """You are a helpful assistant who can use tool of ‘get_current_weather’ and ‘get_current_time’,
         Please respond nicely..""",
        },
        {
            "role": "user",
            "content": "Weather in Shanghai"
        }
    ]

    print (f"DEBUG: Input Tools {json.dumps(tools, indent=2)}")
    response = call_qwen_max_tool_calls(messages, tools)

    tool_call = post_process_function_call_qwen_plus(response)
    print (f"DEBUG: Output tool_call {json.dumps(tool_call, indent=2)}")
    
    tool_call_mapped, completion, reasoningContent = tool_result_to_claude_mapper(tool_call)
    print (f"DEBUG: Output tool_call_mapped {json.dumps(tool_call_mapped, indent=2)}")

def run_qwen_text_chat():

    prompt = "Can you output text in json format, json content with key name and value 2? "
    response = call_qwen_max_user_prompt(prompt)
    tools, completion, reasoningContent = post_process_qwen_plus_response(response)
    print (f"completion {completion}")

def main():
    
    # case 1
    run_qwen_text_chat()

    # case 2
    run_qwen_function_call()

if __name__ == '__main__':
    main()
