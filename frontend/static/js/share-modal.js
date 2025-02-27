// Share modal functionality
document.addEventListener('DOMContentLoaded', function() {
    // Wait for a short delay to ensure all elements are loaded
    setTimeout(() => {
        const shareButton = document.getElementById('share-button');
        const shareModal = document.getElementById('share-modal');
        const closeModal = document.getElementById('close-modal');
        const copyLink = document.getElementById('copy-link');

        if (!shareButton || !shareModal) {
            console.log('Share functionality not available - required elements missing');
            return;
        }

        // Show modal
        shareButton.addEventListener('click', () => {
            shareModal.classList.remove('hidden');
        });

        // Close modal with close button
        if (closeModal) {
            closeModal.addEventListener('click', () => {
                shareModal.classList.add('hidden');
            });
        }

        // Close modal when clicking outside
        shareModal.addEventListener('click', (e) => {
            if (e.target === shareModal) {
                shareModal.classList.add('hidden');
            }
        });

        // Copy link functionality
        if (copyLink) {
            copyLink.addEventListener('click', () => {
                const url = window.location.href;
                navigator.clipboard.writeText(url).then(() => {
                    const originalText = copyLink.textContent;
                    copyLink.textContent = 'Copied!';
                    setTimeout(() => {
                        copyLink.textContent = originalText;
                    }, 2000);
                });
            });
        }

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !shareModal.classList.contains('hidden')) {
                shareModal.classList.add('hidden');
            }
        });
    }, 100); // Small delay to ensure DOM is fully loaded
});