document.addEventListener('DOMContentLoaded', () => {
    const localServersListDiv = document.getElementById('local-servers-list');
    const marketplaceServersListDiv = document.getElementById('marketplace-servers-list');
    const fetchMarketplaceBtn = document.getElementById('fetch-marketplace-btn');

    const queryServerIdInput = document.getElementById('query-server-id');
    const queryToolNameInput = document.getElementById('query-tool-name');
    const queryToolInputTextarea = document.getElementById('query-tool-input');

    const queryToolParameters = document.querySelector(".form-group-parameters");
    const sendQueryBtn = document.getElementById('send-query-btn');
    const queryResultPre = document.getElementById('query-result');

    const installModal = document.getElementById('install-modal');
    const modalServerNameSpan = document.getElementById('modal-server-name');
    const modalGithubUrlSpan = document.getElementById('modal-github-url');
    const modalInstallCommandInput = document.getElementById('modal-install-command');
    const modalConfirmInstallBtn = document.getElementById('modal-confirm-install-btn');
    const closeModalBtn = installModal.querySelector('.close-button');

    let currentMarketplaceServerForInstall = null;

    async function apiCall(url, method = 'GET', body = null) {
        try {
            const options = {
                method,
                headers: { 'Content-Type': 'application/json' },
            };
            if (body) {
                options.body = JSON.stringify(body);
            }
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(`HTTP error ${response.status}: ${errorData.detail || 'Unknown error'}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API call to ${url} failed:`, error);
            alert(`Error: ${error.message}`); // Simple error display
            throw error;
        }
    }


    function addToolsInspector(target) {
        if (target == null) {
            return;
        }
        try {
            // 
            var serverId = "";
            var toolName = "";
            // const serverItem = target.querySelector(".server-item");
            const serverItem = target.parentElement.parentElement;
            if (serverItem != null) {
                // const header = serverItem.getElementsByTagName("h3");
                const serverIdElem = serverItem.querySelector(".div_server_id");
                if (serverIdElem != null) {
                    serverId = serverIdElem.innerText
                }
            }
            const toolSelectedElem = target.getElementsByTagName("a");
            if (toolSelectedElem != null && toolSelectedElem.length > 0) {
                toolName = toolSelectedElem[0].innerText;
            }            


            const toolParameterList = target.getElementsByClassName("tool_parameter");
            if (toolParameterList != null) {

                // Clear Existing Tools
                // clear existing query Tool Parameters
                queryToolParameters.innerHTML = "";
                for (var i = 0; i < toolParameterList.length; i++) {
                    var toolParam = toolParameterList[i];

                    var toolParamNameElem = toolParam.querySelector(".tool_parameter_name");
                    var toolParamTypeElem = toolParam.querySelector(".tool_parameter_type");
                    var toolParamDescriptionElem = toolParam.querySelector(".tool_parameter_description");

                    var toolParamName = (toolParamNameElem != null)?toolParamNameElem.textContent: "";
                    toolParamName = toolParamName.replace(":", "");
                    var toolParamType = (toolParamTypeElem != null)?toolParamTypeElem.textContent: "";
                    var toolParamDescription = (toolParamDescriptionElem != null)?toolParamDescriptionElem.textContent: "";

                    const toolParamDiv = document.createElement('div');
                    toolParamDiv.classList.add('form-group');
                    toolParamDiv.innerHTML = `
                        <label for="query-param-${toolParamName}">${toolParamName}</label>
                        <input type="text" id="query-param-${toolParamName}" placeholder="${toolParamType}, ${toolParamDescription}">
                    `;
                    queryToolParameters.appendChild(toolParamDiv);
                }
            }
            var querySection = document.querySelector(".query-section");
            if (querySection != null) {
                var serverIdElem = querySection.querySelector("#query-server-id");
                var toolNameElem = querySection.querySelector("#query-tool-name");
                var toolInputElem = querySection.querySelector("#query-tool-input");

                serverIdElem.value = serverId;
                toolNameElem.value = toolName;
            }

        } catch (err) {
            console.log(err);
        }
    }

    function renderServerItem(server, isLocal) {
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('server-item');

        command_list = server.command

        tools = server.tools
        toolListHtml = ""
        for (var i = 0; i < tools.length; i++) {
            toolName = tools[i].name;
            description = tools[i].description;
            //inputSchema = tools[i].input_schema;
            input_schema = tools[i].input_schema;
            // .input_schema
            // .input_schema.properties, .input_schema.properties.param1, 
            // .input_schema.properties.param1.type, .input_schema.properties.param1.description
            var toolParamListHtml = "";
            if (input_schema != null) {
                var properties = input_schema.properties;
                if (properties != null) {
                    let propertyEntries = Object.entries(properties);

                    propertyEntries.forEach(([key, value]) => {
                        var paramName = key;
                        var paramType = (value["type"] != null)?value["type"]:"";
                        var paramDescription = (value["description"] != null)?value["description"]:"";
                        var paramHtml = `<div class="tool_parameter">
                            <div class="tool_parameter_name">${paramName}<a>:</a></div>
                            <div class="tool_parameter_type">${paramType}</div>
                            <div class="tool_parameter_description">${paramDescription}</div>
                        </div>`;
                        toolParamListHtml += paramHtml;
                    });
                }
            }
            toolListHtml += `<div class="div_server_tool">
                <a class="a_tool_name">${toolName}</a>
                <div class="div_server_tool_hint">
                    <h4>Description</h4>
                    <div class="tool_description">${description}</div>
                    <h4>Parameters</h4>
                    <div class="tool_param_list">
                        ${toolParamListHtml}
                    </div>
                </div>
                </div>`;
        }
        toolHtml = `<p>Tools: </p><div class="div_server_tool_grid">${toolListHtml}</div>`

        itemDiv.innerHTML = `
            <h3>${server.name}</h3>
            <h3 class="div_server_id" style="display:none">${server.id}</h3>
            ${toolHtml}
            <p>${server.description || 'No description.'}</p>
            ${isLocal ? `<p>Command: <code>${server.command ? server.command : 'N/A'}</code></p>` : ''}
            ${server.github_url ? `<p>GitHub: <a href="${server.github_url}" target="_blank">${server.github_url}</a></p>` : ''}
            ${isLocal && server.tool_definitions_path ? `<p>Tools Path: <code>${server.tool_definitions_path}</code></p>` : ''}
            ${isLocal ? `<p>Status: <span class="status status-${server.status}">${server.status}</span></p>` : ''}
            <div class="actions">
                ${isLocal ? `
                    <button class="enable-btn" data-id="${server.id}" ${server.status === 'On' ? 'disabled' : ''}>Enable</button>
                    <button class="disable-btn" data-id="${server.id}" ${server.status !== 'On' ? 'disabled' : ''}>Disable</button>
                    <button class="restart-btn" data-id="${server.id}">Restart</button>
                    <button class="export-btn" data-id="${server.id}">Export</button>
                ` : `
                    <p>Suggested Install Command: <code>${server.install_command || 'N/A'}</code></p>
                    <button class="install-btn" data-id="${server.id}">Install</button>
                `}
            </div>
        `;

        return itemDiv;
    }

    async function loadLocalServers() {
        localServersListDiv.innerHTML = 'Loading...';
        try {
            const servers = await apiCall('/api/servers/local');

            console.log(servers);

            localServersListDiv.innerHTML = ''; 
            if (servers.length === 0) {
                localServersListDiv.innerHTML = '<p>No local servers configured in mcp.json.</p>';
            } else {
                servers.forEach(server => {
                    localServersListDiv.appendChild(renderServerItem(server, true));
                });
            }

        } catch (error) {
            localServersListDiv.innerHTML = '<p>Error loading local servers.</p>';
        }
    }

    async function loadMarketplaceServers() {
        marketplaceServersListDiv.innerHTML = 'Fetching marketplace servers...';
        try {
            const servers = await apiCall('/api/servers/marketplace');
            marketplaceServersListDiv.innerHTML = ''; // Clear loading
            if (servers.length === 0) {
                marketplaceServersListDiv.innerHTML = '<p>No servers found in the marketplace or error fetching.</p>';
            } else {
                servers.forEach(server => {
                    marketplaceServersListDiv.appendChild(renderServerItem(server, false));
                });
            }
        } catch (error) {
            marketplaceServersListDiv.innerHTML = `<p>Error loading marketplace servers: ${error.message}</p>`;
        }
    }

    async function handleServerAction(serverId, action) {
        try {
            alert(`${action} ${serverId}`);
            const result = await apiCall(`/api/server/${serverId}/${action}`, 'POST');
            alert(result.message);
            loadLocalServers(); // Refresh list
        } catch (error) {
            // Error already alerted by apiCall helper
        }
    }

    async function handleServerExport(serverId, action) {
        try {
            alert(`${action} ${serverId}`);
            const result = await apiCall(`/api/server/${serverId}/${action}`, 'POST');
            if (result != null) {
                resultJson = result.schema;
                var configElem = document.getElementById('json-content')
                if (configElem != null) {
                    configElem.textContent = JSON.stringify(resultJson, null, 2);
                }
                openModal();
            }
            loadLocalServers(); // Refresh list
        } catch (error) {
            // Error already alerted by apiCall helper
            console.log(error);
        }
    }

    function openInstallModal(server) {
        currentMarketplaceServerForInstall = server;
        modalServerNameSpan.textContent = server.name;
        modalGithubUrlSpan.textContent = server.github_url;
        modalInstallCommandInput.value = server.install_command || '';
        installModal.style.display = 'flex';
    }

    closeModalBtn.onclick = () => {
        installModal.style.display = 'none';
        currentMarketplaceServerForInstall = null;
    };

    window.onclick = (event) => {
        if (event.target == installModal) {
            installModal.style.display = 'none';
            currentMarketplaceServerForInstall = null;
        }
    };

    modalConfirmInstallBtn.onclick = async () => {
        if (!currentMarketplaceServerForInstall) return;

        const installPayload = {
            server_id: currentMarketplaceServerForInstall.id,
            name: currentMarketplaceServerForInstall.name,
            github_url: currentMarketplaceServerForInstall.github_url,
            install_command: modalInstallCommandInput.value,
            // These should ideally come from marketplace data if available
            start_command: currentMarketplaceServerForInstall.start_command || ["echo", "Start command not configured after install"],
            tool_definitions_path: currentMarketplaceServerForInstall.tool_definitions_path || null
        };

        try {
            const result = await apiCall('/api/server/install', 'POST', installPayload);
            alert(result.message);
            if (result.success) {
                installModal.style.display = 'none';
                currentMarketplaceServerForInstall = null;
                loadLocalServers(); // Refresh local servers as it should now be there
            }
        } catch (error) {
            // Error already alerted
        }
    };


    async function handleSendQuery() {
        const serverId = queryServerIdInput.value.trim();
        const toolName = queryToolNameInput.value.trim();
        const toolInputStr = queryToolInputTextarea.value.trim();

        const toolParamList = queryToolParameters.getElementsByClassName("form-group");
        if (!serverId || !toolName || (!toolInputStr && toolParamList == null )) {
            queryResultPre.textContent = 'Error: Server ID, Tool Name, and Tool Parameters or Tool Inputs are required.';
            return;
        }
        
        // parse ToolInputJson
        let toolInputJson = {};
        try {
            if (toolInputStr != "") {
                toolInputJson = JSON.parse(toolInputStr);
            }
        } catch (e) {
            // queryResultPre.textContent = `Error: Invalid JSON in Tool Input.\n${e.message}`;
            console.log(e);
        }
        var toolParameters = {};
        if (toolParamList != null) {
            for (var i = 0; i < toolParamList.length; i++) {
                var toolParamElem = toolParamList[i];
                var labelElem = toolParamElem.querySelector("label");
                var inputElem = toolParamElem.querySelector("input");
                var paramName = (labelElem != null)?labelElem.innerText.trim(): "";
                var paramValue = (inputElem != null)?inputElem.value.trim(): "";
                toolParameters[paramName] = paramValue;
            }
        }
        // merge result
        var toolInput = (Object.keys(toolParameters).length > 0)?toolParameters:toolInputJson;
        queryResultPre.textContent = 'Sending query...';
        try {
            const response = await apiCall('/api/query', 'POST', { server_id: serverId, tool_name: toolName, tool_input: toolInput });
            if (response.success) {
                queryResultPre.textContent = `Success:\n${JSON.stringify(response.data, null, 2)}`;
            } else {
                queryResultPre.textContent = `Error:\n${response.error}`;
            }
        } catch (error) {
             queryResultPre.textContent = `Failed to send query or process response:\n${error.message}`;
        }
    }

    // --- Event Listeners ---
    // fetchMarketplaceBtn.addEventListener('click', loadMarketplaceServers);
    sendQueryBtn.addEventListener('click', handleSendQuery);

    //
    function openModal() {
        document.querySelector('.json-modal').style.display = 'block';
        document.querySelector('.modal-overlay').style.display = 'block';
    }

    const copyJsonBtn = document.querySelector('.copy-btn');
    copyJsonBtn.addEventListener('click', (e) => {
            const jsonContent = document.getElementById('json-content').textContent;
            navigator.clipboard.writeText(jsonContent)
                .then(() => {
                        const btn = document.querySelector('.copy-btn');
                        btn.classList.add('copy-success');
                        setTimeout(() => btn.classList.remove('copy-success'), 2000);
                })
                .catch(err => alert('Copy Failed: ' + err));
            alert("Copy MCP Config Successfully!")
        }
    );

    function closeModal() {
        document.querySelector('.json-modal').style.display = 'none';
        document.querySelector('.modal-overlay').style.display = 'none';
        history.pushState("", document.title, window.location.pathname);
    };

    const closePanelBtn = document.querySelector('.close-modal-btn');
    closePanelBtn.addEventListener('click', (e) => {
            closeModal();
        }
    );


    // filter and sort Items
    function filterAndSortList() {
        let searchTerm = "";
        if (searchInput != null) {
            searchTerm = searchInput.value.trim().toLowerCase();
        }

        const sortValue = sortSelect.value;
                
        let items = originalItems.map(item => item.cloneNode(true));
                
                if (searchTerm) {
                    items = items.filter(item => {
                        //const text = item.querySelector('.div_server_id').textContent.toLowerCase();
                        let text = "";
                        const textItem = item.querySelector('.div_server_id');
                        if (textItem != null) {
                            text = textItem.textContent.toLowerCase();
                        }
                        return text.includes(searchTerm);
                    });
                    
                    items.forEach(item => {
                        // const textElement = item.querySelector('.item-text');
                        // const originalText = textElement.textContent;
                        const textItem = item.querySelector('.div_server_id');
                        const originalText = textItem.textContent;
                        let text = "";
                        if (textItem != null) {
                            text = textItem.textContent.toLowerCase();
                        }
                        const regex = new RegExp(`(${searchTerm})`, 'gi');
                        textItem.innerHTML = originalText.replace(regex, '<span class="highlight">$1</span>');
                    });
                }
                
                if (items.length > 0) {
                    items.sort((a, b) => {
                        let aText = "";
                        if (a.querySelector('.div_server_id') != null) {
                            aText = a.querySelector('.div_server_id').textContent.toLowerCase();
                        }
                        let bText = "";
                        if (b.querySelector('.div_server_id') != null) {
                            bText = b.querySelector('.div_server_id').textContent.toLowerCase();
                        }
                        let aStatus = 0;
                        var aStatusTag = a.querySelector('.status');
                        if (aStatusTag != null && aStatusTag.classList.contains('status-On')) {
                            aStatus = 1;
                        } else {
                            aStatus = 0;
                        }
                        let bStatus = 0;
                        var bStatusTag = b.querySelector('.status');
                        if (bStatusTag!= null && bStatusTag.classList.contains('status-On')) {
                            bStatus = 1;
                        } else {
                            bStatus = 0;
                        }                        
                        switch(sortValue) {
                            case 'text-asc': 
                                return aText.localeCompare(bText);
                            case 'text-desc': 
                                return bText.localeCompare(aText);
                            case 'status-asc': 
                                return aStatus - bStatus;
                            case 'status-desc': 
                                return bStatus - aStatus;
                            default: 
                                return 0;
                        }
                    });
                }
                
                itemList.innerHTML = '';
                
                if (items.length === 0) {
                    server = {id: "no_result", tools: [], name: "no_result", command: "", description: "No Results Match Found..."}
                    const newServer = renderServerItem(server, true);
                    itemList.appendChild(newServer);
                } else {
                    items.forEach(item => itemList.appendChild(item));
                }
    }


    let itemList, originalItems, searchInput, sortSelect;
    async function initPage() {
        await loadLocalServers();
        localServersListDiv.addEventListener('click', (event) => {
            const target = event.target;
            if (target.classList.contains('enable-btn')) {
                const serverId = target.dataset.id;
                handleServerAction(serverId, 'enable');
            }
            if (target.classList.contains('disable-btn')) {
                const serverId = target.dataset.id;
                handleServerAction(serverId, 'disable');
            }
            if (target.classList.contains('restart-btn')) {
                const serverId = target.dataset.id;
                handleServerAction(serverId, 'restart');
            }
            if (target.classList.contains('export-btn')) {
                const serverId = target.dataset.id;
                handleServerAction(serverId, 'export');
            }
            // click on tool tag a
            if (target.classList.contains('div_server_tool') || target.parentNode.classList.contains('div_server_tool')) {
                if (target.classList.contains('a_tool_name')) {
                    addToolsInspector(target.parentNode);
                } else if (target.classList.contains('div_server_tool')) {
                    addToolsInspector(target);
                } else {
                }
            }
            
        });

        searchInput = document.getElementById('searchInput');
        sortSelect = document.getElementById('sortSelect');
        
        itemList = document.getElementById('local-servers-list');
        originalItems = Array.from(itemList.children);

        searchInput.addEventListener('input', filterAndSortList);
        sortSelect.addEventListener('change', filterAndSortList);
        
        filterAndSortList();
      
    }
    initPage();

});
