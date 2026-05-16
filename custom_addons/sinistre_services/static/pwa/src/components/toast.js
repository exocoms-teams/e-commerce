/**
 * toast.js — Notifications toast
 */

window.Toast = (() => {
    const container = () => document.getElementById('toastContainer');

    return {
        show(message, type = 'info', duration = 3500) {
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;

            const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
            toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;

            container().appendChild(toast);

            // Auto-remove
            setTimeout(() => {
                toast.classList.add('hide');
                setTimeout(() => toast.remove(), 350);
            }, duration);

            // Click to dismiss
            toast.addEventListener('click', () => {
                toast.classList.add('hide');
                setTimeout(() => toast.remove(), 350);
            });
        },
    };
})();
