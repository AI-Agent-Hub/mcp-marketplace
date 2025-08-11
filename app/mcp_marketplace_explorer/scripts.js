const config_deepnlp = {
    endpoint: "https://www.deepnlp.org/api/mcp_marketplace/v1",
    inputParams: {"field": "MCP SERVER", "page_id": 0, "page_size": 20},
    mapper: function(data) {
            var itemMap = new Map(Object.entries(data.item_map));            
            var indexMap = new Map(Object.entries(data.page_id_map));
            return {"item_map": itemMap, "page_index_map": indexMap};
    },
    paginationParams: {"query": "MCP SERVER", "count_per_page": 20, "page_id": 0},
    extraParams: {"field": "MCP SERVER", "subfield": ""},
    paginationParamsMapper: function(requiredParams, extraParams) {
        var mergeParams = Object.assign({}, requiredParams);
        mergeParams["field"] = extraParams["field"];
        mergeParams["subfield"] = extraParams["subfield"];
        return mergeParams;
    },
    loadLocal: false,
    loadLocalData: {
        itemMap: '{"MCP SERVER":[{"content_name":"Tool 1","description":"Sales and Marketing","field":"MCP SERVER","subfield":"MAP","mcp config":{}},{"content_name":"Tool 2","description":"MAP","field":"MCP SERVER","subfield":"Payment","mcp config":{}},{"content_name":"Tool 3","description":"PAYMENT","field":"MCP SERVER","subfield":"Payment","mcp config":{}},{"content_name":"Tool 4","description":"DATABASE","field":"MCP SERVER","subfield":"DATABASE","mcp config":{}}],"MAP":[{"content_name":"Map 1","description":"Map Tool 1","field":"MCP SERVER","subfield":"MAP","mcp config":{}},{"content_name":"Map 2","description":"Map Tool 2","field":"MCP SERVER","subfield":"MAP","mcp config":{}}],"FETCH":[{"content_name":"Fetch 1","description":"Fetch 1","field":"MCP SERVER","subfield":"FETCH","mcp config":{}},{"content_name":"Fetch 2","description":"Fetch 2","field":"MCP SERVER","subfield":"FETCH","mcp config":{}}],"Browser Use":[{"content_name":"Browser Use 1","description":"Browser Use 1","field":"MCP SERVER","subfield":"Browser Use","mcp config":{}},{"content_name":"Browser Use 2","description":"Browser Use 2","field":"MCP SERVER","subfield":"Browser Use","mcp config":{}}]}',
        pageIndexMap : '{"MCP SERVER": [1, 2], "Map": [1, 2], "FETCH": [1,2], "Browser Use": [1,2]}'
    },      
    timeout: 5000
};

pulsemcp_group = "image";
pulsemcp_count_per_page = 10;
const config_pulsemcp = {
    endpoint: "https://api.pulsemcp.com/v0beta/servers",
    inputParams: {"query": pulsemcp_group, "count_per_page": pulsemcp_count_per_page},
    mapper: function(data) {
        var servers = data.servers;
        var next = data.next;
        var total_count = data.total_count;
        var itemListMapped = [];
        for (var i = 0; i < servers.length; i++) {
            var server = servers[i]
            var name = server.name;
            var url = server.url;
            var short_description = server.short_description;
            var source_code_url = server.source_code_url;
            var item = {content_name: name, description: short_description, thumbnail_picture: ""};
            itemListMapped.push(item);
        }
        var itemMap = new Map(Object.entries({[pulsemcp_group]: itemListMapped}));
        var totalPageCnt = Math.ceil(total_count/pulsemcp_count_per_page)
        var paginationPageIndex = Array.from({ length: totalPageCnt }, (_, i) => i + 1);
        var indexMap = new Map(Object.entries({[pulsemcp_group]: paginationPageIndex}));
        return {item_map: itemMap, page_index_map: indexMap};
    },
    paginationParams: {"query": pulsemcp_group, "count_per_page": pulsemcp_count_per_page, "page_id": 0},
    extraParams: {"offset": 0},   
    paginationParamsMapper: function(requiredParams, extraParams) {
        var mergeParams = Object.assign({}, requiredParams);
        mergeParams["offset"] = extraParams["offset"];
        delete mergeParams.page_id;
        return mergeParams;
    },
    loadLocal: false,
    loadLocalData: {},
    timeout: 5000
};

