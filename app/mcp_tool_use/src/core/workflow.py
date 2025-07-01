import asyncio
import re
import json
import os
import subprocess
import codecs
import logger
import logging
import traceback
import uuid

from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
import mcp_marketplace as mcpm
mcpm.set_endpoint("deepnlp")

from anthropic import Anthropic
from dotenv import load_dotenv
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from pathlib import Path

from .. import global_variables as gv
from ..prompts import *
from ..mock import *
from ..constants import *
from ..msg_system import *
from ..qwen.qwen_general_api import *
from ..mcp_servers import call_tools_base

load_dotenv()

async def tooluse_loop_with_confirmation(messages, kwargs):
    """
        Main Workflow of Query Planing->Search Tools -> User Confirmation -> Run -> Generation
    """
    import json
    import traceback

    if len(messages) < 1:
        yield json.dumps({})
    outputMessageId = str(uuid.uuid4())
    try:

        ## switches
        output_format = OUTPUT_FORMAT_SWITCH
        model_selection = kwargs[KEY_MODEL_SELECTION] if KEY_MODEL_SELECTION in kwargs else MODEL_SELECTION_DEFAULT
        logging.info(f'tooluse_loop_with_confirmation model selected {model_selection}')

        message = messages[len(messages)-1]
        query = message["content"] if "content" in message else ""
        role = message["role"] if "role" in message else ""
        if query == "":
            yield json.dumps({})

        branch, result = routing_branch(query)

        if (branch == BRANCH_AGENT_ACTION):
                print (f"DEBUG: BRANCH_AGENT_ACTION {result}")
                action = result["action"] if "action" in result else ""
                ### continue processing results
                match action:
                    case "ACCEPT":
                        ## execute call and yield back results
                        result = "Thanks for choosing ACCEPT. Continue Running..."
                        print (f"Result: {result}")

                        tool_schema, toolname_to_server_dict = get_tool_call_input_params(messages, kwargs)
                        tool_name = tool_schema["name"] if "name" in tool_schema else ""
                        system_msg = f"Start Running Tool {tool_name} "
                        ## yield
                        yield json.dumps(assembly_message("assistant", output_format, system_msg, section=SECTION_SYSTEM_MSG, message_id=outputMessageId))                        
                        # yield json.dumps(assembly_message("assistant", output_format, json.dumps(tool_schema), section=SECTION_TOOL, message_id=outputMessageId))
                        await asyncio.sleep(0)

                        # message_tool_result = {"role": "assistant", "content": result}
                        message_tool_result_list, tool_results_text = await get_tool_call_result_message(kwargs, tool_schema, toolname_to_server_dict)
                        # update message
                        messages.extend(message_tool_result_list)

                        print (f"Start Yielding Result: {result}")
                        print (f"Start Yielding Result: {tool_results_text}")

                    case "REJECT":

                        result = "Thanks for choosing REJECT. Continue Running..."
                        
                        print (f"Start Yielding Result: {result}")
                        yield json.dumps(assembly_message("assistant", output_format, result, section=SECTION_TOOL, message_id=outputMessageId) )
                        await asyncio.sleep(0)

                        # update message
                    case "INSTALL":

                        result = "Thanks for choosing Install Apps. Continue Running..."
                        
                        print (f"Start Yielding Result: {result}")
                        yield json.dumps(assembly_message("assistant", output_format, result, section=SECTION_TOOL, message_id=outputMessageId) )
                        await asyncio.sleep(0)

                        ## running tools
                        message_tool_result = {"role": "assistant", "content": result}
                        # update message
                        messages.append(message_tool_result)

                ## generation
                for chunk in call_response_generation(messages, kwargs):
                    yield chunk 

        elif (branch == BRANCH_NORMAL):

                # Stage 1
                yield json.dumps(assembly_message("assistant", output_format, MSG_SEARCH_MARKETPLACE, section=SECTION_SYSTEM_MSG, message_id=outputMessageId) )                
                await asyncio.sleep(0)

                # Stage 1 Creating DispatcherAgent to find relevent tools and servvers
                dispatcher_agent = DispatcherAgent(model_selection=model_selection)

                # Call LLM to query planning of tools
                query_list = dispatcher_agent.plan(query)
                logging.info(f"Dispatcher Agent Plan the Tools Function Call parse query {query} from queries: {query_list}")

                display_message = "<p>Finding Relevant Tools Using Queries: </p>" + "<div>" + " ".join(['<div class="div_planning_highlight">' + query + '</div>' for query in query_list]) + "</div>" + "\r"
                print (f"Start Yielding Result: {display_message}")
                yield json.dumps(assembly_message("assistant", output_format, display_message, section=SECTION_THINK, message_id=outputMessageId) )                
                await asyncio.sleep(0)

                # key: server_id, value: tools
                server_ids, servers_tools_dict_remote = dispatcher_agent.search_tool(query_list)
                logging.info(f"Dispatcher Agent Plan Find Relevant server_ids: {server_ids}, servers_tools_dict_remote: {servers_tools_dict_remote} ")

                display_message = "<p>Relevant MCP Servers: </p>" + "<div>" + " ".join(['<div class="div_planning_highlight">' + server_id + '</div>' for server_id in server_ids]) + "</div>" + "\r"
                print (f"Start Yielding Result: {display_message}")
                yield json.dumps(assembly_message("assistant", output_format, display_message, section=SECTION_THINK, message_id=outputMessageId) )                
                await asyncio.sleep(0)

                ## Merge Available Tools: Local and Remote Marketplace
                server_tools_dict_local = get_available_tools_from_registry(gv._global_server_registry)
                print ("DEBUG: server_tools_runnable size|" + str(len(server_tools_dict_local)))

                server_tools_dict = merge_local_and_remote_servers(server_tools_dict_local, servers_tools_dict_remote)
                available_tools_keys = server_tools_dict.keys()
                logging.info(f"Dispatcher Agent Merging Remote and Local Tools Available: {available_tools_keys}, server_tools_dict: {server_tools_dict} ")

                # each while loop yield a new line of tool_call json
                ## initialize, load servers from mcp, toolname_to_server_dict for starting servers mapping
                available_tools, toolname_to_server_dict = parse_available_tools(server_tools_dict)
                logging.info(f"Start Making Function Calls Iteration available_tools {available_tools}")

                call_messages = [
                    {"role": "user", "content": query}
                ]
                iterations = 0
                max_iterations = 1

                ## multi round tool call set max_iterations=1 for quick use

                available_tools_size = len(available_tools)
                available_tools_display = format_available_tools_display(available_tools)
                logging.info(f"Start Making Function Calls Iteration {iterations}, Messages {call_messages} , available_tools size {available_tools_size}, available_tools_display {available_tools_display}")
                
                display_message = f"<p>Loading Available Tools: </p> <div>{available_tools_display}</div>"
                print (f"Start Yielding Result: {display_message}")                
                yield json.dumps(assembly_message("assistant", output_format, display_message, section=SECTION_THINK, message_id=outputMessageId) )                
                await asyncio.sleep(0)

                response = call_llm_tools_function_call_wrapper(model_selection, {"messages": call_messages, "tools": tools_openai_wrapper(available_tools)})
                tools_choice_response, completion, reasoning_content = process_llm_tools_function_call_result(model_selection, response)

                if len(tools_choice_response) == 0:
                    # no tools Chosen
                    logging.info("No Tools Chosen by LLM tools_choice_response")
                    for chunk in call_response_generation(messages, kwargs):
                        yield chunk 
                else:
                    tool_results = []

                    is_function_call = tools_choice_response["is_function_call"] if "is_function_call" in tools_choice_response else False
                    tool_name = tools_choice_response["function_name"] if "function_name" in tools_choice_response else ""
                    tool_arguments_str = tools_choice_response["function_arguments"] if "function_arguments" in tools_choice_response else ""
                    tool_id = tools_choice_response["id"] if "id" in tools_choice_response else str(uuid.uuid4()) ## if tool_id not returned, using uuid

                    tool_arguments = {}
                    try:
                        tool_arguments = json.loads(tool_arguments_str)
                    except Exception as e:
                        print (e)
                    
                    print (f"DEBUG: Convertion tool_arguments_str  is {tool_arguments_str}")
                    print (f"DEBUG: Convertion tool_arguments  is {tool_arguments}")

                    if is_function_call:
                        tool_choose_result = get_tool_choose_result_html(tool_id, tool_name, tool_arguments)
                        print (f"DEBUG: tool_choose_result  is {tool_choose_result}")

                        display_message =  tool_choose_result
                        print (f"Start Yielding Result: {tool_choose_result}")                
                        yield json.dumps(assembly_message("assistant", output_format, tool_choose_result, section = SECTION_TOOL, message_id=outputMessageId) )                
                        await asyncio.sleep(0)

                        ## hidden area
                        tool_call_input = {"tool_id": tool_id, "tool_name": tool_name, "tool_arguments": tool_arguments, KEY_TOOLNAME_TO_SERVER_DICT: toolname_to_server_dict}

                        display_message =  json.dumps(tool_call_input)
                        yield json.dumps(assembly_message("assistant", output_format, display_message, section = SECTION_CONTEXT, message_id=outputMessageId) )                
                        await asyncio.sleep(0)

                    else:
                        for chunk in call_response_generation(messages, kwargs):
                            yield chunk 
                         
    except Exception as e:
        logging.error(f"claude_tooluse_loop_with_confirmation {e}")
        traceback.print_exc()

