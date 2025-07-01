document.addEventListener('DOMContentLoaded', function() {
    
    // Element/Plugin
    const sendBtn = document.getElementById('sendBtn');
    const chatbox = document.getElementById('chatbox');
    const searchInput = document.getElementById('searchInput');    
    const sidebar = document.querySelector('.sidebar');
    const collapseBtn = document.querySelector('.collapse-btn');
    const systemMessages = document.getElementById('system-messages');
    const newChatBtn = document.getElementById('new-chat');
    const aiAgentMarketplaceSidebar = document.getElementById('all-apps');
    const mcpMarketplaceSidebar = document.getElementById('mcp-marketplace-sidebar');
    const historyItemSideBar = document.querySelectorAll('.history-item');
    const settingBtn = document.querySelector('.setting-btn');

    // processing received message
    const messageStates = new Map();
    const TYPEWRITER_SPEED = 5000;
    const MARKDOWN_RENDER_DELAY = 200;

    // keep track of chat history
    let chatHistory = [];

    collapseBtn.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
    });

    searchInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // 
    const buttonActionClassname = "agent-button-base";

    const messageTypeIncoming = "bot-message";
    const messageTypeOutgoing = "user-message";

    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = (crypto.getRandomValues(new Uint8Array(1))[0] % 16) | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    function appendMessage(id, role, message_type, section, content, template) {
        msgDiv = document.getElementById(id);
        if (msgDiv == null) {
            msgDiv = document.createElement('div');
            msgDiv.id = id;
            msgDiv.className = `message ${role} ${message_type}`;
            chatbox.appendChild(msgDiv);
        }
        if (role === 'assistant' && content.match(/^<img src=/)) {
            // If the content is an image tag, render as HTML
            msgDiv.innerHTML = content;
        } else {
            msgDiv.textContent = content;
        }
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    function appendMessageHtml(id, role, message_type, section, content, template) {
        try {
            msgDiv = document.getElementById(id);
            if (msgDiv == null) {
                // wrapper
                msgDiv = createDivByTemplate(template);
                msgDiv.id = id;
                msgDiv.className = `message ${role} ${message_type}`;
                updateMessageDivByContent(template, msgDiv, section, content);
                chatbox.appendChild(msgDiv);
            }
            updateMessageDivByContent(template, msgDiv, section, content);
            chatbox.scrollTop = chatbox.scrollHeight;
        } catch (err) {
            console.log(err)
        } finally {
            //
        }
    }

    /**
    * Add Click Event to Rendered Element in Html
    */
    function addEventListenerDynamicButton(buttonElement, actionName) {
        if (buttonElement == null) {
            return;
        }
        buttonElement.addEventListener('click', () => {
                clickButtonAction(actionName); 
            }
        );
        buttonElement.setAttribute("set_on_click", true);
        console.log(buttonElement)
    }

    function createDivByTemplate(template) {

        if (template == "reason_html") {
            return createNewReasonHtmlDiv()
        
        } else if (template == "reason_text") {
            
            return createNewReasonTextDiv();
        
        } else {
            return createNewReasonTextDiv();

        }

    }

    /**
    * iframe has isolated html and js action are not good
    */
    function updateMessageDivByContent(template, div, section, content) {
        if (template == "reason_html") {
            var divList = div.getElementsByClassName(section);
            if (divList != null) {
                // update the first match div
                for (var i = 0; i < divList.length; i++) {
                    // find iframe that classlist match section
                    if (divList[i].classList.contains(section)) {
                            divList[i].innerHTML = content;
                    }
                }
            }

        } else if (template == "reason_text") {
            // section: think, tools, answer
            var divList = div.getElementsByClassName(section);
            if (divList != null) {
                // update the first match div
                for (var i = 0; i < divList.length; i++) {
                    // find iframe that classlist match section
                    if (divList[i].classList.contains(section)) {
                        divList[i].textContent = content;
                    }
                }
            } 
        } else {

        }

    }

    /**
    *
    */
    function createNewReasonHtmlDiv() {

        msgDiv = document.createElement('div');

        divSystemMsg = document.createElement('div');
        divSystemMsg.className = "system_msg";

        divReason = document.createElement('div');
        divReason.className = "think";

        divTool = document.createElement('div');
        divTool.className = "tool";

        divHtml = document.createElement('div');
        divHtml.className = "answer";

        divContext = document.createElement('div');
        divContext.className = "context";
        divContext.style.display = "none";
        // divContext.style.visibility = "hidden";

        msgDiv.appendChild(divSystemMsg);
        msgDiv.appendChild(divReason);
        msgDiv.appendChild(divTool);
        msgDiv.appendChild(divHtml);
        msgDiv.appendChild(divContext);

        return msgDiv;
    }

    /**
    * 
    */
    function createNewReasonTextDiv() {

        msgDiv = document.createElement('div');

        divSystemMsg = document.createElement('div');
        divSystemMsg.className = "system_msg";

        divReason = document.createElement('div');
        divReason.className = "think";

        divTool = document.createElement('div');
        divTool.className = "tool";

        divText = document.createElement('div');
        divText.className = "answer";

        divContext = document.createElement('div');
        divContext.className = "context";
        // divContext.style.hidden = "hidden";
        // divContext.style.visibility = "hidden";
        divContext.style.display = "none";

        // divToolResult = document.createElement('div');
        // divToolResult.className = "tool";
        msgDiv.appendChild(divSystemMsg);
        msgDiv.appendChild(divReason);
        msgDiv.appendChild(divTool);
        msgDiv.appendChild(divText);
        msgDiv.appendChild(divContext);
        // msgDiv.appendChild(divToolResult);    
        return msgDiv;    
    }

    function appendSystemMessage(msg) {
        systemMessages.textContent = msg;
    }

    /**
    * messagesHistory: list
    */
    function getModelSelected() {

        try {
            var button = document.getElementById("modelBtn");
            var modelDataValue = button.getAttribute('data-value');
            return modelDataValue;
        } catch (err) {
            console.log(err);
            return "";
        }
    }

    async function waitForAllMessages(messageIds) {
        return new Promise((resolve) => {
            const checkAllCompleted = () => {
                const allDone = messageIds.every(id => {
                    const state = messageStates.get(id);
                    return state && state.isFinished;
                });
                
                if (allDone) resolve();
                else setTimeout(checkAllCompleted, 100);
            };
            checkAllCompleted();
        });
    }

    async function processStream(reader, decoder) {
        let done = false;
        let buffer = "";
        var messageIdTotal = [];

        while (!done) {
            const { value, done: doneReading } = await reader.read();
            done = doneReading;
            
            if (value) {
                const chunk = decoder.decode(value, { stream: true });
                buffer += chunk;
                // Router According to Chunk
                var curMessageIdList = processBuffer(buffer);
                messageIdTotal = messageIdTotal.concat(curMessageIdList);
                buffer = "";
            }
        }
        
        if (buffer) {
            var curMessageIdList = processBuffer(buffer);
            messageIdTotal = messageIdTotal.concat(curMessageIdList);
        };
        messageIdTotal = [...new Set(messageIdTotal)]; 

        // append chat history
        appendChatHistory(messageIdTotal);

        return messageIdTotal;

    }

    function appendChatHistory(messageIdList) {
        messageIdList.forEach(messageId => {
                var messageState = messageStates.get(messageId);
                if (messageState != null) {
                    var contentMap = messageState.sectionContentMap;
                    var thinkVar = contentMap.get("think").display;
                    var toolVar = contentMap.get("tool").display;
                    var answerVar = contentMap.get("answer").display;
                    var contextVar = contentMap.get("context").display;
                    var msgSummary = [thinkVar, answerVar, toolVar].join("|");
                    var allEmpty = ([thinkVar, toolVar, answerVar, contextVar].join("") == "")
                    if (!allEmpty) {
                        chatHistory.push({role: 'assistant', content: msgSummary, context: contextVar});
                    }
                }
        });
    }

    function processBuffer(buffer) {

        var messageIdList = [];

        buffer.split('\n').forEach(line => {
            if (!line.trim()) return;
            try {
                const data = JSON.parse(line);
                const messageId = data.message_id || `msg-${Date.now()}`;
                
                if (!messageIdList.includes(messageId)) {
                    messageIdList.push(messageId);
                }

                // system, assistant
                const dataType = data.type;
                // image, video, html, text
                const dataFormat = data?.format ?? "";
                // system_msg, think, tool, answer, context
                const dataSection = data?.section ?? "";
                const dataContent = data?.content ?? "";
                // template: reason_html: reason+tool+answer, reason_text: reason + answer, others
                const dataTemplate = data?.template ?? "reason_html";

                if (!messageStates.has(messageId)) {
                    messageStates.set(messageId, {
                        messageId,
                        displayedContent: '',
                        pendingContent: '',
                        isFinished: false,
                        sectionContentMap: new Map([
                            ["system_msg", {pending: "", display:""}],
                            ["think", {pending: "", display:""}],
                            ["tool", {pending: "", display:""}],
                            ["answer", {pending: "", display:""}],
                            ["context", {pending: "", display:""}]
                        ]),
                        template: dataTemplate,
                        timer: null
                    });
                }

                // update message States
                const state = messageStates.get(messageId);
                var curSectionContent = state.sectionContentMap.get(dataSection);
                if (curSectionContent != null) {
                    curSectionContent.pending += dataContent;
                }

                updateMessageDOM(state);

            } catch (err) {
                console.error('process error:', err);
                appendSystemMessage('Failed to process Error...');
            }
        });

        return messageIdList;
    }

    /**
    * display text in a paragraph with \r\n break lines
    */
    function formatTextWithParagraphs(text, div_class) {
        if (text == null || text.trim() == "") {
            return '';
        }
        try {
            var lineList = text.split(/\r\n|\r|\n/);
            var wrappedParagraphDivList = "";
            if (lineList != null) {
                wrappedParagraphDivList = lineList.map(line => {
                    const hasHtmlTags = /<\/?[a-zA-Z][\s\S]*?>/i.test(line);
                    if (!hasHtmlTags) {
                        return line.trim() ? `<p>${line}</p>` : ''
                    } else {
                        return line.trim() ? `${line}` : ''
                    }
                }).join('');
            }
            var wraperContent = `<div class="${div_class}">` + wrappedParagraphDivList + '</div>';
            return wraperContent;
        } catch (err) {
            console.log(err)
            return text;
        }
    }

    /**
    * display Content
    */
    function updateMessageDOM(state) {

        // update message unfinished
        var existingPendingContent = "";
        if (state.sectionContentMap != null) {
            state.sectionContentMap.forEach(function(value, key) {
                existingPendingContent += value.pending.trim();
            })
        }
        if (existingPendingContent.trim().length === 0) {
            return;
        }        

        const messageId = state.messageId;
        const template = state.template;
        const messageRole = "assistant";

        state.sectionContentMap.forEach(function(value, key) {
            var curSection = key;
            var curPendingContent = value.pending;
            var curDisplayContent = value.display;
            if (curPendingContent == "") {
                return;
            }
            var curMessageDiv = document.getElementById(messageId);
            if (curMessageDiv == null) {
                curMessageDiv = createDivByTemplate(template);
                curMessageDiv.id = messageId;
                curMessageDiv.className = `message ${messageRole} ${messageTypeIncoming}`;
                chatbox.appendChild(curMessageDiv);
                chatbox.scrollTop = chatbox.scrollHeight;
            }
            var curSectionElement  = curMessageDiv.querySelector(`.${curSection}`)
            // append pendding to display and clear pending
            if (curSection == "system_msg") {
                // update State
                value.display = curPendingContent;
                value.pending = "";
                curSectionElement.innerHTML = formatTextWithParagraphs(value.display, "div_msg_paragraph");

            } else if (curSection == "think" || curSection == "tool" || curSection == "context") {

                value.display += curPendingContent;
                value.pending = "";
                curSectionElement.innerHTML = formatTextWithParagraphs(value.display, "div_msg_paragraph");

            } else if (curSection == "answer") {
                // markdown and html
                value.display += curPendingContent;
                value.pending = "";
                try {
                    setTimeout(() => {
                        curSectionElement.innerHTML = marked.parse(value.display);
                    }, MARKDOWN_RENDER_DELAY);
                } catch (err) {
                    console.log(err);
                    curSectionElement.innerHTML = formatTextWithParagraphs(value.display, "div_msg_paragraph");
                }

            } else if (curSection == "context") {

                value.display += curPendingContent;
                value.pending = "";

                curSectionElement.innerHTML = formatTextWithParagraphs(value.display, "div_msg_paragraph");

            } else {
                curDisplayContent += curPendingContent;

                value.pending = "";
                value.display = curDisplayContent;

                curSectionElement.innerHTML = formatTextWithParagraphs(value.display, "div_msg_paragraph");

            }
        })

    }


    /**
    * Main function to process API request and update Message Card
    */
    async function callChatService(chatHistory, kwargs) {
        // Stream response from backend
        try {
            const response = await fetch('http://127.0.0.1:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: chatHistory, kwargs: kwargs})
            });
            if (!response.body) throw new Error('No response body');
            const reader = response.body.getReader();
            // let assistantMsg = '';
            hideThinking();

            let responseMap = new Map()

            let decoder = new TextDecoder();

            var messageIdTotal = await processStream(reader, decoder);

        } catch (err) {
            appendSystemMessage('Error: ' + err.message);
        }
    } 


    async function callChatServiceVBeta(chatHistory, kwargs) {
        // Stream response from backend
        try {
            const response = await fetch('http://127.0.0.1:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: chatHistory, kwargs: kwargs})
            });
            if (!response.body) throw new Error('No response body');
            const reader = response.body.getReader();
            // let assistantMsg = '';

            // Remoeve Thinking Status
            let responseMap = new Map()

            let decoder = new TextDecoder();
            let done = false;
            while (!done) {
                const { value, done: doneReading } = await reader.read();
                done = doneReading;
                if (value) {
                    const chunk = decoder.decode(value, {stream: true});
                    // Each chunk is a JSON line
                    chunk.split('\n').forEach(line => {
                        if (!line.trim()) return;
                        try {
                            const data = JSON.parse(line);
                            // group by single message
                            var messageId = data.message_id;
                            
                            if (data.type === 'system') {
                                appendSystemMessage(data.message);
                            } else if (data.type === 'assistant') {

                                if (data.format === 'image') {
                                    appendMessage('', 'assistant', 'incoming', 'response', `<img class='chat-image' src='${data.content}' alt='Image' />`);
                                } else if (data.format === 'video') {
                                    appendMessage('', 'assistant', 'incoming', 'response', `<img class='chat-image' src='${data.content}' alt='Image' />`);

                                } else if (data.format === 'html') {

                                    section = data.section;
                                    var newContent = data.content;

                                    var curContent = "";
                                    if (responseMap.has(section)) {
                                        curContent = responseMap.get(section);
                                    } else {
                                        curContent = "";
                                    }


                                    // check if to stop thinking
                                    if (section != "think" && newContent != "") {
                                        hideThinking();
                                    }

                                    if (section == "system_msg") {
                                        curContent = data.content;
                                    } else if (section == "think" || section == "answer" || section == "tool" || section == "context") {
                                        curContent += data.content;
                                    } else {
                                    }
                                    if (curContent.trim() != "") {
                                        // msg overried
                                        appendMessageHtml(messageId, 'assistant', messageTypeIncoming, section, curContent, 'reason_html');
                                        // add action
                                        var divMessage = document.getElementById(messageId);
                                        if (divMessage != null) {
                                            var buttonList = divMessage.getElementsByClassName(buttonActionClassname);
                                            for (var i = 0; i < buttonList.length; i++) {
                                                var buttonElem = buttonList[i];
                                                var actionName = buttonElem.value;
                                                if (buttonElem.getAttribute("set_on_click") == null || !buttonElem.getAttribute("set_on_click")) {
                                                    addEventListenerDynamicButton(buttonElem, actionName);
                                                }
                                            }
                                        }
                                        // update map
                                        responseMap.set(section, curContent);
                                    }                                

                                } else if (data.format === 'text') {
                                    // text ()
                                    // separate assistant message different section
                                    section = data.section;
                                    var newContent = data.content;
                                    if (section != "think" && newContent != "") {
                                        hideThinking();
                                    }

                                    if (section == "system_msg") {
                                        curContent = data.content;
                                    } else if (section == "think" || section == "answer" || section == "tool" || section == "context") {
                                        curContent += data.content;
                                    } else {
                                    }
                                    if (curContent.trim() != "") {
                                        // msg overried
                                        appendMessageHtml(messageId, 'assistant', messageTypeIncoming, section, curContent, 'reason_text'); 
                                        // update map
                                        responseMap.set(section, curContent);                                    
                                    }
                                } else {

                                }
                            }
                        } catch (err) {
                            appendSystemMessage('Error parsing response');
                        }
                    });
                }
            }
            // chatHistory.push({role: 'assistant', content: assistantMsg});

            // update chat history
            var assistantThinkMsg = (responseMap.get("think") == null)?"": responseMap.get("think");
            var assistantAnswerMsg = (responseMap.get("answer") == null)?"": responseMap.get("answer");
            var assistantToolMsg = (responseMap.get("tool") == null)?"": responseMap.get("tool");
            var assistantContextMsg = (responseMap.get("context") == null)?"": responseMap.get("context");
            var msgSummary = [assistantThinkMsg, assistantAnswerMsg, assistantToolMsg].join()
            
            // pass context variable back to server side
            chatHistory.push({role: 'assistant', content: msgSummary, context: assistantContextMsg});

        } catch (err) {
            appendSystemMessage('Error: ' + err.message);
        }
    } 


    // model selection
    const modelActionButton = document.querySelector('.action-btn');
    const modelDropDownContent = document.querySelector('.dropdown-content');
    
    document.addEventListener('click', (e) => {

        const isModelButtonClick = modelActionButton.contains(e.target);
        if (isModelButtonClick) {
            modelDropDownContent.classList.toggle('dropdown-content-show');
        } else {
            modelDropDownContent.classList.remove('dropdown-content-show');
        }
    });

    // AI Agent Marketplace End
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    const modelBtn = document.getElementById('modelBtn');
    
    dropdownItems.forEach(item => {
        item.addEventListener('click', function() {
            const modelName = this.querySelector('strong').textContent;
            const dataValue = this.getAttribute('data-value');
            modelBtn.querySelector('span').textContent = modelName;
            modelBtn.setAttribute("data-value", dataValue);
        });
    });

    const thinkBtn = document.getElementById('thinkBtn');
    if (thinkBtn != null) {
        thinkBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            console.log('Think: ' + (this.classList.contains('active') ? 'Open' : 'Close'));
        });
    }

    const webSearchBtn = document.getElementById('webSearchBtn');
    if (webSearchBtn != null) {
        webSearchBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            console.log('Web Search: ' + (this.classList.contains('active') ? 'Open' : 'Close'));
        });
    }

    const uploadBtn = document.getElementById('imageUploadBtn')
    if (uploadBtn != null) {
        uploadBtn.addEventListener('click', function() {
            document.getElementById('imageFile').click();
        });
    }


    const imageFileBtn = document.getElementById('imageFile')
    if (imageFileBtn != null) {
        imageFileBtn.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                uploadFile(e.target.files[0], '/api/uploadimages');
            }
        });
    }

    const fileUploadBtn = document.getElementById('fileUploadBtn')
    if (fileUploadBtn != null) {
        fileUploadBtn.addEventListener('click', function() {
            document.getElementById('documentFile').click();
        });
    }

    const documentFile = document.getElementById('documentFile');
    if (documentFile != null) {
        documentFile.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                uploadFile(e.target.files[0], '/api/uploadfiles');
            }
        });
    }

    function uploadFile(file, url) {
        console.log(`Uploading File: ${file.name} to ${url}`);
        const formData = new FormData();
        formData.append('file', file);
        
        const uploadStatus = document.createElement('div');
        uploadStatus.classList.add('upload-status');
        uploadStatus.innerHTML = `uploading: ${file.name} <div class="upload-progress"></div>`;
        document.querySelector('.input-container').prepend(uploadStatus);
        
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Upload Successfully:', data);
            uploadStatus.innerHTML = `✅ Upload Successfully: ${file.name}`;
            setTimeout(() => uploadStatus.remove(), 3000);
        })
        .catch(error => {
            console.error('Upload Failed:', error);
            uploadStatus.innerHTML = `❌ Upload Failed: ${file.name}`;
            setTimeout(() => uploadStatus.remove(), 5000);
        });
    }

    const templateBtn = document.getElementById('templateBtn');
    const templatePanel = document.getElementById('templatePanel');
    const closeTemplatePanel = templatePanel.querySelector('.close-panel');
    
    if (templateBtn != null) {
        templateBtn.addEventListener('click', function() {
            templatePanel.style.display = 'block';
        });
    }

    if (closeTemplatePanel != null) {
        closeTemplatePanel.addEventListener('click', function() {
            templatePanel.style.display = 'none';
        });
    }

    const memoryBtn = document.getElementById('memoryBtn');
    const memoryPanel = document.getElementById('memoryPanel');
    const closeMemoryPanel = memoryPanel.querySelector('.close-panel');
    
    if (memoryBtn != null) {
        memoryBtn.addEventListener('click', function() {
            memoryPanel.style.display = 'block';
        });
    }

    if (closeMemoryPanel) {
        closeMemoryPanel.addEventListener('click', function() {
            memoryPanel.style.display = 'none';
        });
    }

    if (sendBtn != null) {
        sendBtn.addEventListener('click', sendMessage);
    }

    if (searchInput != null) {
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    function sendMessage() {
        const inputContent = searchInput.value.trim();
        if (inputContent) {

            appendMessage(generateUUID(), 'user', 'outgoing', "", inputContent);
            chatHistory.push({role: 'user', content: inputContent});
            searchInput.value = '';
            appendSystemMessage('');

            showThinking();

            // Get Model Selection
            modelSelection = getModelSelected()
            kwargs = {"model_selection": modelSelection}
            callChatService(chatHistory, kwargs);

        }
    }

    function addMessageToChatbox(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
        
        if (sender === 'bot') {
            let formattedMessage = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            formattedMessage = formattedMessage.replace(/\*(.*?)\*/g, '<em>$1</em>');
            formattedMessage = formattedMessage.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
            
            messageDiv.innerHTML = formattedMessage;
        } else {
            messageDiv.textContent = message;
        }
        
        chatbox.appendChild(messageDiv);
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    function showThinking() {
        const thinkingDiv = document.createElement('div');
        thinkingDiv.classList.add('div_thinking_status');
        thinkingDiv.innerHTML = '<p>Thinking</p><span class="dot-flashing"></span>';
        
        chatbox.appendChild(thinkingDiv);
        chatbox.scrollTop = chatbox.scrollHeight;
    }


    // remove div_thinking_status
    function hideThinking() {
        var removeThink = true;
        if (removeThink) {
            var div_thinking_section = document.querySelector('.div_thinking_status');
            if (div_thinking_section != null) {
                div_thinking_section.remove();
            }
        }
    }

    function generateResponse(message) {
        const responses = [
            "I think your question is about" + message + ". According to my latest knowledge, ",
            "About" + message + ", I can think of a few aspects...",
            "This question is very interesting " + message + "mechanism..."
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }

    if (newChatBtn != null) {
        newChatBtn.addEventListener('click', function() {
            chatbox.innerHTML = '';
            searchInput.value = '';
            alert('New Chat Created');
        });

    }

    if (aiAgentMarketplaceSidebar != null) {
        aiAgentMarketplaceSidebar.addEventListener('click', function() {
            alert('Opening AI Agent Marketplace...');
        });
    }

    if (mcpMarketplaceSidebar != null ) {
        mcpMarketplaceSidebar.addEventListener('click', function() {
            window.open("/mcp", "_blank");
        });
    }

    if (historyItemSideBar != null) {
        historyItemSideBar.forEach(item => {
            item.addEventListener('click', function() {
                const chatTitle = this.textContent;
                chatbox.innerHTML = `<div class="message bot-message">Loading Chat History: ${chatTitle}...</div>`;
                setTimeout(() => {
                    chatbox.innerHTML = '';
                    addMessageToChatbox(`This is "${chatTitle}" history`, 'bot');
                    addMessageToChatbox('Question...', 'user');
                    addMessageToChatbox('AI Answer...', 'bot');
                }, 1000);
            });
        });
    }

    if (settingBtn != null) {
        document.querySelector('.setting-btn').addEventListener('click', function() {
            chatbox.innerHTML = '';
            addMessageToChatbox('Setting', 'bot');
            addMessageToChatbox('User Name: Logged In User', 'bot');
            addMessageToChatbox('Email: user@example.com', 'bot');
            addMessageToChatbox('You can update your personal information...', 'bot');
        });
    }


    // Non-Dom Loaded Function Starts
    // Dpn't need to tie to an element
    function clickButtonAction(action_name) {

            var message = '<action>' + action_name + '</action>'

            appendMessage(generateUUID(), 'user', 'outgoing', "", action_name);
            chatHistory.push({role: 'user', content: message});
            
            searchInput.value = '';
            appendSystemMessage('');

            // Call Backend Chat Service
            // Get Model Selection
            modelSelection = getModelSelected()
            kwargs = {"model_selection": modelSelection}
            callChatService(chatHistory, kwargs);
    }


    // Add New Append Dom Event
    // Returned Dom Add Event Listern to Parent Dom
    // Chatbox Returned Dom Add Event Listener to Body
    document.body.addEventListener('click', (e) => {
        // add event listern to header
        if (e.target.matches('.tool-call-container, .tool-call-header, .arrow, .header-text')) {
            handleToolCallHeaderClick(e.target);
        }

        // add return button click
        if (e.target.matches(".agent-button-base")) {
            handleToolCallResultUserSelect(e.target);
        }

        // 
        if (e.target.matches(".delete-tool")) {
            handleToolboxItemDelete(e.target)
        }

    });

    function handleToolCallHeaderClick(target) {

        var container = target.closest('.tool-call-container');
        if (container) {
            // Call back to get the result again
            var curContentArea = container.querySelector('.collapsible-content');
            var curHeader = container.querySelector('.tool-call-header');
            var curArrow = container.querySelector('.arrow');
            var curContentArea = container.querySelector('.collapsible-content');

            if (curContentArea != null) {
                const isExpanded = curContentArea.classList.toggle('expanded');
                curArrow.textContent = isExpanded ? '▼' : '▶';
                
                if (isExpanded && curContentArea.children.length === 0) {

                    // update new Json
                    addParametersSection(jsonData);
                    addButtonOptionsSection();
                    // simulateAsyncResult();
                }
                console.log('Button container clicked:', container);
            }
        }
    }

    /**
    * Add Click Event to Rendered Element in Html
    */
    function addEventListenerDynamicButton(buttonElement, actionName) {
        if (buttonElement == null) {
            return;
        }
        buttonElement.addEventListener('click', () => {
                clickButtonAction(actionName); 
            }
        );
        buttonElement.setAttribute("set_on_click", true);
        console.log(buttonElement)
    }

    /**
    * <input type="button" class="agent-button-base agent-button-highlight" value="ACCEPT">
    */
    function handleToolCallResultUserSelect(button) {        
        // addEventListenerDynamicButton(buttonElem, actionName);
        clickButtonAction(button.value);
    }


    function handleToolboxItemDelete(toolDeleteSpan) {
        
        var toolItem = toolDeleteSpan.parentElement;
        if (toolItem != null) {
            toolItem.remove();
        }
    }

});