const configsMap = new Map([
    ["deepnlp", config_deepnlp],
    ["pulsemcp", config_pulsemcp]
]);

function getConfigByName(name) {
    return configsMap.get(name);
}

// Choose the default API Provider
const config = getConfigByName("deepnlp");

// const config = getConfigByName("pulsemcp");

// Get User Selected MCP Information
let selectedItems = new Set();

function truncateString(str, length) {
    if (str == null) {
        return "";
    }
    return str.length > length ? str.substring(0, length) + '...' : str;
}


/**
* result: result Json from http response
*/
function renderItemsGroupPagination(result, paginationRequiredParams, divDisplayToolId, divPaginationId) {

    var itemMap = result.item_map;
    var pageIndexMap = result.page_id_map;
    
    // const agentButton = document.querySelector('.agent-button');
    // const panelSectionContainer = document.querySelector('.panel_section_container');
    if (itemMap == null) {
        return;
    }
    if (pageIndexMap == null) {
        pageIndexMap = new Map();
    }
    var sectionId = (paginationRequiredParams["query"] != null)?paginationRequiredParams["query"]:"";
    var pageId = (paginationRequiredParams["page_id"] != null)?paginationRequiredParams["page_id"]:"";
    if (sectionId == null || sectionId == "") {
        return;
    }
    var itemsGrid = document.getElementById(divDisplayToolId);
    if (itemsGrid != null) {
        itemsGrid.innerHTML = "";
    }
    // // sectionID = divDisplayToolId
    var panelSectionElem = itemsGrid.parentElement;
    if (panelSectionElem == null) {
        return;
    }

    var itemData = itemMap[sectionId];
    var paginationData = pageIndexMap[sectionId];

    console.log("Section ID:" + sectionId);
    console.log(itemData);
    console.log(paginationData);

    if (itemData == null) {
        return;
    }
    itemData.forEach(schema => {

        var tool = schemaToTool(schema);
        if (tool != null) {
            tool.addEventListener('click', () => toggleSelectionAddTool(tool, schema));
            itemsGrid.appendChild(tool);
        }

    });

    var paginationElem = document.getElementById(divPaginationId);
    for (var i = 0; i < paginationData.length; i++) {
        var curPagePaginationParams = paginationRequiredParams;
        curPagePaginationParams["page_id"] = i;
        var extraParams = config.extraParams;
        var id = i + 1;
        const idElem = pageIdSelectorElement(id, curPagePaginationParams, extraParams);
        if (idElem != null) {
            paginationElem.appendChild(idElem);
        }
    }

    // update page selector, request using current page_id: pageId            
    var pSelectorList = panelSectionElem.getElementsByClassName("page_id_a");
    if (pSelectorList != null) {
        for (var j = 0; j < pSelectorList.length ; j++) {
            var selector = pSelectorList[j];
            if (j == pageId) {
                selector.classList.add("page_id_a_active");
            } else {
                selector.classList.remove("page_id_a_active");
            }
        }
    }
}