def clean_response_json(completion):
    """
    """
    try:
        completion_clean = completion.replace("`", "")
        completion_clean = completion_clean.replace("\n", "")
        completion_clean = completion_clean.replace("json", "")
        completion_clean = completion_clean.strip()
        output_json =json.loads(completion_clean)
        return output_json
    except Exception as e:
        print (e)
        return {}

def call_llm_model_selection_wrapper(prompt, model_selection):
    """ support non function call request
    """
    if model_selection == MODEL_SELECTION_QWEN3_MAX:
        response = call_qwen_max_user_prompt(prompt)
        return response
    elif model_selection == MODEL_SELECTION_QWEN3_PLUS:
        response = call_qwen_plus_user_prompt(prompt)
        return response
    elif model_selection in [MODEL_SELECTION_CLAUDE_37, MODEL_SELECTION_CLAUDE_OPUS_4, MODEL_SELECTION_GPT4O,
        MODEL_SELECTION_GEMINI_25_FLASH]:
        # TBD, set to default model selection
        response = call_qwen_plus_user_prompt(prompt)
        return response
    else:
        response = call_qwen_plus_user_prompt(prompt)
        return response

def call_llm_tools_function_call_wrapper(model_selection, kwargs):

    tools = kwargs["tools"] if "tools" in kwargs else []
    messages = kwargs["messages"] if "messages" in kwargs else []
    logging.info(f"Input call_llm_tools_function_call_wrapper tools {tools} and messages {messages}")

    if model_selection == MODEL_SELECTION_QWEN3_MAX:
        response = call_qwen_max_tool_calls(messages, tools)
        return response
    elif model_selection == MODEL_SELECTION_QWEN3_PLUS:
        response = call_qwen_plus_tool_calls(messages, tools)
        return response
    elif model_selection in [MODEL_SELECTION_CLAUDE_37, MODEL_SELECTION_CLAUDE_OPUS_4, MODEL_SELECTION_GPT4O, MODEL_SELECTION_GEMINI_25_FLASH]:
        # TBD, Set to default first
        response = call_qwen_plus_tool_calls(messages, tools)
        return response
    else:
        response = call_qwen_plus_tool_calls(messages, tools)
        return response

