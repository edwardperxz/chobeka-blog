document.addEventListener('DOMContentLoaded', function() {
    // Show modal on page load
    document.getElementById('deleteConfirmModal').classList.remove('hidden');
// Handle close button
document.getElementById('closeModal').addEventListener('click', function() {
    window.history.back();
    });
// Handle cancel button to redirect back
document.getElementById('cancelButton').addEventListener('click', function() {
    window.history.back();
    });
});