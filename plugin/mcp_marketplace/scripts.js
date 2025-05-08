const config_deepnlp = {
      endpoint: "http://www.deepnlp.org/api/mcp_marketplace/v1",
      inputParams: {"field": "MCP SERVER", "page_id": 0, "page_size": 20},
      mapper: function(data) {
            var itemMap = new Map(Object.entries(data.item_map));            
            var indexMap = new Map(Object.entries(data.page_id_map));
            return {"item_map": itemMap, "page_index_map": indexMap};
      },
      paginationParams: {"field": "MCP SERVER", "subfield": "", "section": "MCP SERVER", "page_size": 20},
      loadLocal: true,
      loadLocalData: {
        itemMap: '{"MCP SERVER":[{"content_name":"Tool 1","description":"Sales and Marketing","field":"MCP SERVER","subfield":"MAP","mcp config":{}},{"content_name":"Tool 2","description":"MAP","field":"MCP SERVER","subfield":"Payment","mcp config":{}},{"content_name":"Tool 3","description":"PAYMENT","field":"MCP SERVER","subfield":"Payment","mcp config":{}},{"content_name":"Tool 4","description":"DATABASE","field":"MCP SERVER","subfield":"DATABASE","mcp config":{}}],"MAP":[{"content_name":"Map 1","description":"Map Tool 1","field":"MCP SERVER","subfield":"MAP","mcp config":{}},{"content_name":"Map 2","description":"Map Tool 2","field":"MCP SERVER","subfield":"MAP","mcp config":{}}],"FETCH":[{"content_name":"Fetch 1","description":"Fetch 1","field":"MCP SERVER","subfield":"FETCH","mcp config":{}},{"content_name":"Fetch 2","description":"Fetch 2","field":"MCP SERVER","subfield":"FETCH","mcp config":{}}],"Browser Use":[{"content_name":"Browser Use 1","description":"Browser Use 1","field":"MCP SERVER","subfield":"Browser Use","mcp config":{}},{"content_name":"Browser Use 2","description":"Browser Use 2","field":"MCP SERVER","subfield":"Browser Use","mcp config":{}}]}',
        pageIndexMap : '{"MCP SERVER": [1, 2], "Map": [1, 2], "FETCH": [1,2], "Browser Use": [1,2]}'
      },      
      timeout: 5000
};

const config_pulsemcp = {
      endpoint: "https://api.pulsemcp.com/v0beta/servers",
      inputParams: {"query": "image", "count_per_page": 10},
      mapper: function(data) {
        var servers = data.servers;
        var next = data.next;
        var total_cnt = data.total_cnt;

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
        // key1: category, value: list of json
        var itemMap = new Map(Object.entries({"MCP SERVER": itemListMapped}));
        var indexMap = new Map();
        return {item_map: itemMap, page_index_map: indexMap};
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

// set the default config
const config = getConfigByName("deepnlp");
// const config = getConfigByName("pulsemcp");

document.addEventListener('DOMContentLoaded', () => {
    const agentButton = document.querySelector('.agent-button');
    const panel = document.querySelector('.panel');
    const panelSection = document.querySelector('.panel_section');    
    const itemsGrid = document.getElementById('items-grid');
    let selectedItems = new Set();

    // Toggle panel visibility
    if (agentButton != null) {
        agentButton.addEventListener('click', (e) => {
            e.stopPropagation();
            panel.classList.toggle('hidden');
            // update button css
            if (selectedItems.size > 0) {
                // agentButton.classList.remove('agent-button-close');
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
            // update panel data
            if (!panel.classList.contains('hidden') && itemsGrid.innerHTML == "") {
                fetchMarketGroupDataFromWeb(config) 
            }

        });
    }

    // Close panel when clicking outside
    document.addEventListener('click', (e) => {
        if (!panel.contains(e.target) && !agentButton.contains(e.target)) {
            panel.classList.add('hidden');
        }
        // set button color
        if (selectedItems.size > 0) {
            if (agentButton.classList.contains('agent-button-close')) {
                agentButton.classList.remove('agent-button-close');
            }
            agentButton.classList.add('agent-button-chosen');
        }        
    });

    // function for MCP plugin pagination
    function pagination(paginationParams) {    
            timeOutId = setTimeout(function(){
                        // et method
                        $.get(config.endpoint
                            , paginationParams
                            , function(data){
                                var result = config.mapper(data);
                                var itemMap = result.item_map;
                                var pageIndexMap = result.page_index_map;
                                renderItemsGroup(itemMap, pageIndexMap);
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
            renderItemsGroup(itemMap, pageIndexMap);
        } else {
            timeOutId = setTimeout(function(){
                // et method
                $.get(config.endpoint
                    , config.inputParams
                    , function(data){
                        var result = config.mapper(data);
                        var itemMap = result.item_map;
                        var pageIndexMap = result.page_index_map;
                        renderItemsGroup(itemMap, pageIndexMap);
                });
            }, 5);
        }
    }

    function truncateString(str, length) {
        if (str == null) {
            return "";
        }
        return str.length > length ? str.substring(0, length) + '...' : str;
    }
    
    /**
    * agent.content_name
    * agent.description
    * agent.thumbnail_picture
    * agent.field
    * agent.subfield
    * agentsIndexMap, key: groupname, value: list of index for pagination, e.g. [1,2,3,..., 10]
    */
    function renderItemsGroup(agentsMap, agentsIndexMap) {
        if (agentsMap == null) {
            itemsGrid.innerHTML = 'loading...';
            return;
        }
        itemsGrid.innerHTML = '';

        if (agentsIndexMap == null) {
            agentsIndexMap = new Map();
        }

        agentsMap.forEach((value, key) => {
                var agentGroup = key;
                var agents = value;

                // section_title
                var groupHtml = document.createElement('div');
                groupHtml.innerHTML = `<h3>${agentGroup}</h3>`;
                panelSection.appendChild(groupHtml);

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
                panelSection.appendChild(curItemsGrid);
                // pagination
                var pageSelectorHtml = document.createElement('div');
                var pageIdDisplayList = agentsIndexMap.get(key);
                var pageHtml = "";
                var paginationParams = config.paginationParams;

                if (pageIdDisplayList != null) {
                    for (var pageId =0 ; pageId < pageIdDisplayList.length; pageId++) {

                        // assemble pagination param
                        paginationParams.page_id = pageId;
                        paginationParams.group = key;

                        var pageIdDisplay = pageIdDisplayList[pageId];
                        var curPageHtml = "";
                        if (pageId == 0) {
                            curPageHtml = "<div class=\"page_id_wrapper\"><a class=\"page_id_a page_id_a_active\" onclick='pagination(" + JSON.stringify(paginationParams) + ")'>" + pageIdDisplay + "</a></div>";
                        } else {
                            curPageHtml = "<div class=\"page_id_wrapper\"><a class=\"page_id_a\" onclick='pagination(" + JSON.stringify(paginationParams) +")'>" + pageIdDisplay + "</a></div>";
                        }
                        pageHtml += curPageHtml;
                    }
                    pageSelectorHtml.innerHTML = `<div class="page_selector">${pageHtml}</div>`;
                    panelSection.appendChild(pageSelectorHtml);
                }
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

        // Send selection to parent window
        window.parent.postMessage({
            type: 'agentSelection',
            selected: Array.from(selectedItems).map(c => JSON.parse(c))
        }, '*');

        // update global variable
        window.agent_selected_items = selectedItems;
    }
});
