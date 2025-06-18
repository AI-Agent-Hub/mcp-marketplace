document.addEventListener('DOMContentLoaded', function() {
    const jsonData = {
        user: {
            id: 12345,
            name: "User",
            email: "zhangsan@example.com",
            preferences: {
                theme: "dark",
                notifications: true
            }
        },
        timestamp: "2025-06-02T08:30:00Z"
    };

    const container = document.querySelector('.tool-call-container');
    const header = document.querySelector('.tool-call-header');
    const arrow = document.querySelector('.arrow');
    const contentArea = document.querySelector('.collapsible-content');

    if (header != null) {
        header.addEventListener('click', function() {
            const isExpanded = contentArea.classList.toggle('expanded');
            arrow.textContent = isExpanded ? '▼' : '▶';
            
            if (isExpanded && contentArea.children.length === 0) {
                addParametersSection(jsonData);
                addButtonOptionsSection();
                simulateAsyncResult();
            }
        });
    }

    function addParametersSection(data) {
        const paramsRow = document.createElement('div');
        paramsRow.className = 'div_tool_call_row';
        
        const paramsTitle = document.createElement('h3');
        paramsTitle.textContent = 'Parameters';
        
        const jsonContainer = document.createElement('div');
        jsonContainer.className = 'div_tool_call_json';
        jsonContainer.textContent = formatJson(JSON.stringify(data));
        
        paramsRow.appendChild(paramsTitle);
        paramsRow.appendChild(jsonContainer);
        contentArea.appendChild(paramsRow);
    }


    // [{"button" ,"action":"ACCEPT"}, {"action":"ACCEPT"}]
    function addButtonOptionsSection(data) {
        const buttonOptionsRow = document.createElement('div');
        buttonOptionsRow.classList.add('div_tool_call_row', 'div_tool_call_row_options');
        buttonOptionsRow.innerHTML = '<input type="button" class="agent-button-base agent-button-highlight" value="ACCEPT" set_on_click="true"><input type="button" class="agent-button-base" value="REJECT" set_on_click="true">';        
        contentArea.appendChild(buttonOptionsRow);
    }

    // 
    function addResultsSection(resultData) {
        const resultsRow = document.createElement('div');
        resultsRow.className = 'div_tool_call_row results-section';
        
        const resultsTitle = document.createElement('h3');
        resultsTitle.textContent = 'Results';
        
        const jsonContainer = document.createElement('div');
        jsonContainer.className = 'div_tool_call_json';
        jsonContainer.textContent = formatJson(JSON.stringify(resultData));
        
        resultsRow.appendChild(resultsTitle);
        resultsRow.appendChild(jsonContainer);
        contentArea.appendChild(resultsRow);
    }

    function formatJson(jsonString) {
        try {
            return JSON.stringify(JSON.parse(jsonString), null, 2);
        } catch (e) {
            console.error('JSON Format Error:', e);
            return jsonString;
        }
    }

    function simulateAsyncResult() {
        setTimeout(() => {
            const resultData = {
                status: "success",
                execution_time: "320ms",
                data_processed: 42,
                message: "Finished"
            };
            addResultsSection(resultData);
        }, 1500);
    }

});
