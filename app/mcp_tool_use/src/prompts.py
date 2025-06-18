# -*- coding: utf-8 -*-

prompt_query_plan = '''
    **Background**
    You are a search engine expert who can analyze users' search intent and generate a few keywords to search for suitable tools to fullfill users intent.

    **Tasks**:
    - Analyze users' intent
    - Separate the original Complicated Tasks into a few sub tasks 
    - Identify what type of tools need to be used by each sub task, so the AI agent can accomplish the tasks and get the tool_result.
    - Output a list of keywords or queries to search the tools from open MCP Marketplace to get the tools schema

    **Output Format**:
    - The output must be in a valid Json format containing the following fields: query

    **Example**:
    **User Query**:
    Please find the stock price of Apple, Tesla and Alibaba in various stock market and plot the chart.
    **Output**:
    ```
    {{"query": ["stock","finance data","plot"]}}
    ```
    **User Query**:
    Please help me find the route between New York University and Time Square and Hail a Uber Driver Order
    **Output**:
    ```
    {{"query": ["map","route planning","ride hailing"]}}
    ```
    **User Query**
    {user_input}
'''


prompt_tool_choose_result = ''' 
    <div class="tool-call-container">
        <div class="tool-call-header">
            <span class="arrow">▶</span>
            <span class="header-text">Call Tool {tool_name} </span>
        </div>
        <div class="collapsible-content">
            <div class="div_tool_call_row"><h3>Parameters</h3><div class="div_tool_call_json"> {tool_arguments} </div></div>
            <div class="div_tool_call_row div_tool_call_row_options">
                <input type="button" class="agent-button-base agent-button-highlight" value="ACCEPT" set_on_click="true">
                <input type="button" class="agent-button-base" value="REJECT" set_on_click="true">
            </div>
            <div class="div_tool_call_row results-section"><h3>Results</h3><div class="div_tool_call_json"></div></div>
        </div>
    </div>

'''

