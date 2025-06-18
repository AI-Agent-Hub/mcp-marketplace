import logging
import codecs
import time
import os

def read_file(file_path):
    lines = []
    lines_clean = []
    try:
        with codecs.open(file_path, "r", "utf-8") as file:
            lines = file.readlines()
        for line in lines:
            line_clean = line.strip()
            line_clean = line_clean.replace("\n", "")
            lines_clean.append(line_clean)
        return lines_clean
    except Exception as e:
        #print ("DEBUG: read_file failed file_path %s" % file_path)
        #print (e)
        return lines_clean

def save_file(file_path, lines):
    try:
        with codecs.open(file_path, "w", "utf-8") as file:
            for line in lines:
                file.write(line + "\n")
        file.close()
    except Exception as e:
        #print (e)
        return

def read_file_traverse(directory, extension=""):
    try:
        travers_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if extension != "":
                    if file.endswith(extension):
                        # print(os.path.join(root, file))
                        file_path = os.path.join(root, file)
                        travers_files.append(file_path)
                else:
                    file_path = os.path.join(root, file)
                    travers_files.append(file_path)
        return travers_files
    except Exception as e:
        # logging.error(e)
        return []

def get_current_timestamp():
    import time
    timestamp = int(time.time())
    return timestamp

def get_current_datetime():
    import datetime    
    now = datetime.datetime.now()
    datetime = now.strftime('%Y-%m-%d %H:%M:%S')
    return datetime

def load_available_mcp_servers(input_file):
    """
        load_available_mcp_servers("../data/mcp_location.json")
        format: {"mcpServers": []}        
    """
    try:
        mcp_config_files = read_file(input_file) 
        mcp_config_str = "".join(mcp_config_files)
        mcp_config = json.loads(mcp_config_str)
        mcp_servers_config_map = mcp_config["mcpServers"] if "mcpServers" in mcp_config else {}
        return mcp_servers_config_map
    except Exception as e:
        logging.error(e)
        return {}

def load_available_tools(folder, valid_extension = ["json"]):
    """
        load available tools from folder
        format: {"tools": []}
    """
    server_tools_dict = {}
    try:
        for file in os.listdir(folder):
            path_items = file.split("/")
            file_item = path_items[-1]
            extension = file_item.split(".")[-1]
            if extension not in valid_extension:
                continue        
            abs_file_path = os.path.join(folder, file)
            server_name = file.replace(".json", "")
            tools = []
            json_str = "".join(read_file(abs_file_path))
            tool_dict = {}
            try:
                tool_dict = json.loads(json_str)
            except Exception as e:
                print (e)
            tools_list = tool_dict["tools"] if "tools" in tool_dict else []    
            server_tools_dict[server_name] = tools_list
    except Exception as e:
        logging.error(e)
    return server_tools_dict

def assembly_message(type, format, content, **kwargs):
    """
        type: role
        format: text/img        
        section: reason/tool/response

        content:
            str,
            dict
    """
    if "section" in kwargs:
        section = kwargs["section"] if "section" in kwargs else ""
        messageId = kwargs["message_id"] if "message_id" in kwargs else ""
        return {"type": type, "format": format, "content": content, "section": section, "message_id": messageId}
    else:
        messageId = kwargs["message_id"] if "message_id" in kwargs else ""
        return {"type": type, "format": format, "content": content, "section": "", "message_id": messageId}