def process_llm_tools_function_call_result(model_selection, response):
    """
        Args:
            model_selection: Depending on the model and API selection processing various function call response, streaming vs non-streaming, claude or Gemini or OpenAI
            response
        Return:
            response
    """
    ## query planning use non streaming LLM API to get whole results
    planning_api_streaming = False
    tools_choice_response, completion, reasoning_content = {}, "", ""    
    if planning_api_streaming:
        tools_choice_response, completion, reasoning_content = process_streaming_chunks(response)
    else:
        tools_choice_response, completion, reasoning_content = tool_result_to_claude_mapper(post_process_function_call_qwen_max(response))
    return tools_choice_response, completion, reasoning_content

class DispatcherAgent(object):
    """
        DispatcherAgent is responsible for planning on users' query and decide what keywords to use to search relevant tools
    """
    def __init__(self, **kwargs):
        self.topk = kwargs["topk"] if "topk" in kwargs else 3
        self.model_selection = kwargs[KEY_MODEL_SELECTION] if KEY_MODEL_SELECTION in kwargs else ""
        logging.info(f"Initializing DispatcherAgent model_selection {self.model_selection}")

    def plan(self, query:str):
        """
            args:
                query： str, e.g. query = "Find the best route from New York University to Times Square"
            return:
                quert_list: List[String]
        """
        # 1. calling llm to seperate query to separate queries
        user_prompt = prompt_query_plan.format(user_input=query)
        output_json = {}
        if MOCK_RESPONSE_SWITCH:
            output_json = mock_dispatcher_agent_query_plan(query)
        else:
            response = call_llm_model_selection_wrapper(user_prompt, self.model_selection)

            ## post process wrapper
            tools, completion, reasoningContent = {}, "", ""
            output_json = {}
            if self.model_selection == MODEL_SELECTION_CLAUDE_37:
                tools, completion, reasoningContent = process_streaming_chunks(response)
                output_json = clean_response_json(completion)
                logging.info(f"DispatcherAgent plan query before Calling Claude completion {completion}| tools {tools} | reasoningContent {reasoningContent}| output_json {output_json}")

            elif self.model_selection == MODEL_SELECTION_QWEN3_MAX:
                tools, completion, reasoningContent = post_process_qwen_max_response(response)
                output_json = clean_response_json(completion)
                logging.info(f"DispatcherAgent plan query before Calling Qwen Max completion {completion}| tools {tools} | reasoningContent {reasoningContent}| output_json {output_json}")
            elif self.model_selection == MODEL_SELECTION_QWEN3_PLUS:
                tools, completion, reasoningContent = post_process_qwen_plus_response(response)
                output_json = clean_response_json(completion)
                logging.info(f"DispatcherAgent plan query before Calling Qwen Plus completion {completion}| tools {tools} | reasoningContent {reasoningContent}| output_json {output_json}")

            else:
                logging.info(f"MODEL {self.model_selection} not supported")
            ## post process completion output in json format
        ## split content
        query_list = output_json["query"] if "query" in output_json else []
        query_list.append(query)
        return query_list

    def search_server(self, query_list:list):
        """
            Args: 
                Query List
            Return: 
                dict, key: server_id, value: list of tools dict
                    { 
                        "name": str,
                        "description": str,
                        "input_schema": dict
                    }
        """
        if query_list is None or len(query_list) == 0:
            return []
        query_cnt = len(query_list)
        # key: query, value: list of items
        query_to_servers_dict = {}
        try:
            params_list = [{"query": query, "page_id":0, "count_per_page":50} for query in query_list]
            results = mcpm.search_batch(params_list)
            for (params, result) in results:
                query = params["query"] if "query" in params else ""
                items = result["items"] if "items" in result else []
                itemd_ids = [item["id"] for item in items]
                item_cnt = len(items)
                print (f"DEBUG: Input Query {query}, Relevant Server Count {item_cnt}, Server Id {itemd_ids}")
                query_to_servers_dict[query] = items
        except Exception as e:
            print (f"search_server failed with error {e}")
        return query_to_servers_dict

    def rank_server(self, servers):
        """
            Rerank of relevant servers
        """
        return servers

    def search_tool(self, query_list:list):
        """
            Args: 
                Query List: List[String]
            Return: 
                dict, key: server_id, value: list of tools dict
                    { 
                        "name": str,
                        "description": str,
                        "input_schema": dict
                    }
        """
        if query_list is None or len(query_list) == 0:
            return []
        server_id_list = []
        servers_tools_dict = {}
        try:
            query_cnt = len(query_list)
            ## key: quert, value: list of servers
            query_to_servers_dict = self.search_server(query_list)
            for query, servers in query_to_servers_dict.items():
                servers_ranked = self.rank_server(servers)
                servers_top = []
                if len(servers_ranked) > self.topk:
                    servers_top = servers_ranked[0:self.topk]
                else:
                    servers_top = servers_ranked
                server_ids = [server["id"] for server in servers_top]
                server_id_list.extend(server_ids)
            
            server_id_list_no_dup = list(set(server_id_list))
            servers_tools_dict = {}
            try:
                param_list =[{"id": server_id, "config_name": "deepnlp_tool"} for server_id in server_id_list_no_dup]
                tools_result = mcpm.list_tools_batch(param_list)
                for param, result in tools_result:
                    id_value = param["id"] if "id" in param else ""
                    tools = result["tools"] if "tools" in result else []
                    if id_value != "":
                        servers_tools_dict[id_value] = tools
            except Exception as e1:
                print (f"mcpm.list_tools_batch failed {e1}")
        except Exception as e:
            print (f"agent search_tool {e}")
        return server_id_list, servers_tools_dict

