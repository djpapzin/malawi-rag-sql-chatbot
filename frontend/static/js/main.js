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

    // Use relative URL instead of hardcoded IP
    const API_BASE_URL = '';

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
            if (chatInput) {
                chatInput.value = queryText;
                
                // Show the chat view
                if (initialView) initialView.style.display = 'none';
                if (chatView) chatView.style.display = 'block';
                
                // Send the query
                sendMessage(queryText);
            }
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
            
            // Clear input - ensure this happens
            chatInput.value = '';
            
            // Force focus back to the input
            setTimeout(() => {
                chatInput.focus();
            }, 0);
            
            // Send message
            await sendMessage(message);
        });
    }

    async function sendMessage(message) {
        if (isLoading) return;
        showLoading();
        
        // Add user message
        appendMessage(message, true);
        
        try {
            // Get session ID from the last bot message if it exists
            const lastBotMessage = chatMessages.querySelector('.bot-message-container:last-of-type');
            const sessionId = lastBotMessage?.dataset.sessionId;
            
            const response = await fetch(`/api/rag-sql-chatbot/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            // Ensure input is cleared again after API call
            if (chatInput) {
                chatInput.value = '';
            }
            
            const data = await response.json();
            
            // Update query details panel with metadata
            if (data.metadata) {
                updateQueryDetails(data.metadata);
            }
            
            // Handle the results
            if (data.results && data.results.length > 0) {
                const messageContainer = document.createElement('div');
                messageContainer.className = 'bot-message-container';
                
                // Store session ID if provided
                if (data.pagination && data.pagination.session_id) {
                    messageContainer.dataset.sessionId = data.pagination.session_id;
                }
                
                data.results.forEach(result => {
                    if (result.type === 'text') {
                        // Check if message is a string or an object
                        if (typeof result.message === 'string') {
                            appendMessage(result.message, false, false, messageContainer);
                        } else if (result.message && result.message.response) {
                            // Handle nested response format
                            const response = result.message.response;
                            if (response.results && response.results.length > 0) {
                                response.results.forEach(item => {
                                    if (item.message) {
                                        appendMessage(item.message, false, false, messageContainer);
                                    }
                                });
                            } else if (typeof response === 'string') {
                                appendMessage(response, false, false, messageContainer);
                            }
                        } else if (result.message) {
                            // Try to extract any message content
                            const messageContent = extractMessageContent(result.message);
                            if (messageContent) {
                                appendMessage(messageContent, false, false, messageContainer);
                            } else {
                                console.warn('Unrecognized message format:', result.message);
                                appendMessage("Received a response in an unexpected format.", false, false, messageContainer);
                            }
                        }
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
                
                // Add pagination controls if needed
                if (data.pagination) {
                    const paginationDiv = createPaginationControls(data.pagination);
                    messageContainer.appendChild(paginationDiv);
                }
                
                chatMessages.appendChild(messageContainer);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else {
                appendMessage("I couldn't find any projects matching your criteria. Please try a different query.");
            }
            
        } catch (error) {
            console.error('Error:', error);
            appendMessage(`Sorry, there was an error processing your request. ${error.message}`);
        } finally {
            hideLoading();
        }
    }

    function createPaginationControls(pagination) {
        const paginationDiv = document.createElement('div');
        paginationDiv.className = 'pagination-controls';
        
        // Add page info
        const pageInfo = document.createElement('span');
        pageInfo.className = 'pagination-info';
        pageInfo.textContent = `Page ${pagination.current_page} of ${pagination.total_pages}`;
        paginationDiv.appendChild(pageInfo);
        
        // Add navigation buttons
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'pagination-buttons';
        
        if (pagination.has_previous) {
            const prevButton = document.createElement('button');
            prevButton.className = 'pagination-button';
            prevButton.textContent = '← Previous';
            prevButton.onclick = () => {
                if (chatInput && !isLoading) {
                    chatInput.value = pagination.prev_page_command || "previous page";
                    chatForm.dispatchEvent(new Event('submit'));
                }
            };
            buttonContainer.appendChild(prevButton);
        }
        
        if (pagination.has_more) {
            const nextButton = document.createElement('button');
            nextButton.className = 'pagination-button';
            nextButton.textContent = 'Next →';
            nextButton.onclick = () => {
                if (chatInput && !isLoading) {
                    chatInput.value = pagination.next_page_command || "next page";
                    chatForm.dispatchEvent(new Event('submit'));
                }
            };
            buttonContainer.appendChild(nextButton);
        }
        
        paginationDiv.appendChild(buttonContainer);
        return paginationDiv;
    }

    function extractMessageContent(messageObj) {
        // Try to extract message content from various possible formats
        if (typeof messageObj === 'string') {
            return messageObj;
        }
        
        if (messageObj.message) {
            return messageObj.message;
        }
        
        if (messageObj.response && typeof messageObj.response === 'string') {
            return messageObj.response;
        }
        
        if (messageObj.response && messageObj.response.results) {
            const results = messageObj.response.results;
            if (Array.isArray(results) && results.length > 0) {
                const messages = results
                    .filter(r => r.message)
                    .map(r => r.message);
                if (messages.length > 0) {
                    return messages.join('\n');
                }
            }
        }
        
        // If we can't extract a specific message, stringify the object
        // but limit its size to avoid overwhelming the UI
        try {
            const jsonStr = JSON.stringify(messageObj);
            if (jsonStr.length > 500) {
                return jsonStr.substring(0, 500) + '... (truncated)';
            }
            return jsonStr;
        } catch (e) {
            return "Received a complex response that couldn't be displayed.";
        }
    }

    function appendMessage(message, isUser = false, isError = false, container = null) {
        if (!chatMessages && !container) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'message user' : 'message bot';
        if (isError) {
            messageDiv.classList.add('error-message');
        }
        
        // Create avatar
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = isUser ? '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>' : '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>';
        
        // Create content
        const content = document.createElement('div');
        content.className = 'message-content';
        content.style.fontWeight = isUser ? '500' : '400';
        content.style.color = isUser ? '#ffffff' : (document.body.classList.contains('dark-mode') ? '#e8eaed' : '#202124');
        content.textContent = message;
        
        // Append elements
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        // Append to container or chat messages
        if (container) {
            container.appendChild(messageDiv);
        } else {
            chatMessages.appendChild(messageDiv);
        }
        
        // Scroll to bottom if appending to chat messages
        if (!container) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function appendTable(title, data, container = null) {
        const tableDiv = document.createElement('div');
        tableDiv.className = 'table-container';
        
        if (title) {
            const titleElement = document.createElement('h3');
            titleElement.textContent = title;
            tableDiv.appendChild(titleElement);
        }
        
        if (data && data.headers && data.rows) {
            const table = document.createElement('table');
            table.className = 'results-table';
            
            // Create header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            data.headers.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);
            
            // Create body
            const tbody = document.createElement('tbody');
            data.rows.forEach(row => {
                const tr = document.createElement('tr');
                data.headers.forEach(header => {
                    const td = document.createElement('td');
                    td.textContent = row[header] || '';
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            
            tableDiv.appendChild(table);
        }
        
        if (container) {
            container.appendChild(tableDiv);
        } else if (chatMessages) {
            chatMessages.appendChild(tableDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function appendList(title, data, container = null) {
        if (!chatMessages || !data || !data.fields || !data.values) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message list-message';
        
        // Add title if provided
        if (title) {
            const titleElement = document.createElement('h3');
            titleElement.className = 'list-title';
            titleElement.textContent = title;
            messageDiv.appendChild(titleElement);
        }
        
        // Create list for each project
        data.values.forEach((project, index) => {
            const projectDiv = document.createElement('div');
            projectDiv.className = 'project-item';
            
            const projectTitle = document.createElement('h4');
            projectTitle.textContent = `Project ${index + 1}`;
            projectDiv.appendChild(projectTitle);
            
            const detailsList = document.createElement('ul');
            detailsList.className = 'project-details-list';
            
            data.fields.forEach(field => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `<strong>${field}:</strong> ${project[field] || 'Unknown'}`;
                detailsList.appendChild(listItem);
            });
            
            projectDiv.appendChild(detailsList);
            messageDiv.appendChild(projectDiv);
        });
        
        if (container) {
            container.appendChild(messageDiv);
        } else if (chatMessages) {
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function appendProjectDetails(title, data, container = null) {
        if (!chatMessages || !data || !data.project) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        
        // Apply styling based on theme
        const isDarkMode = document.body.classList.contains('dark-mode');
        
        // Create the project details container
        const detailsContainer = document.createElement('div');
        detailsContainer.className = 'project-details-container';
        detailsContainer.style.display = 'block';
        detailsContainer.style.width = '100%';
        detailsContainer.style.backgroundColor = isDarkMode ? '#303134' : '#f8f9fa';
        detailsContainer.style.color = isDarkMode ? '#e8eaed' : '#202124';
        detailsContainer.style.borderRadius = '8px';
        detailsContainer.style.padding = '15px';
        detailsContainer.style.marginTop = '10px';
        
        // Add title if provided
        if (title) {
            const titleElement = document.createElement('h3');
            titleElement.className = 'project-details-title';
            titleElement.textContent = title;
            titleElement.style.fontSize = '18px';
            titleElement.style.fontWeight = 'bold';
            titleElement.style.marginBottom = '10px';
            titleElement.style.color = isDarkMode ? '#e8eaed' : '#202124';
            detailsContainer.appendChild(titleElement);
        }
        
        // Create the project card
        const projectCard = document.createElement('div');
        projectCard.className = 'project-card';
        projectCard.style.display = 'block';
        projectCard.style.width = '100%';
        projectCard.style.backgroundColor = isDarkMode ? '#3c4043' : '#ffffff';
        projectCard.style.borderRadius = '6px';
        projectCard.style.padding = '12px';
        projectCard.style.boxShadow = isDarkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)';
        
        // Add project title instead of number
        const projectTitle = document.createElement('h4');
        projectTitle.className = 'project-title';
        projectTitle.textContent = data.project['Name of project'] || data.project.project_name || 'Project Details';
        projectTitle.style.fontSize = '16px';
        projectTitle.style.fontWeight = 'bold';
        projectTitle.style.marginBottom = '10px';
        projectTitle.style.color = isDarkMode ? '#8ab4f8' : '#1a73e8';
        projectCard.appendChild(projectTitle);
        
        // Add project details
        const project = data.project;
        
        // Define field display order and formatting
        const fieldOrder = [
            'Name of project', 
            'project_name',
            'Fiscal year', 
            'fiscal_year',
            'Location', 
            'location',
            'Budget', 
            'total_budget',
            'Status', 
            'status',
            'Project Sector', 
            'project_sector'
        ];
        
        // Field display names (for formatting)
        const fieldDisplayNames = {
            'project_name': 'Project Name',
            'fiscal_year': 'Fiscal Year',
            'location': 'Location',
            'total_budget': 'Budget',
            'status': 'Status',
            'project_sector': 'Project Sector'
        };
        
        // Track which fields have been displayed to avoid duplicates
        const displayedFields = new Set();
        
        // First display fields in the preferred order
        fieldOrder.forEach(field => {
            if (project[field] && !displayedFields.has(field.toLowerCase())) {
                addFieldToCard(field);
                displayedFields.add(field.toLowerCase());
            }
        });
        
        // Then add any remaining fields not in the preferred order
        Object.keys(project).forEach(field => {
            if (!displayedFields.has(field.toLowerCase())) {
                addFieldToCard(field);
                displayedFields.add(field.toLowerCase());
            }
        });
        
        function addFieldToCard(field) {
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'project-field';
            fieldDiv.style.display = 'flex';
            fieldDiv.style.width = '100%';
            fieldDiv.style.marginBottom = '8px';
            
            const fieldName = document.createElement('span');
            fieldName.className = 'field-name';
            
            // Use the display name if available, otherwise format the field name
            const displayName = fieldDisplayNames[field] || field;
            fieldName.textContent = displayName + ':';
            
            fieldName.style.flexShrink = '0';
            fieldName.style.width = '140px';
            fieldName.style.color = isDarkMode ? '#a8c7fa' : '#1967d2';
            fieldName.style.fontWeight = '600';
            
            const fieldValue = document.createElement('span');
            fieldValue.className = 'field-value';
            
            // Format the value based on field type
            let displayValue = project[field];
            
            // Format budget values
            if (field.toLowerCase().includes('budget') && !isNaN(displayValue)) {
                displayValue = parseFloat(displayValue).toLocaleString('en-US', {
                    style: 'currency',
                    currency: 'MWK',
                    maximumFractionDigits: 0
                });
            }
            
            fieldValue.textContent = displayValue || 'Unknown';
            fieldValue.style.flexGrow = '1';
            fieldValue.style.color = isDarkMode ? '#e8eaed' : '#202124';
            
            fieldDiv.appendChild(fieldName);
            fieldDiv.appendChild(fieldValue);
            projectCard.appendChild(fieldDiv);
        }
        
        // Create avatar
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = 'D';
        
        detailsContainer.appendChild(projectCard);
        
        // Append elements
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(detailsContainer);
        
        if (container) {
            container.appendChild(messageDiv);
        } else if (chatMessages) {
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
});