function renderItemsGroup(agentsMap, agentsIndexMap, divDisplayToolId) {
    if (agentsMap == null) {
        return;
    }
    if (agentsIndexMap == null) {
        agentsIndexMap = new Map();
    }
    // var divTemplateTools = document.querySelector(".template-tools");
    var divTemplateTools = document.getElementById(divDisplayToolId);
    if (divTemplateTools == null) {
        return;
    }

    const agentButton = document.querySelector('.agent-button');
    const panelSectionContainer = document.querySelector('.panel_section_container');
    panelSectionContainer.innerHTML = "";
    agentsMap.forEach((value, key) => {
        var sectionId = key;
        var agents = value;

        var panelSectionElem = document.getElementById(sectionId);
        if (panelSectionElem == null) {
            panelSectionElem = document.createElement('div');
            panelSectionElem.id = sectionId;
            panelSectionElem.classList.add("panel_section");
        }
        var groupHtml = document.createElement('div');
        groupHtml.innerHTML = `<h3>${sectionId}</h3>`;
        panelSectionElem.appendChild(groupHtml);

        const curItemsGrid = document.createElement('div');
        curItemsGrid.className = 'grid-container';
        agents.forEach(agent => {
                    const item = document.createElement('div');

                    var contentName = agent.content_name;
                    var abstract = truncateString(agent.description, 80);
                    var thumbnailURL = agent.thumbnail_picture;
                    var field = (agent.field != null)?agent.field:"";
                    var subfield = (agent.subfield != null)?agent.subfield:"";
                    var nameShort = "MCP"

                    var thumbnailHtml = "";
                    if (thumbnailURL != null && thumbnailURL != "") {
                        thumbnailHtml = `<img class='display_card_image_thumbnail_img' src="${thumbnailURL}"></img>`;
                    } else {
                        thumbnailHtml = `<div class="div_icon_default_name">${nameShort}</div>`;
                    }
                    var summaryHtml = `
                        <h3>${contentName}</h3>
                        <p>${abstract}</p>
                        <p>${subfield}</p>
                    `;
                    item.className = 'tool-item';
                    item.innerHTML = thumbnailHtml + summaryHtml;
                    item.addEventListener('click', () => toggleSelection(item, agent));
                    curItemsGrid.appendChild(item);
        });
        panelSectionElem.appendChild(curItemsGrid);

        var pageSelectorHtml = document.createElement('div');
        var pageIdDisplayList = agentsIndexMap.get(key);
        var pageHtml = "";
        var paginationParams = config.paginationParams;
        var extraParams = config.extraParams;
        if (pageIdDisplayList != null) {
            for (var pageId =0 ; pageId < pageIdDisplayList.length; pageId++) {
                    // update required base paginationParams
                    paginationParams["query"] = sectionId;
                    paginationParams["page_id"] = pageId;
                    // update extraParams 
                    extraParams["offset"] = pageId * paginationParams.count_per_page;
                    var pageIdDisplay = pageIdDisplayList[pageId];
                    var curPageHtml = "";
                    if (pageId == 0) {
                        curPageHtml = "<div class=\"page_id_wrapper\"><a class=\"page_id_a page_id_a_active\" onclick='pagination(" + JSON.stringify(paginationParams) + "," + JSON.stringify(extraParams) + ")'>" + pageIdDisplay + "</a></div>";
                    } else {
                        curPageHtml = "<div class=\"page_id_wrapper\"><a class=\"page_id_a\" onclick='pagination(" + JSON.stringify(paginationParams) + "," + JSON.stringify(extraParams) +")'>" + pageIdDisplay + "</a></div>";
                    }
                    pageHtml += curPageHtml;
            }
            pageSelectorHtml.innerHTML = `<div class="page_selector">${pageHtml}</div>`;
            panelSectionElem.appendChild(pageSelectorHtml);
        }
        panelSectionContainer.appendChild(panelSectionElem);
    });
}

function toggleSelection(item, agent) {
    item.classList.toggle('selected');
    const config = JSON.stringify(agent);
        
    if (selectedItems.has(config)) {
        selectedItems.delete(config);
    } else {
        selectedItems.add(config);
    }

    window.parent.postMessage({
            type: 'agentSelection',
            selected: Array.from(selectedItems).map(c => JSON.parse(c))
    }, '*');
    // update global variable
    window.agent_selected_items = selectedItems;
}


