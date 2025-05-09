const config_deepnlp = {
    endpoint: "http://www.deepnlp.org/api/mcp_marketplace/v1",
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


function renderItemsGroupPagination(agentsMap, agentsIndexMap, paginationRequiredParams) {
    const agentButton = document.querySelector('.agent-button');
    const panelSectionContainer = document.querySelector('.panel_section_container');
    if (agentsMap == null) {
        return;
    }
    if (agentsIndexMap == null) {
        agentsIndexMap = new Map();
    }
    // define the section and pageId that user wants to refresh
    var sectionId = (paginationRequiredParams["query"] != null)?paginationRequiredParams["query"]:"";
    var pageId = (paginationRequiredParams["page_id"] != null)?paginationRequiredParams["page_id"]:"";
    if (sectionId == null || sectionId == "") {
        return;
    }
    var panelSectionElem = document.getElementById(sectionId);
    if (panelSectionElem == null) {
        panelSectionElem = document.createElement('div');
        panelSectionElem.id = sectionId;
        panelSectionElem.class = "panel_section";
        panelSectionContainer.append(panelSectionElem);
    }
    var itemsGrid = panelSectionElem.querySelector('.grid-container');
    if (itemsGrid != null) {
        itemsGrid.innerHTML = "";
    }
    var itemData = agentsMap.get(sectionId);
    if (itemData == null) {
        return;
    }
    itemData.forEach(agent => {
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
        item.className = 'grid-item';
        item.innerHTML = thumbnailHtml + summaryHtml;
        item.addEventListener('click', () => toggleSelection(item, agent));
        itemsGrid.appendChild(item);
    });
    // update page selector            
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

function renderItemsGroup(agentsMap, agentsIndexMap) {
    if (agentsMap == null) {
        return;
    }
    if (agentsIndexMap == null) {
        agentsIndexMap = new Map();
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
                    item.className = 'grid-item';
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

document.addEventListener('DOMContentLoaded', () => {
    const agentButton = document.querySelector('.agent-button');
    const panel = document.querySelector('.panel');
    const panelSection = document.querySelector('.panel_section');    
    const itemsGrid = document.getElementById('items-grid');
    
    if (agentButton != null) {
        agentButton.addEventListener('click', (e) => {
            e.stopPropagation();
            panel.classList.toggle('hidden');
            if (selectedItems.size > 0) {
                if (agentButton.classList.contains('agent-button-close')) {
                    agentButton.classList.remove('agent-button-close');
                }
                agentButton.classList.add('agent-button-chosen');
            } else {
                if (agentButton.classList.contains('agent-button-chosen')) {
                    agentButton.classList.remove('agent-button-chosen');
                }
                agentButton.classList.add('agent-button-close');
            }
            if (!panel.classList.contains('hidden') && itemsGrid.innerHTML == "") {
                fetchMarketGroupDataFromWeb(config) 
            }

        });
    }

    document.addEventListener('click', (e) => {

        var panelElem = document.getElementById('panel');
        if (!panelElem.contains(e.target) && !agentButton.contains(e.target)) {
            panelElem.classList.add('hidden');
        }
        // set button color
        if (selectedItems.size > 0) {
            if (agentButton.classList.contains('agent-button-close')) {
                agentButton.classList.remove('agent-button-close');
            }
            agentButton.classList.add('agent-button-chosen');
        }        
    });

});
