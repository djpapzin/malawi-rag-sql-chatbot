document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('user-input');
    const sendButton = document.getElementById('sendButton');
    const guidanceTiles = document.querySelector('.guidance-tiles');
    const chatMessages = document.getElementById('chat-messages');
    const initialView = document.getElementById('initial-view');
    const chatView = document.getElementById('chat-view');

    if (!chatInput || !sendButton || !guidanceTiles || !chatMessages || !chatForm) {
        console.error('Required DOM elements not found');
        return;
    }

    // Initially hide the chat view
    chatView.style.display = 'none';

    // State
    let isLoading = false;

    async function sendMessage(e) {
        if (e) e.preventDefault();
        if (isLoading) return;
        
        const message = chatInput.value.trim();
        if (!message) return;
        
        isLoading = true;
        
        // Clear input
        chatInput.value = '';

        // Show chat view and hide initial view
        initialView.style.display = 'none';
        chatView.style.display = 'block';
        
        // Add user message
        appendMessage(message, true);
        
        try {
            console.log('Sending request:', message);
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
            
            const response = await fetch('http://localhost:5000/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            const data = await response.json();
            console.log('Received response:', data);
            
            if (!response.ok) {
                throw new Error(data.detail || `Server error: ${response.status}`);
            }
            
            if (data && data.response) {
                // Format the response for display
                let formattedResponse = '';
                
                // Handle greeting messages
                if (data.response.query_type === "greeting" && data.response.results[0].message) {
                    formattedResponse = data.response.results[0].message;
                }
                // Handle query results
                else if (data.response.results && data.response.results.length > 0) {
                    // Check if it's a total budget query
                    if (data.response.results[0].total_budget && !data.response.results[0].project_name) {
                        const budget = data.response.results[0].total_budget;
                        formattedResponse = `The total budget is ${budget.formatted}`;
                    } else {
                        // Format multiple project results
                        formattedResponse = data.response.results.map(project => {
                            let details = [];
                            
                            if (project.project_name) {
                                details.push(`📋 Project: ${project.project_name}`);
                            }
                            
                            if (project.district) {
                                details.push(`📍 District: ${project.district}`);
                            }

                            if (project.region) {
                                details.push(`🌍 Region: ${project.region}`);
                            }
                            
                            if (project.project_sector) {
                                details.push(`🏗️ Sector: ${project.project_sector}`);
                            }
                            
                            if (project.project_status) {
                                details.push(`📊 Status: ${project.project_status}`);
                            }
                            
                            if (project.total_budget && project.total_budget.formatted) {
                                details.push(`💰 Budget: ${project.total_budget.formatted}`);
                            }
                            
                            if (project.completion_percentage !== undefined) {
                                details.push(`✅ Completion: ${project.completion_percentage}%`);
                            }

                            if (project.start_date) {
                                details.push(`📅 Start Date: ${project.start_date}`);
                            }

                            if (project.completion_date) {
                                details.push(`🏁 Completion Date: ${project.completion_date}`);
                            }
                            
                            return details.join('\n');
                        }).join('\n\n');
                        
                        // Add summary if there are multiple results
                        if (data.response.metadata && data.response.metadata.total_results > 1) {
                            formattedResponse += `\n\n📈 Found ${data.response.metadata.total_results} projects`;
                        }
                    }
                } else {
                    formattedResponse = 'I couldn\'t find any results matching your query. Try:\n\n' +
                        '• Being more specific about the location or sector\n' +
                        '• Checking for spelling mistakes\n' +
                        '• Using simpler terms\n' +
                        '• Asking about a different region or project type';
                }
                appendMessage(formattedResponse);
            } else {
                console.error('Invalid response format:', data);
                appendMessage('Sorry, I received an invalid response format. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            if (error.name === 'AbortError') {
                appendMessage('Sorry, the request took too long. Please try again with a simpler question.');
            } else {
                // Provide more helpful error messages
                let errorMessage = 'I encountered an error. ';
                if (error.message.includes('Must include FROM')) {
                    errorMessage += 'Could you please rephrase your question to be more specific about what project information you\'re looking for?';
                } else if (error.message.includes('500')) {
                    errorMessage += 'The server encountered an issue. Please try asking a different question about the projects.';
                } else {
                    errorMessage += error.message;
                }
                appendMessage(errorMessage);
            }
        } finally {
            isLoading = false;
        }
    }

    function appendMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message p-4 ${isUser ? 'bg-[#2e2e2e]' : 'bg-[#1e1e1e]'} rounded-lg`;

        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'flex items-start gap-4';

        const avatar = document.createElement('div');
        avatar.className = `avatar ${isUser ? 'bg-blue-500/20 text-blue-500' : 'bg-green-500/20 text-green-500'} p-2 rounded-lg`;
        avatar.innerHTML = isUser ? 
            '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>' :
            '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>';

        const messageContent = document.createElement('div');
        messageContent.className = 'flex-1 text-gray-300 whitespace-pre-wrap';
        messageContent.textContent = message;
        
        contentWrapper.appendChild(avatar);
        contentWrapper.appendChild(messageContent);
        messageDiv.appendChild(contentWrapper);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Handle form submission
    chatForm.addEventListener('submit', sendMessage);

    // Handle enter key press
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Handle tile clicks
    const tiles = document.querySelectorAll('.tile');
    tiles.forEach(tile => {
        tile.addEventListener('click', () => {
            const exampleQuery = tile.querySelector('.example-query').textContent;
            if (exampleQuery) {
                chatInput.value = exampleQuery.replace('Example: ', '').replace(/["]/g, '');
                sendMessage();
            }
        });
    });

    // Hide guidance tiles when chat starts
    chatInput.addEventListener('focus', () => {
        guidanceTiles.style.opacity = '0';
        setTimeout(() => {
            guidanceTiles.style.display = 'none';
        }, 300);
    });

    // Handle tile clicks
    window.initiateChat = function(query) {
        chatInput.value = query;
        sendMessage();
        guidanceTiles.style.opacity = '0';
        setTimeout(() => {
            guidanceTiles.style.display = 'none';
        }, 300);
    }
});