def tools_openai_wrapper(tools):
    tools_wrapped = [{
        "type": "function",
        "function":{
            "name": tool["name"] if "name" in tool else "", 
            "description": tool["description"] if "description" in tool else "",
            "parameters": tool["input_schema"] if "input_schema" in tool else {}
        }
    } for tool in tools]
    return tools_wrapped

def process_streaming_chunks(response):
    """
        post process response streaming service
    """
    accumulated_data = {
        'function_name': '',
        'function_arguments': '',
        'is_function_call': False, 
        'id': ''
    }

    completion_list = []
    reasoning_content_list = []

    for line in response.iter_lines():
        if line == "[Done]":
            break
        line_clean =line.decode().replace("data: ", "")
        if line_clean == "":
            continue
        delta = {}
        try:
            delta = json.loads(line_clean)
        except Exception as e:
            print (f"process_streaming_chunks failed with error {e}")

        if "toolCalls" in delta:
            accumulated_data['is_function_call'] = True
            
            tools_calls_list = delta["toolCalls"]
            if len(tools_calls_list) > 0:
              tools_calls_dict = tools_calls_list[0]
              # Accumulate function name
              if 'function' in tools_calls_dict:
                if "name" in tools_calls_dict['function']:
                    accumulated_data['function_name'] += tools_calls_dict['function']['name']
                
                # Accumulate function arguments
                if "arguments" in tools_calls_dict['function']:
                    accumulated_data['function_arguments'] += tools_calls_dict['function']['arguments']

              if 'id' in tools_calls_dict:
                tool_id = tools_calls_dict["id"]
                accumulated_data['id'] = tool_id

        elif "reasoningContent" in delta:

            reasoning_content_list.append(delta["reasoningContent"])
        
        elif "completion" in delta:
            completion_list.append(delta["completion"])
        else:
            continue

    completion = "".join(completion_list)
    reasoning_content = "".join(reasoning_content_list)

    return accumulated_data, completion, reasoning_content

