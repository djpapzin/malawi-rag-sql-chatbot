document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('user-input');
    const sendButton = document.getElementById('sendButton');
    const guidanceTiles = document.querySelector('.guidance-tiles');
    const chatMessages = document.getElementById('chat-messages');
    const initialView = document.getElementById('initial-view');
    const chatView = document.getElementById('chat-view');
    const queryDetails = document.getElementById('query-details');
    const queryDetailsHeader = document.querySelector('.query-details-header');
    const queryDetailsContent = document.querySelector('.query-details-content');
    const sqlQueryText = document.getElementById('sql-query-text');
    const queryTime = document.getElementById('query-time');
    const totalResults = document.getElementById('total-results');
    const toggleDetailsBtn = document.getElementById('toggle-details');
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = '<div class="spinner"></div>';

    // Get the base URL from the current window location
    const baseUrl = window.location.origin;

    // Validate required DOM elements
    const requiredElements = { chatInput, sendButton, guidanceTiles, chatMessages, chatForm, queryDetails, queryDetailsHeader, queryDetailsContent, sqlQueryText, queryTime, totalResults, toggleDetailsBtn };
    for (const [name, element] of Object.entries(requiredElements)) {
        if (!element) {
            console.error(`Required DOM element not found: ${name}`);
            return;
        }
    }

    // Initially hide the chat view
    if (chatView) chatView.style.display = 'none';

    // State
    let isLoading = false;
    let isQueryDetailsExpanded = false;

    function showLoading() {
        isLoading = true;
        if (chatMessages) {
            chatMessages.appendChild(loadingIndicator.cloneNode(true));
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function hideLoading() {
        isLoading = false;
        const indicators = chatMessages?.querySelectorAll('.loading-indicator');
        indicators?.forEach(indicator => indicator.remove());
    }

    function updateQueryDetails(metadata) {
        if (!metadata) return;
        
        // Show query details panel
        if (queryDetails) {
            queryDetails.classList.remove('hidden');
        }
        
        // Update SQL query
        if (sqlQueryText && metadata.sql_query) {
            sqlQueryText.textContent = metadata.sql_query;
        }
        
        // Update metadata
        if (queryTime) {
            queryTime.textContent = metadata.query_time || '0s';
        }
        if (totalResults) {
            totalResults.textContent = metadata.total_results || '0';
        }
    }

    function toggleQueryDetails() {
        isQueryDetailsExpanded = !isQueryDetailsExpanded;
        
        if (queryDetailsContent) {
            queryDetailsContent.classList.toggle('expanded', isQueryDetailsExpanded);
        }
        
        if (toggleDetailsBtn) {
            toggleDetailsBtn.classList.toggle('expanded', isQueryDetailsExpanded);
        }
    }

    async function sendMessage(e) {
        if (e) e.preventDefault();
        if (isLoading) return;
        
        const message = chatInput?.value?.trim();
        if (!message) return;
        
        showLoading();
        
        // Clear input
        if (chatInput) chatInput.value = '';

        // Show chat view and hide initial view
        if (initialView) initialView.style.display = 'none';
        if (chatView) chatView.style.display = 'block';
        
        // Add user message
        appendMessage(message, true);
        
        try {
            const response = await fetch(`${baseUrl}/api/rag-sql-chatbot/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message
                })
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();
            console.log('Response:', data);
            
            // Update query details panel with metadata
            if (data.response?.metadata) {
                updateQueryDetails(data.response.metadata);
            }
            
            // Handle different response types
            if (data.response?.query_type === "chat") {
                // For chat responses (greetings, help, other)
                const message = data.response.results[0]?.message;
                if (message) {
                    appendMessage(message);
                }
            } else if (data.response?.results?.length > 0) {
                // For SQL query responses
                const results = data.response.results;
                
                // If there's an explanation, show it first
                if (data.response.explanation) {
                    appendMessage(data.response.explanation);
                }
                
                // Show each result
                results.forEach(result => {
                    // Format the response in a user-friendly way
                    const details = [];
                    if (result.project_name) {
                        details.push(`📋 Project: ${result.project_name}`);
                    }
                    if (result.district) {
                        details.push(`📍 District: ${result.district}`);
                    }
                    if (result.project_sector) {
                        details.push(`🏗️ Sector: ${result.project_sector}`);
                    }
                    if (result.project_status) {
                        details.push(`📊 Status: ${result.project_status}`);
                    }
                    if (result.total_budget) {
                        const budget = typeof result.total_budget === 'object' ? 
                            result.total_budget.formatted : 
                            `MWK ${Number(result.total_budget).toLocaleString()}`;
                        details.push(`💰 Budget: ${budget}`);
                    }
                    if (result.completion_percentage !== undefined) {
                        details.push(`✅ Completion: ${result.completion_percentage}%`);
                    }
                    if (result.start_date) {
                        details.push(`📅 Start Date: ${result.start_date}`);
                    }
                    if (result.completion_date) {
                        details.push(`🏁 Completion Date: ${result.completion_date}`);
                    }
                    
                    if (details.length > 0) {
                        appendMessage(details.join('\n'));
                    }
                });
            } else {
                appendMessage("I couldn't find any projects matching your criteria. Please try a different query.");
            }
            
        } catch (error) {
            console.error('Error:', error);
            appendMessage(`Sorry, there was an error processing your request: ${error.message}`);
        } finally {
            hideLoading();
        }
    }

    function appendMessage(message, isUser = false) {
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const iconSpan = document.createElement('span');
        iconSpan.className = 'message-icon';
        iconSpan.textContent = isUser ? '👤' : '🤖';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = message;
        
        messageDiv.appendChild(iconSpan);
        messageDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event Listeners
    chatForm?.addEventListener('submit', sendMessage);
    
    chatInput?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Query details toggle
    queryDetailsHeader?.addEventListener('click', toggleQueryDetails);
    toggleDetailsBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleQueryDetails();
    });

    // Handle tile clicks
    function initiateChat(query) {
        if (chatInput && query) {
            chatInput.value = query;
            sendMessage();
        }
    }

    // Add click handlers to guidance tiles
    const tiles = guidanceTiles?.querySelectorAll('.tile');
    tiles?.forEach(tile => {
        const query = tile.querySelector('.example-query')?.textContent?.replace('Example: ', '')?.replace(/["]/g, '');
        if (query) {
            tile.addEventListener('click', () => initiateChat(query));
        }
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