function toggleSelectionAddTool(tool, agentConfig) {
    tool.classList.toggle('selected');
    const config = JSON.stringify(agentConfig);
    
    // update global variables
    if (selectedItems.has(config)) {
        selectedItems.delete(config);
        // delete tool
        deleteMyTool(tool);

    } else {
        // addTool
        selectedItems.add(config);
        // add to frond end dom
        addMyTool(tool);
    }

    // update global variables
    window.parent.postMessage({
            type: 'agentSelection',
            selected: Array.from(selectedItems).map(c => JSON.parse(c))
    }, '*');
    // update global variable
    window.agent_selected_items = selectedItems;
}

/**
* 
* Convert Tool Element to Schema JsonObject
*/
function toolToSchema(tool) {
        schema = null
        try {
            // 
            var toolId = "";
            if (tool.querySelector(".tool_id") != null) {
                var toolIdElement = tool.querySelector(".tool_id");
                toolId = toolIdElement.textContent;
            }
            var contentName = "";
            if (tool.querySelector(".content_name") != null) {
                var contentNameElement = tool.querySelector(".content_name");
                contentName = contentNameElement.textContent;
            }
            var description = "";
            if (tool.querySelector(".description") != null) {
                var descriptionElement = tool.querySelector(".description");
                description = descriptionElement.textContent;
            }
            var category = "";
            if (tool.querySelector(".category") != null) {
                var categoryElement = tool.querySelector(".category");
                category = categoryElement.textContent;
            }
            var thumbnailPicture = "";
            if (tool.querySelector(".display_card_image_thumbnail_img") != null) {
                var imageElement = tool.querySelector(".display_card_image_thumbnail_img");
                thumbnailPicture = imageElement.src;
            }
            schema = {
                id: toolId,
                content_name: contentName, 
                description: description, 
                category: category,
                thumbnail_picture: thumbnailPicture
            }
        } catch (err) {
            console.log("toolToSchema failed...")
            console.log(err);
        }
        return schema;
}

/**
* Convert Schema JsonObject to Tool
* config.content_name
* config.description
* config.thumbnail_picture
* config.field
* config.subfield
* config.content_name_short
*/
function schemaToTool(schema) {
    try {
        // contentId should be unique
        var toolId = (schema.id != null)?schema.id:"";
        var contentName = (schema.content_name != null)?schema.content_name: "";
        if (toolId == "") {
            // id is set to content name if missing
            toolId = contentName;
        }
        var descriptionShort = truncateString(schema.description, 80);
        var thumbnailURL = schema.thumbnail_picture;
        var field = (schema.field != null)?schema.field:"";
        var subfield = (schema.subfield != null)?schema.subfield:"";
        var nameShort = (schema.content_name_short != null)?schema.content_name_short:"MCP";
        var thumbnailHtml = "";
        if (thumbnailURL != null && thumbnailURL != "") {
            thumbnailHtml = `<img class='display_card_image_thumbnail_img' src="${thumbnailURL}"></img>`;
        } else {
            thumbnailHtml = `<div class="div_icon_default_name">${nameShort}</div>`;
        }
        var summaryHtml = `
                            <a hidden="true" class="tool_id">${toolId}</a>
                            <h3 class="content_name">${contentName}</h3>
                            <p class="description">${descriptionShort}</p>
                            <p class="category">${subfield}</p>
        `;
        var deleteHtml = `<span class="delete-tool"></span>`;
        // create new div
        const newTool = document.createElement('div');
        newTool.className = 'tool-item';
        newTool.innerHTML = thumbnailHtml + summaryHtml + deleteHtml;
        return newTool;
    } catch (err) {
        console.log(err);
        return null;
    }
}