def format_available_tools_display(available_tools):
    """
    """
    tool_name_list = [tool["name"] if "name" in tool else "" for tool in available_tools]
    tool_name_filter = [tool_name for tool_name in tool_name_list if tool_name != "" and tool_name is not None]
    tool_name_display = "".join(['<div class="div_planning_highlight">' + tool_name + '</div>' for tool_name in tool_name_filter])
    return tool_name_display

def process_streaming_chunk(line):
    """
    """
    accumulated_data = {
        'reasoningContent':'',
        'completion': '',
        'function_name': '',
        'function_arguments': '',
        'is_function_call': False, 
        'id': '',
        'finished': False
    }
    try:
        if line == "":
            # append "\n" to change lines
            return accumulated_data
        if line == "[Done]":
            accumulated_data['finished'] = True
            return accumulated_data

        line_clean = line.decode().replace("data: ", "")
        if line_clean == "":
            return accumulated_data

        delta = {}
        try:
            delta = json.loads(line_clean)
        except Exception as e:
            print (f"process line_clean {line_clean} error {e}")
        # chunk 
        if "toolCalls" in delta:
            accumulated_data['is_function_call'] = True
            
            tools_calls_list = delta["toolCalls"]
            if len(tools_calls_list) > 0:
              tools_calls_dict = tools_calls_list[0]
              # Accumulate function name
              if 'function' in tools_calls_dict:
                if "name" in tools_calls_dict['function']:
                    accumulated_data['function_name'] += tools_calls_dict['function']['name']
                
                # Accumulate function arguments
                if "arguments" in tools_calls_dict['function']:
                    accumulated_data['function_arguments'] += tools_calls_dict['function']['arguments']

              if 'id' in tools_calls_dict:
                tool_id = tools_calls_dict["id"]
                accumulated_data['id'] = tool_id

        elif "reasoningContent" in delta:
            accumulated_data["reasoningContent"] = delta["reasoningContent"]
        elif "completion" in delta:
            accumulated_data["completion"] = delta["completion"]
        else:
            print (f"Not Valid Response Delta {delta} for input line ")

        return accumulated_data
    except Exception as e:
        print (e)
        return accumulated_data

