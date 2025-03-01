document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatForm = document.querySelector('#chat-form');
    const chatInput = document.querySelector('#user-input');
    const sendButton = document.querySelector('#sendButton');
    const guidanceTiles = document.querySelector('.guidance-tiles');
    const chatMessages = document.querySelector('#chat-messages');
    const initialView = document.querySelector('#initial-view');
    const chatView = document.querySelector('#chat-view');
    const queryDetails = document.querySelector('#query-details');
    const queryDetailsHeader = document.querySelector('.query-details-header');
    const queryDetailsContent = document.querySelector('.query-details-content');
    const sqlQueryText = document.querySelector('#sql-query-text');
    const queryTime = document.querySelector('#query-time');
    const totalResults = document.querySelector('#total-results');
    const toggleDetailsBtn = document.querySelector('#toggle-details');
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = '<div class="spinner"></div>';

    // Use relative URL instead of hardcoded IP
    const API_BASE_URL = '';

    // Initially hide the chat view
    if (chatView) chatView.style.display = 'none';

    // State
    let isLoading = false;
    let isQueryDetailsExpanded = false;

    function showLoading() {
        isLoading = true;
        if (chatMessages) {
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'loading';
            loadingDiv.textContent = 'Thinking';
            chatMessages.appendChild(loadingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function hideLoading() {
        isLoading = false;
        const indicators = chatMessages?.querySelectorAll('.loading');
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
            const toggleIcon = toggleDetailsBtn.querySelector('.toggle-icon');
            if (toggleIcon) {
                toggleIcon.textContent = isQueryDetailsExpanded ? '▼' : '▲';
            }
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
            const response = await fetch(`/api/rag-sql-chatbot/chat`, {
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
            
            // Update query details panel with metadata
            if (data.metadata) {
                updateQueryDetails(data.metadata);
            }
            
            // Handle the results
            if (data.results && data.results.length > 0) {
                data.results.forEach(result => {
                    if (result.type === 'text') {
                        appendMessage(result.message);
                    }
                });
            } else {
                appendMessage("I couldn't find any projects matching your criteria. Please try a different query.");
            }
            
        } catch (error) {
            console.error('Error:', error);
            appendMessage(`Sorry, there was an error processing your request. Server error: ${error.message}`);
        } finally {
            hideLoading();
        }
    }

    function appendMessage(message, isUser = false) {
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event Listeners
    chatForm?.addEventListener('submit', sendMessage);
    
    // Add click handlers to guidance tiles
    const exampleQueries = document.querySelectorAll('.example-query');
    exampleQueries?.forEach(query => {
        query.addEventListener('click', () => {
            if (chatInput) {
                chatInput.value = query.textContent;
                chatForm?.dispatchEvent(new Event('submit'));
            }
        });
    });

    // Add click handler for toggle details button
    toggleDetailsBtn?.addEventListener('click', toggleQueryDetails);
});
