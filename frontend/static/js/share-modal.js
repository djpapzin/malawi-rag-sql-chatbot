// Share modal functionality
document.addEventListener('DOMContentLoaded', function() {
    const shareButton = document.getElementById('share-button');
    const shareModal = document.getElementById('share-modal');
    
    // If share functionality is not available, hide the share button
    if (!shareButton || !shareModal) {
        if (shareButton) shareButton.style.display = 'none';
        return;
    }
    
    // Show modal
    shareButton.addEventListener('click', () => {
        shareModal.classList.remove('hidden');
    });
    
    // Close modal
    shareModal.addEventListener('click', (e) => {
        if (e.target === shareModal) {
            shareModal.classList.add('hidden');
        }
    });
    
    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !shareModal.classList.contains('hidden')) {
            shareModal.classList.add('hidden');
        }
    });
}); 