def merge_local_and_remote_servers(server_tools_dict_local, servers_tools_dict_remote):
    """
        Args:
            server_tools_dict_local: dict, key: server_id, value: list of tools
            servers_tools_dict_remote: dict, key:  server_id, str, value: list of tools schema

            server_id: e.g. google-maps, amap-amap-sse, or github ${ownername}/${reponame}

        Return:
            server_tools_dict, Note: remote servers might not be available
    """
    server_tools_dict = {}
    try:
        union_server_ids = set.union(set(servers_tools_dict_remote.keys()), set(server_tools_dict_local.keys()))
        for key in union_server_ids:
                servers_remote = servers_tools_dict_remote[key] if key in servers_tools_dict_remote else []
                servers_local = server_tools_dict_local[key] if key in server_tools_dict_local else []
                servers_union = servers_remote + servers_local

                # remove duplicate
                if len(servers_union) > 0:
                    server_tools_dict[key] = servers_union
        available_tools_keys = server_tools_dict.keys()
        logging.info(f"Dispatcher Agent Merging Remote and Local Tools Available: {available_tools_keys}, server_tools_dict: {server_tools_dict} ")

        return server_tools_dict
    except Exception as e:
        print (e)
        return server_tools_dict

def parse_available_tools(server_tools_dict):
    available_tools = []
    toolname_to_server_dict = {}
    try:
        for server_name, tools in server_tools_dict.items():
            available_tools.extend(tools)
            for tool in tools:
                tool_name = tool["name"] if "name" in tool else ""
                description = tool["description"] if "description" in tool else ""
                input_schema = tool["input_schema"] if "input_schema" in tool else {}
                ## duplicate tool name, key: tool_name, value: list of server_name list
                if tool_name in toolname_to_server_dict:
                    cur_list = toolname_to_server_dict[tool_name]
                    cur_list.append(server_name)
                    toolname_to_server_dict[tool_name] = cur_list
                else:
                    toolname_to_server_dict[tool_name] = [server_name]
        return available_tools, toolname_to_server_dict

    except Exception as e:
        logging.error(e)
        return available_tools, toolname_to_server_dict

def get_tool_choose_result_html(tool_id, tool_name, tool_arguments):
    """
        tool_name: str
        tool_arguments: dict, e.g. {"param1": "value1", "param2": "value2"}
    """
    try:
        tool_arguments_str = json.dumps(tool_arguments, sort_keys = True, indent = 4, ensure_ascii=False)
        tool_choose_result = prompt_tool_choose_result.format(tool_name=tool_name, tool_arguments = tool_arguments_str)
        return tool_choose_result
    except Exception as e:
        logging.error(f"get_tool_choose_result_html failed with error {e}")
        return ""

