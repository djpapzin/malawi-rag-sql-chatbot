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
    const themeToggle = document.querySelector('#theme-toggle');
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = '<div class="spinner"></div>';

    // Set the API base URL
    const API_BASE_URL = 'http://154.0.164.254:5000';

    // Initially hide the chat view
    if (chatView) chatView.style.display = 'none';

    // State
    let isLoading = false;
    let isQueryDetailsExpanded = false;
    
    // Theme handling
    function initTheme() {
        // Check for saved theme preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
        }
    }
    
    // Initialize theme on page load
    initTheme();
    
    // Theme toggle functionality
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            
            // Save preference to localStorage
            if (document.body.classList.contains('dark-mode')) {
                localStorage.setItem('theme', 'dark');
            } else {
                localStorage.setItem('theme', 'light');
            }
        });
    }

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
        
        // Update query time
        if (queryTime) {
            queryTime.textContent = metadata.query_time || '0s';
        }
        
        // Update total results
        if (totalResults) {
            totalResults.textContent = metadata.total_results || '0';
        }
    }

    // Toggle query details panel
    if (toggleDetailsBtn) {
        toggleDetailsBtn.addEventListener('click', () => {
            isQueryDetailsExpanded = !isQueryDetailsExpanded;
            if (queryDetailsContent) {
                queryDetailsContent.style.display = isQueryDetailsExpanded ? 'block' : 'none';
            }
            const toggleIcon = toggleDetailsBtn.querySelector('.toggle-icon');
            if (toggleIcon) {
                toggleIcon.textContent = isQueryDetailsExpanded ? '▲' : '▼';
            }
        });
    }

    // Handle example query clicks
    const exampleQueries = document.querySelectorAll('.example-query');
    exampleQueries.forEach(query => {
        query.addEventListener('click', () => {
            const queryText = query.textContent;
            
            // Show the chat view
            if (initialView) initialView.style.display = 'none';
            if (chatView) chatView.style.display = 'block';
            
            // Send the query without updating the input field
            sendMessage(queryText);
        });
    });

    // Handle form submission
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Show the chat view
            if (initialView) initialView.style.display = 'none';
            if (chatView) chatView.style.display = 'block';
            
            // Clear input and store message
            const userMessage = message;
            chatInput.value = '';
            
            // Force focus back to the input
            chatInput.focus();
            
            // Send message
            await sendMessage(userMessage);
        });
    }

    async function sendMessage(message) {
        if (isLoading) return;
        showLoading();
        
        // Add user message
        appendMessage(message, true);
        
        // Clear input field
        if (chatInput) {
            chatInput.value = '';
        }
        
        try {
            const response = await fetch('/api/rag-sql-chatbot/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Update query details panel with metadata
            if (data.metadata) {
                updateQueryDetails(data.metadata);
            }
            
            // Handle the results
            if (data.results && data.results.length > 0) {
                // Handle legacy format with 'results' array
                const messageContainer = document.createElement('div');
                messageContainer.className = 'bot-message-container';
                
                data.results.forEach(result => {
                    if (result.type === 'text') {
                        appendMessage(result.message, false, false, messageContainer);
                    } else if (result.type === 'table') {
                        appendTable(result.message, result.data, messageContainer);
                    } else if (result.type === 'list') {
                        appendList(result.message, result.data, messageContainer);
                    } else if (result.type === 'project_details') {
                        appendProjectDetails(result.message, result.data, messageContainer);
                    } else if (result.type === 'error') {
                        appendMessage(`Error: ${result.message}`, false, true, messageContainer);
                    }
                });
                
                chatMessages.appendChild(messageContainer);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else if (data.projects && data.projects.length > 0) {
                // Handle new format with 'projects' array
                const messageContainer = document.createElement('div');
                messageContainer.className = 'bot-message-container';
                
                // First add the response message
                if (data.response) {
                    // Check if response is an array (new format) or a string (old format)
                    if (Array.isArray(data.response)) {
                        // Handle response array with objects
                        data.response.forEach(item => {
                            if (item.type === 'text') {
                                appendMessage(item.message, false, false, messageContainer);
                            } else if (item.type === 'table') {
                                appendTable(item.message, item.data, messageContainer);
                            } else if (item.type === 'list') {
                                appendList(item.message, item.data, messageContainer);
                            } else if (item.type === 'project_details') {
                                appendProjectDetails(item.message, item.data, messageContainer);
                            }
                        });
                    } else {
                        // Handle legacy string response
                        appendMessage(data.response, false, false, messageContainer);
                    }
                }
                
                // Then add the projects as a table
                appendTable("Projects", data.projects, messageContainer);
                
                chatMessages.appendChild(messageContainer);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else if (data.response) {
                // If we have just a response message but no projects
                const messageContainer = document.createElement('div');
                messageContainer.className = 'bot-message-container';
                
                // Check if response is an array (new format) or a string (old format)
                if (Array.isArray(data.response)) {
                    // Handle response array with objects
                    data.response.forEach(item => {
                        if (item.type === 'text') {
                            appendMessage(item.message, false, false, messageContainer);
                        } else if (item.type === 'table') {
                            appendTable(item.message, item.data, messageContainer);
                        } else if (item.type === 'list') {
                            appendList(item.message, item.data, messageContainer);
                        } else if (item.type === 'project_details') {
                            appendProjectDetails(item.message, item.data, messageContainer);
                        }
                    });
                } else {
                    // Handle legacy string response
                    appendMessage(data.response, false, false, messageContainer);
                }
                
                chatMessages.appendChild(messageContainer);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else {
                // Fallback for no results
                appendMessage("I couldn't find any results for your query.", false, false);
            }
        } catch (error) {
            console.error('Error:', error);
            appendMessage("Sorry, I encountered an error while processing your request. Please try again.", false, true);
        } finally {
            hideLoading();
        }
    }

    function appendMessage(message, isUser = false, isError = false, container = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'} ${isError ? 'error-message' : ''}`;
        messageDiv.textContent = message;
        
        if (container) {
            container.appendChild(messageDiv);
        } else {
            chatMessages.appendChild(messageDiv);
        }
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendTable(title, data, container = null) {
        const tableDiv = document.createElement('div');
        tableDiv.className = 'table-container';
        
        if (title) {
            const titleDiv = document.createElement('div');
            titleDiv.className = 'table-title';
            titleDiv.textContent = title;
            tableDiv.appendChild(titleDiv);
        }
        
        const table = document.createElement('table');
        table.className = 'data-table';
        
        // Create header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        Object.keys(data[0]).forEach(key => {
            const th = document.createElement('th');
            th.textContent = key;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Create body
        const tbody = document.createElement('tbody');
        data.forEach(row => {
            const tr = document.createElement('tr');
            Object.values(row).forEach(value => {
                const td = document.createElement('td');
                td.textContent = value;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        
        tableDiv.appendChild(table);
        
        if (container) {
            container.appendChild(tableDiv);
        } else {
            chatMessages.appendChild(tableDiv);
        }
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendList(title, data, container = null) {
        const listDiv = document.createElement('div');
        listDiv.className = 'list-container';
        
        if (title) {
            const titleDiv = document.createElement('div');
            titleDiv.className = 'list-title';
            titleDiv.textContent = title;
            listDiv.appendChild(titleDiv);
        }
        
        // Create table instead of list for structured data
        const table = document.createElement('table');
        table.className = 'data-table';
        
        // Add header row
        if (data.fields && Array.isArray(data.fields)) {
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            data.fields.forEach(field => {
                const th = document.createElement('th');
                th.textContent = field;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);
        }
        
        // Add data rows
        if (data.values && Array.isArray(data.values)) {
            const tbody = document.createElement('tbody');
            data.values.forEach(item => {
                const row = document.createElement('tr');
                Object.values(item).forEach(value => {
                    const td = document.createElement('td');
                    td.textContent = value || '-';
                    row.appendChild(td);
                });
                tbody.appendChild(row);
            });
            table.appendChild(tbody);
        }
        
        listDiv.appendChild(table);
        
        if (container) {
            container.appendChild(listDiv);
        } else {
            chatMessages.appendChild(listDiv);
        }
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendProjectDetails(title, data, container = null) {
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'project-details';
        
        if (title) {
            const titleDiv = document.createElement('div');
            titleDiv.className = 'project-title';
            titleDiv.textContent = title;
            detailsDiv.appendChild(titleDiv);
        }
        
        const card = document.createElement('div');
        card.className = 'project-card';
        
        Object.entries(data).forEach(([key, value]) => {
            const field = document.createElement('div');
            field.className = 'project-field';
            field.innerHTML = `
                <span class="field-label">${key}:</span>
                <span class="field-value">${value}</span>
            `;
            card.appendChild(field);
        });
        
        detailsDiv.appendChild(card);
        
        if (container) {
            container.appendChild(detailsDiv);
        } else {
            chatMessages.appendChild(detailsDiv);
        }
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
