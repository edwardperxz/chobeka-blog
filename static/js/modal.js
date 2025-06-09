document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('deleteConfirmModal');
    if (modal) {
        modal.classList.remove('hidden');
    }

    const closeBtn = document.getElementById('closeModal');
    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (modal) modal.classList.add('hidden');
        });
    }

    const cancelBtn = document.getElementById('cancelButton');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (modal) modal.classList.add('hidden');
        });
    }
});

/**
 * Lógica para cerrar modales de login/register en desktop:
 * - Al hacer click en el botón X o fuera del modal, redirige a la última URL válida (no login/register).
 * - Si no hay URL válida, redirige a "/".
 */

function safeBackOrHome() {
    const lastValidUrl = localStorage.getItem('lastValidUrl');
    if (lastValidUrl) {
        window.location.href = lastValidUrl;
    } else {
        window.location.href = '/';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Botón X (desktop)
    const closeBtn = document.getElementById('close-modal-desktop');
    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            safeBackOrHome();
        });
    }
    // Overlay (desktop)
    const overlay = document.getElementById('desktop-modal-overlay');
    if (overlay) {
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                safeBackOrHome();
            }
        });
    }
});