def get_tool_call_input_params(messages, kwargs):
    """
        Args:
            messages: list of message
            kwargs: 'context' contains tool_id, tool_name, tool_arguments, toolname_to_server_dict

        Return:
            tool_schema
            toolname_to_server_dict
    """
    try:
        if len(messages) <= 1:
            return None          
        message_tool_args = messages[-2]
        message_action = messages[-1]

        print (f"DEBUG: get_tool_call_result_message message_tool_args {message_tool_args}")
        print (f"DEBUG: get_tool_call_result_message message_action {message_action}")

        ## parse from the front_End of interleaved 
        context_dict_str = message_tool_args[KEY_CONTEXT] if KEY_CONTEXT in message_tool_args else ""
        context_dict = {}
        try:
            context_dict = json.loads(context_dict_str)
        except Exception as e:
            print (e)
        print (f"get_tool_call_result_message context_dict {context_dict}")

        tool_id = context_dict[KEY_TOOL_ID] if KEY_TOOL_ID in context_dict else ""
        tool_name = context_dict[KEY_TOOL_NAME] if KEY_TOOL_NAME in context_dict else ""
        tool_arguments = context_dict[KEY_TOOL_ARGUMENTS] if KEY_TOOL_ARGUMENTS in context_dict else {}
        tool_arguments_type = type(tool_arguments)
        
        toolname_to_server_dict = context_dict[KEY_TOOLNAME_TO_SERVER_DICT] if KEY_TOOLNAME_TO_SERVER_DICT in context_dict else {}
        toolname_to_server_dict_type = type(toolname_to_server_dict)
        
        print (f"get_tool_call_result_message context_dict tool_arguments {tool_arguments} type {tool_arguments_type}")
        print (f"get_tool_call_result_message context_dict toolname_to_server_dict {toolname_to_server_dict} type {toolname_to_server_dict_type}")

        server_name_list = toolname_to_server_dict[tool_name] if tool_name in toolname_to_server_dict else None 

        logging.info(f"LLM Choosing Tools {tool_name} and Arguments {tool_arguments} From Server {server_name_list} with toolname_to_server_dict {toolname_to_server_dict}")

        # assembly tool_schema
        tool_schema = {
            "id": tool_id,
            "name": tool_name,
            "arguments" : tool_arguments
        }

        return tool_schema, toolname_to_server_dict
    except Exception as e:
        logging.error(e)
        return {}, {}


