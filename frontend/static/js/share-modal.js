// Share modal functionality
document.addEventListener('DOMContentLoaded', function() {
    const shareButton = document.querySelector('.share-button');
    const shareModal = document.querySelector('.share-modal');
    
    if (shareButton && shareModal) {
        shareButton.addEventListener('click', function() {
            shareModal.classList.toggle('hidden');
        });
    }
}); 