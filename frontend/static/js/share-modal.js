// Share modal functionality
document.addEventListener('DOMContentLoaded', function() {
    const shareButton = document.getElementById('share-button');
    const shareModal = document.getElementById('share-modal');
    
    // Only initialize share functionality if both elements exist
    if (shareButton && shareModal) {
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
    }
}); 