async def get_tool_call_result_message(kwargs, tool_schema, toolname_to_server_dict):
        """
            parse the last message from messages
            message [msg_tool_arg, msg_action]
        """
        message_tool_result, tool_results_text = [], ""

        print (f"get_tool_call_result_message context_dict tool_schema {tool_schema}")
        print (f"get_tool_call_result_message context_dict toolname_to_server_dict {toolname_to_server_dict}")

        tool_id = tool_schema["id"] if "id" in tool_schema else ""
        tool_name = tool_schema["name"] if "name" in tool_schema else ""
        tool_arguments = tool_schema["arguments"] if "arguments" in tool_schema else ""
        server_name_list = toolname_to_server_dict[tool_name] if tool_name in toolname_to_server_dict else None 
        logging.info(f"LLM Choosing Tools {tool_schema} From Server {server_name_list} with toolname_to_server_dict {toolname_to_server_dict}")

        if server_name_list is not None and len(server_name_list) > 0:
            server_name_choice = server_name_list[0]

            server_tools_runnable = get_available_tools_from_registry(gv._global_server_registry)
            print ("DEBUG: server_tools_runnable size|" + str(len(server_tools_runnable)))

            runnable_tools = server_tools_runnable[server_name_choice] if server_name_choice in server_tools_runnable else []
            runnable_tools_namelist = [tool["name"] if "name" in tool else "" for tool in runnable_tools]
            local_installed = True if tool_name in runnable_tools_namelist else False 

            print (f"DEBUG: server chosen by LLM {server_name_choice}|local_installed {local_installed}")

            if local_installed:
                if MOCK_RESPONSE_SWITCH:
                    print (f"DEBUG: call_tools_base MOCK_RESPONSE_SWITCH on mock response")
                    ## add tool result to chat history
                    mock_tool_calls, mock_call_messages = mock_call_claude_37_sonnet_tools_result()
                    ## append message list, effective next while run
                    message_tool_result.extend(mock_call_messages)
                else:

                    print (f"DEBUG: call_tools_base {server_name_choice}|tool_name {tool_name} tool_arguments {tool_arguments}")

                    result = await call_tools_base(server_name_choice, tool_name, tool_arguments)

                    success = result[KEY_SUCCESS] if KEY_SUCCESS in result else False
                    tool_results_text = result[KEY_CONTENT] if KEY_CONTENT in result else False
                    if success:
                        tool_results_text = result[KEY_CONTENT] if KEY_CONTENT in result else ""
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
                        message_tool_result.extend([
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
                        logging.info(f"Running Tools {tool_name} and Result {tool_results_text}")

                    else:
                        logging.info(f"Running Tools {tool_name} Result Error and result is {result}" )
            else:
                print ("DEBUG: Installing MCP Server From Remote Marketplace")
        return message_tool_result, tool_results_text

def routing_branch(query):
    """
        <action></action>
    """
    result = {}
    branch = BRANCH_NORMAL
    try:
        action_tag_regex = r'<action>(.*?)</action>'
        match = re.search(action_tag_regex, query)
        if match is not None:
            action = match.group(1)
            result["action"] = action
            branch = BRANCH_AGENT_ACTION
        return branch, result
    except Exception as e:
        print (e)
        return branch, result

def filter_valid_tools_openai(tools):
    """ filter valid tools
        e.g. {'type': 'function', 'function': {'name': '', 'description': '', 'parameters': {}}}
    """
    valid_tools = []
    for tool in tools:
        try:
            function_schema = tool["function"] if "function" in tool else {}
            tool_name = function_schema["name"] if "name" in function_schema else ""
            tool_description = function_schema["description"] if "description" in function_schema else ""
            tool_parameters = function_schema["parameters"] if "parameters" in function_schema else {}
            ## valid
            if tool_name != "" and tool_description != "":
                valid_tools.append(tool)
        except Exception as e:
            logger.error(e)
    return valid_tools


def filter_valid_tools_claude(tools):
    """ filter valid tools
        e.g. {'name': '', 'description': '', 'input_schema': {}}
    """
    valid_tools = []
    for tool in tools:
        try:
            tool_name = tool["name"] if "name" in tool else ""
            tool_description = tool["description"] if "description" in tool else ""
            tool_parameters = tool["input_schema"] if "input_schema" in tool else {}
            ## valid
            if tool_name != "" and tool_description != "":
                valid_tools.append(tool)
        except Exception as e:
            logger.error(e)
    return valid_tools

def get_available_tools_from_registry(global_server_registry):
    """
        Args: 
            global_server_registry: Dict, global_server_registry
            registry is the dict of started server and available tools, there are multiple strategies for tool rag to a small pool of tools,
            which will be feed to LLM to choose tools and arguments.
        Return:
            Dict
    """
    available_tools_dict = {}
    available_tools_cnt = 0
    logging.info(f"global_server_registry {global_server_registry}")
    for server_id, registry in gv._global_server_registry.items():    
        config = registry["config"] if "config" in registry else {}
        process = registry["process"] if "process" in registry else None
        status = registry["status"] if "status" in registry else "Off"        
        tools = registry["tools"] if "tools" in registry else []
        if status == "On" and len(tools) > 0:
            valid_tools = filter_valid_tools_claude(tools)
            available_tools_dict[server_id] = valid_tools
            available_tools_cnt += len(valid_tools)
    logging.info(f"get_available_tools_from_registry tools size {available_tools_cnt}, available_tools_dict {available_tools_dict}")
    return available_tools_dict

def call_response_generation(messages, kwargs):
    """
        Args:
            messages: list of dict message
            kwargs: dict
        Return:
            yield generator
    """
    model_selection = kwargs[KEY_MODEL_SELECTION] if KEY_MODEL_SELECTION in kwargs else MODEL_SELECTION_CLAUDE_37
    if model_selection == MODEL_SELECTION_QWEN3_MAX:
        for chunk in call_response_generation_qwen_max(messages):
            yield chunk
    elif model_selection == MODEL_SELECTION_QWEN3_PLUS:
        for chunk in call_response_generation_qwen_plus(messages):
            yield chunk
    elif model_selection in [MODEL_SELECTION_CLAUDE_37, MODEL_SELECTION_CLAUDE_OPUS_4, MODEL_SELECTION_GPT4O, MODEL_SELECTION_GEMINI_25_FLASH]:
        for chunk in call_response_generation_qwen_plus(messages):
            yield chunk
    else:
        print (f"Model Selection {model_selection} is not supported, Set Qwen as Default")
        for chunk in call_response_generation_qwen_plus(messages):
            yield chunk

def main():
    """
    """
    print ("Initializating workflow...")

if __name__ == "__main__":
    main()
