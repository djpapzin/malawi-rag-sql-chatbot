document.addEventListener('DOMContentLoaded', function() {
  // Wait a short moment for React to initialize
  setTimeout(function() {
    // Find the RAG SQL Chatbot tab by its text content and click it
    const tabElements = document.querySelectorAll('a, button, div');
    for (const element of tabElements) {
      if (element.textContent && element.textContent.trim() === 'RAG SQL Chatbot') {
        element.click();
        console.log('Automatically selected RAG SQL Chatbot tab');
        break;
      }
    }
  }, 500);
}); 