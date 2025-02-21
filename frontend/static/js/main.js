document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const guidanceTiles = document.querySelector('.guidance-tiles');
    const chatContainer = document.createElement('div');
    chatContainer.className = 'chat-container mt-4 w-full max-w-2xl space-y-4';
    chatInput.parentElement.insertBefore(chatContainer, chatInput.parentElement.firstChild);

    // State
    let isLoading = false;

    // Hide guidance tiles when chat starts
    chatInput.addEventListener('focus', () => {
        guidanceTiles.style.opacity = '0';
        setTimeout(() => {
            guidanceTiles.style.display = 'none';
        }, 300);
    });

    // Handle send button click
    sendButton.addEventListener('click', handleSendMessage);

    // Handle enter key press
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    async function handleSendMessage() {
        const message = chatInput.value.trim();
        if (message && !isLoading) {
            // Show user message
            appendMessage('user', message);
            
            // Clear input and set loading state
            chatInput.value = '';
            isLoading = true;
            toggleLoadingState(true);

            try {
                const response = await fetch('/api/rag-sql-chatbot/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        source_lang: 'english',
                        page: 1,
                        page_size: 30,
                        continue_previous: false
                    })
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                appendMessage('bot', data.response);
            } catch (error) {
                console.error('Error:', error);
                appendMessage('error', 'Sorry, I encountered an error processing your request. Please try again.');
            } finally {
                isLoading = false;
                toggleLoadingState(false);
            }
        }
    }

    function appendMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? 'U' : 'D';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (type === 'error') {
            messageContent.innerHTML = `<div class="error-text">${escapeHtml(content)}</div>`;
            messageDiv.classList.add('error');
        } else {
            messageContent.innerHTML = escapeHtml(content);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        chatContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        return messageDiv;
    }

    function toggleLoadingState(loading) {
        sendButton.disabled = loading;
        if (loading) {
            sendButton.innerHTML = `
                <svg class="animate-spin h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            `;
        } else {
            sendButton.innerHTML = `
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
            `;
        }
    }

    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Handle tile clicks
    window.initiateChat = function(message) {
        chatInput.value = message;
        handleSendMessage();
        guidanceTiles.style.opacity = '0';
        setTimeout(() => {
            guidanceTiles.style.display = 'none';
        }, 300);
    }
});
