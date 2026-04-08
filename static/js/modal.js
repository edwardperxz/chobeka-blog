function closeCurrentModal(trigger) {
    const parentModal = trigger ? trigger.closest('#confirmModal, #deleteConfirmModal, [role="dialog"]') : null;
    const fallbackModal = document.getElementById('confirmModal') || document.getElementById('deleteConfirmModal');
    const modal = parentModal || fallbackModal;

    if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        return;
    }

    window.location.href = '/';
}

document.addEventListener('click', function(e) {
    const trigger = e.target.closest('#closeModal, #cancelButton');
    if (!trigger) {
        return;
    }

    e.preventDefault();
    closeCurrentModal(trigger);
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