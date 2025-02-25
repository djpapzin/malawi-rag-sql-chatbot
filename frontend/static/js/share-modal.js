// Share modal functionality
document.addEventListener('DOMContentLoaded', function() {
    // Only try to initialize if the elements exist
    const initShareModal = () => {
        const shareButton = document.getElementById('share-button');
        const shareModal = document.getElementById('share-modal');
        
        if (!shareButton || !shareModal) {
            console.log('Share functionality not available - required elements missing');
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
    };

    // Try to initialize share modal
    initShareModal();
}); 