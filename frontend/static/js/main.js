document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatInput = document.getElementById('user-input');
    const sendButton = document.getElementById('sendButton');
    const guidanceTiles = document.querySelector('.guidance-tiles');
    const chatMessages = document.getElementById('chat-messages');

    if (!chatInput || !sendButton || !guidanceTiles || !chatMessages) {
        console.error('Required DOM elements not found');
        return;
    }

    // State
    let isLoading = false;

    // Hide guidance tiles when chat starts
    chatInput.addEventListener('focus', () => {
        guidanceTiles.style.opacity = '0';
        setTimeout(() => {
            guidanceTiles.style.display = 'none';
        }, 300);
    });

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

    function appendMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message flex items-start gap-2 mb-4 ${isUser ? 'justify-end' : ''}`;

        const avatar = document.createElement('div');
        avatar.className = `avatar ${isUser ? 'bg-blue-500' : 'bg-green-500'} text-white rounded-full w-8 h-8 flex items-center justify-center`;
        avatar.textContent = isUser ? 'U' : 'D';

        const messageContent = document.createElement('div');
        messageContent.className = `message-content max-w-[80%] p-3 rounded-lg ${isUser ? 'bg-blue-100' : 'bg-gray-100'}`;
        
        // Format the message content
        let formattedContent = message;
        if (!isUser) {
            formattedContent = message.replace(/###\s*Step\s*\d+:/g, match => {
                return `<strong class="block mb-2">${match}</strong>`;
            });
        }
        
        messageContent.innerHTML = formattedContent;
        
        if (isUser) {
            messageDiv.appendChild(messageContent);
            messageDiv.appendChild(avatar);
        } else {
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
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
    document.querySelectorAll('.tile').forEach(tile => {
        tile.addEventListener('click', () => {
            const exampleQuery = tile.querySelector('.example-query').textContent.replace('Example: ', '').replace(/["]/g, '');
            chatInput.value = exampleQuery;
            chatInput.focus();
            sendMessage();
            
            // Fade out guidance tiles
            guidanceTiles.style.opacity = '0';
            setTimeout(() => {
                guidanceTiles.style.display = 'none';
            }, 300);
        });
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
