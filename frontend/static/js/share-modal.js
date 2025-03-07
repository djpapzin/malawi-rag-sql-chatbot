// Share modal functionality
document.addEventListener('DOMContentLoaded', function() {
    const shareButton = document.querySelector('.share-button');
    const shareModal = document.querySelector('.share-modal');
    const closeButton = document.querySelector('.share-modal .close-button');

    if (shareButton && shareModal && closeButton) {
        shareButton.addEventListener('click', function() {
            shareModal.classList.add('active');
        });

        closeButton.addEventListener('click', function() {
            shareModal.classList.remove('active');
        });

        // Close modal when clicking outside
        window.addEventListener('click', function(event) {
            if (event.target === shareModal) {
                shareModal.classList.remove('active');
            }
        });
    }
}); 