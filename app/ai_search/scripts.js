// Function to add a message to the chatbox
function addMessage(sender, text) {
  const chatbox = document.getElementById('chatbox');
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}-message`;
  msgDiv.textContent = text;
  chatbox.appendChild(msgDiv);
  chatbox.scrollTop = chatbox.scrollHeight;
}

function getSelectAgent() {
  var agents_data = window.agent_selected_items;
  if (agents_data == null) {
    return [];
  }
  var select_agent_data = Array.from(agents_data).map(c => JSON.parse(c));
  return select_agent_data;
}

function getSelectedAgentInfo(select_agent_data) {

    var user_defined_tools = [];
    for (var i = 0; i < select_agent_data.length; i++) {
      var agent = select_agent_data[i];
      
      var contentName = agent.content_name;
      // var abstract = truncateString(agent.description, 10);
      var thumbnailURL = agent.thumbnail_picture;
      var field = agent.field;
      var subfield = agent.subfield;
      user_defined_tools.push(contentName);
    }

    var result = user_defined_tools.join(", \n");
    var response_message = "";
    if (user_defined_tools.length > 0) {
      response_message = '[System] Selected MCP Tools From Endpoint http://www.deepnlp.org/store/ai-agent/mcp-server: ' + result
    }
    return response_message;
}


// Handle submit (circular) button click
document.getElementById('submit-btn').addEventListener('click', () => {
  const input = document.getElementById('search-input');
  const message = input.value.trim();


  var selectedAgentData = getSelectAgent();
  if (!message && selectedAgentData.length == 0) {
    return
  };

  // hide introduction
  document.getElementById('introduction').style.display='none';

  // Add user message
  addMessage('user', message);
  input.value = '';

  // Simulate AI response
  response_message = getSelectedAgentInfo(selectedAgentData);
  setTimeout(() => {
    //parse result from agent marketplace button
    if (response_message == "") {
        response_message = "response";
    }
    addMessage('bot', response_message);
  }, 500);
});

// Optional: Attach handlers to other buttons if needed
// e.g., document.getElementById('search-btn').addEventListener(...);