/**
* id: 1
* paginationParams: {"page_id": 0, count_per_page: 5}
*/
function pageIdSelectorElement(id, paginationParams, extraParams) {
    const newTool = document.createElement('div');
    newTool.className = 'page_id_wrapper';
    var paginationHtml = "<a class=\"page_id_a\" onclick='pagination(" + JSON.stringify(paginationParams) + "," + JSON.stringify(extraParams) +")'>" + id + "</a>";
    newTool.innerHTML = paginationHtml;
    return newTool;
}


// add dom element item to my-tools
function addMyTool(tool) {
    const myTools = document.querySelector('.my-tools');
    const newTool = tool.cloneNode(true);
    myTools.appendChild(newTool);
}

/**
* delete the copied tool from myToolsSection
* delete by same tool id
*/
function deleteMyTool(tool) {
    try {
        const myTools = document.querySelector('.my-tools');
        var targetToolId = "";
        if (tool.querySelector('.tool_id') != null) {
            var targetToolIdElem = tool.querySelector('.tool_id');
            targetToolId = targetToolIdElem.textContent;
        }
        if (targetToolId == "") {
            console.log("deleteMyTool failed Input tool ID is empty...");
            return;
        }
        const childNodes = myTools.querySelectorAll('.tool-item');
        var firstMatchIndex = -1;
        for (let i = 0; i < childNodes.length; i++) {
            var toolIdElem = childNodes[i].querySelector('.tool_id');
            if (toolIdElem != null) {
                if (toolIdElem.textContent == targetToolId) {
                    firstMatchIndex = i;
                    break;
                }
            }
        }
        if (firstMatchIndex >= 0 && firstMatchIndex < childNodes.length) {
            myTools.removeChild(childNodes[firstMatchIndex]);
        }
    } catch (err) {
        console.log(err)
    }
}

// function for MCP plugin Panel pagination
function pagination(paginationRequiredParams, extraParams) {    
    timeOutId = setTimeout(function(){
    var mergePaginationParams = config.paginationParamsMapper(paginationRequiredParams, extraParams);
    $.get(config.endpoint
        , mergePaginationParams
        , function(data){
            var result = config.mapper(data);
                var itemMap = result.item_map;
                var pageIndexMap = result.page_index_map;

                // Todo: Add Pagination
                renderItemsGroupPagination(itemMap, pageIndexMap, paginationRequiredParams);
        });
    }, 5);
}



function fetchMarketGroupDataFromWeb(config) {
    var agentsGroup = {};
    if (config.loadLocal) {
        var itemMapStr = config.loadLocalData.itemMap;
        var pageIndexMapStr = config.loadLocalData.pageIndexMap;
        var itemMap = new Map();
        if (itemMapStr != null) {
                itemMap = new Map(Object.entries(JSON.parse(itemMapStr)));
        }
        var pageIndexMap = new Map();
        if (pageIndexMapStr != null) {
            pageIndexMap = new Map(Object.entries(JSON.parse(pageIndexMapStr)));
        }
        renderItemsGroup(itemMap, pageIndexMap, "");
    } else {
        timeOutId = setTimeout(function(){
            // Get method
            $.get(config.endpoint
                , config.inputParams
                , function(data){
                    var result = config.mapper(data);
                    var itemMap = result.item_map;
                    var pageIndexMap = result.page_index_map;
                    renderItemsGroup(itemMap, pageIndexMap, "");
            });
        }, 5);
    }
}

function renderItemsList(resultJson, divDisplayToolId) {
    if (resultJson == null) {
        return;
    }
    const toolsData = resultJson["items"];
    if (toolsData == null) {
        return;
    }

    var divDiplayTools = document.getElementById(divDisplayToolId);
    if (divDiplayTools == null) {
        return;
    }
    divDiplayTools.innerHTML = "";
    var toolsNumber = toolsData.length;
    toolsData.forEach(schema => {

        var tool = schemaToTool(schema);
        if (tool != null) {
            tool.addEventListener('click', () => toggleSelectionAddTool(tool, schema));
            // add
            divDiplayTools.appendChild(tool);
        }
    });

}


