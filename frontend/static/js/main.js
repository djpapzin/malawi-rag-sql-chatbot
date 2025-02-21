document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const guidanceTiles = document.querySelector('.guidance-tiles');
    const chatContainer = document.createElement('div');
    chatContainer.id = 'chat-container';
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

    function appendMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = isUser ? 'U' : 'D';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Format the message content
        let formattedContent = message;
        if (!isUser) {
            // Replace ### Step X: with formatted steps
            formattedContent = message.replace(/###\s*Step\s*\d+:/g, match => {
                return `<pre>${match}</pre>`;
            });
        }
        
        messageContent.innerHTML = formattedContent;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        chatContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async function sendMessage() {
        const message = chatInput.value.trim();
        
        if (!message) return;
        
        // Clear input
        chatInput.value = '';
        
        // Add user message
        appendMessage(message, true);
        
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
                }),
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            appendMessage(data.response);
        } catch (error) {
            console.error('Error:', error);
            appendMessage('Sorry, I encountered an error processing your request. Please try again.');
        }
    }

    // Handle send button click
    sendButton.addEventListener('click', sendMessage);

    // Handle enter key press
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
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