function timeoutFetch(timeout = 5000) {
    return (url, option = {}) => {
        const controller = new AbortController();
        option.signal = controller.signal;

        const tid = setTimeout(() => {
        console.error(`Fetch timeout: ${url}`);
            controller.abort();
        }, timeout);

            return fetch(url, option).finally(() => {
            clearTimeout(tid);
        });
    };
}

document.addEventListener('DOMContentLoaded', () => {

    // get new sub section
    const templateSelect = document.getElementById('templateSelect');    
    const templateToolsWrapper = document.getElementById('template-tools-wrapper');
    const templateTools = document.getElementById('template-tools');
    const toolSearchResults = document.getElementById('tools-search-results');

    const divTemplateToolsId = "template-tools";
    const divPaginationId = "template-page-selector";
    const apiTimeout = 20000;
    
    // Adjust to Change of Selection
    templateSelect.addEventListener('change', async (event) => {
      const selectedCategory = event.target.value;
      
      try {
        const divLoading = document.createElement('div');
        divLoading.className = "loading";
        divLoading.innerHTML = "<p>Loading...</p>";

        templateTools.innerHTML = "";
        templateTools.appendChild(divLoading);

        var mode = "dict";
        var paginationRequiredParams = {query: selectedCategory, page_id: 0, count_per_page: 6, mode: mode}
        const kvMapsList = Object.entries(paginationRequiredParams).map(
          ([key, value]) => `${key}=${value}`
        );
        var kvMapParam = kvMapsList.join("&")
        console.log(kvMapParam)

        const response = await timeoutFetch(apiTimeout)(`http://www.deepnlp.org/api/mcp_marketplace/v1?${kvMapParam}`)
            .then(response => {
                console.log('enter resolve');
                console.log(response);
            })
            .catch(reason => {
                console.log('enter reject');
                console.log(reason);
        });

        if (!response.ok) {
            console.log("Network response error...")
        }        
        if (divLoading != null) {
            divLoading.remove();
        }

        const resultJson = await response.json();
        console.log(resultJson)   
        if (mode == "list") {

            renderItemsList(resultJson, divTemplateToolsId);

        } else if (mode == "dict") {
            renderItemsGroupPagination(resultJson, paginationRequiredParams, divTemplateToolsId, divPaginationId);

        } else {

        }

      } catch (error) {
          console.log(error)
          //templateTools.innerHTML = `<div class="error">Error: ${error.message}</div>`;
      }
    });


    const templateToolSearchButton = document.getElementById('search-box-button');
    
    templateToolSearchButton.addEventListener('click', async (e) => {

        var displaySearchResultId = "tools-search-results";
        var searchBoxInput = document.getElementById("search-box-input");


        const divLoading = document.createElement('div');
        divLoading.className = "loading";
        divLoading.innerHTML = "<p>Loading...</p>";

        //     const curItemsGrid = document.createElement('div');
        //     curItemsGrid.className = 'grid-container';
        // templateTools.innerHTML = '<div class="loading">Loading...</div>';
        toolSearchResults.innerHTML = "";
        toolSearchResults.appendChild(divLoading);

        if (searchBoxInput != null) {
            var inputText = searchBoxInput.value;

            console.log("SearchBox Input Query:" + inputText);
            // search Tools
            const response = await fetch(`http://www.deepnlp.org/api/mcp_marketplace/v1?mode=list&query=${inputText}&page_id=0&count_per_page=6`, {
              method: 'GET',
              headers: { 'Content-Type': 'application/json' },
              mode: 'cors',       
              credentials: 'omit' 
            });
            if (!response.ok) throw new Error('Network response error');
            
            const resultJson = await response.json();
            
            console.log(resultJson)
            // update Panel
            renderItemsList(resultJson, displaySearchResultId);
        } else {
            console.log("SearchBoxInput Input is null...");
        }
    }
    );

    // Agent Toolbox Functions
    document.querySelectorAll('.add-tool').forEach(button => {
        button.addEventListener('click', function() {
            const toolName = this.previousElementSibling.textContent;
            const myTools = document.querySelector('.my-tools');
            
            const newTool = document.createElement('div');
            newTool.classList.add('tool-item');
            newTool.textContent = toolName;
            
            myTools.appendChild(newTool);
            alert(`Tools Added: ${toolName}`);
        });
    });

    function addDeleteButtonsToTools() {
        document.querySelectorAll('.tool-item').forEach(tool => {
            if (!tool.querySelector('.delete-tool')) {
                const deleteBtn = document.createElement('span');
                deleteBtn.classList.add('delete-tool');
                deleteBtn.addEventListener('click', function(e) {
                    e.stopPropagation(); 
                    tool.remove();
                });
                tool.appendChild(deleteBtn);
            }

            // Add Toggle Event Listener
            // toggleSelection(item, agent)
        });
    }

    function addToggleToTools() {
        document.querySelectorAll('.tool-item').forEach(tool => {
            var schema = toolToSchema(tool);
            if (schema != null) {
                tool.addEventListener('click', () => toggleSelectionAddTool(tool, toolToSchema(tool)));
            }
        });
    }

    function initAgentToolBox() {
        // Todo: init the demo of thoolbox
    }

    initAgentToolBox();
    addDeleteButtonsToTools();
    addToggleToTools();

    document.querySelectorAll('.add-tool').forEach(button => {
        button.addEventListener('click', function() {
            const toolName = this.previousElementSibling.textContent;
            const myTools = document.querySelector('.my-tools');
            
            const newTool = document.createElement('div');
            newTool.classList.add('tool-item');
            newTool.textContent = toolName;
            
            const deleteBtn = document.createElement('span');
            deleteBtn.classList.add('delete-tool');
            deleteBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                newTool.remove();
            });
            newTool.appendChild(deleteBtn);
            
            myTools.appendChild(newTool);
        });
    });

    function openModal() {
        document.querySelector('.json-modal').style.display = 'block';
        document.querySelector('.modal-overlay').style.display = 'block';
    }

    async function exportToolConfig() {
        // get user selected tools, fetch to fill mcp config json and export 
        var selectedToolId = [];
        if (selectedItems != null) {
            selectedItems.forEach((value, key, set) => {
                var valueJsonObj = {}
                try {
                    valueJsonObj = JSON.parse(value);
                } catch (err) {
                    console.log(err);
                }
                var toolId = valueJsonObj.id;
                if (toolId != null) {
                    selectedToolId.push(toolId);
                }
            });
        }
        console.log(selectedToolId);
        var serverIds = selectedToolId.join(",");
        var serverCnt = selectedToolId.length;
        var msg = `Selected ${serverCnt} Tools: ${serverIds} Updated to Your Marketplace Admin, see /mcp to manage them`;
        
        // call api to save to local mcp_config.json
        var method = "GET";
        var body = null;
        var url = `/api/marketplace/config?server_ids=${encodeURIComponent(serverIds)}`;
        var resultJson = {};
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
            resultJson = await response.json();
        } catch (error) {
            console.error(`API call to ${url} failed:`, error);
            // alert(`Error: ${error.message}`); // Simple error display
        }
        // notify tools
        alert(msg);
        
        // alert(resultJson);
        // enlarge
        var configElem = document.getElementById('json-content')
        if (configElem != null) {
            configElem.textContent = JSON.stringify(resultJson, null, 2);
        }
        // trigger enlarge
        openModal();
    }
    
    const exportConfigButton = document.getElementById('tool-export-button');
    exportConfigButton.addEventListener('click', async (e) => {
        exportToolConfig();
        }
    );

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

});
