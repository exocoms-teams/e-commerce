/* static/src/js/auth_login_win121.js */
/* WIN-121: Redesign Pages Connexion/Inscription - Interactions JS */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        
        // ============================================================
        // TOGGLE PASSWORD VISIBILITY
        // ============================================================
        const passwordToggles = document.querySelectorAll('.o_winners_password_toggle');
        
        passwordToggles.forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Trouver l'input de mot de passe associé
                const wrapper = this.closest('.o_winners_input_wrapper');
                const input = wrapper.querySelector('.o_winners_password_input');
                
                if (!input) return;
                
                // Toggle le type
                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                
                // Toggle l'icône
                const icon = this.querySelector('i');
                if (icon) {
                    icon.classList.toggle('fa-eye');
                    icon.classList.toggle('fa-eye-slash');
                }
                
                // Change la couleur au hover
                this.classList.toggle('o_winners_password_visible');
            });
        });

        // ============================================================
        // SOCIAL BUTTONS - Toast "Bientôt disponible"
        // ============================================================
        const socialButtons = document.querySelectorAll('.o_winners_btn_social');
        
        socialButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                
                const provider = this.dataset.provider || 'Social';
                
                // Afficher le toast
                showToast(`${provider} sera bientôt disponible`, 'info');
            });
        });

        // ============================================================
        // VALIDATION FORMULAIRE
        // ============================================================
        const forms = document.querySelectorAll('.o_winners_auth_form');
        
        forms.forEach(form => {
            // Validation en temps réel
            const inputs = form.querySelectorAll('.o_winners_input');
            
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    validateField(this);
                });
                
                input.addEventListener('input', function() {
                    if (this.classList.contains('o_winners_input_error')) {
                        validateField(this);
                    }
                });
            });
            
            // Submit
            form.addEventListener('submit', function(e) {
                let isValid = true;
                
                const requiredInputs = form.querySelectorAll('[required]');
                requiredInputs.forEach(input => {
                    if (!validateField(input)) {
                        isValid = false;
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    showToast('Veuillez corriger les erreurs', 'error');
                }
            });
        });

        // ============================================================
        // FONCTIONS UTILITAIRES
        // ============================================================
        
        /**
         * Valide un champ et applique les classes d'erreur/succès
         */
        function validateField(input) {
            const value = input.value.trim();
            const type = input.type;
            const wrapper = input.closest('.o_winners_input_wrapper');
            
            if (!wrapper) return true;
            
            // Réinitialiser les classes
            wrapper.classList.remove('o_winners_input_error', 'o_winners_input_valid', 'o_winners_input_success');
            
            // Validation par type
            if (type === 'email') {
                if (!isValidEmail(value)) {
                    wrapper.classList.add('o_winners_input_error');
                    return false;
                }
                wrapper.classList.add('o_winners_input_valid');
                return true;
            }
            
            if (type === 'password') {
                if (value.length < 8) {
                    wrapper.classList.add('o_winners_input_error');
                    return false;
                }
                wrapper.classList.add('o_winners_input_valid');
                return true;
            }
            
            if (input.name === 'name' || input.name === 'login') {
                if (value.length < 2) {
                    wrapper.classList.add('o_winners_input_error');
                    return false;
                }
                wrapper.classList.add('o_winners_input_valid');
                return true;
            }
            
            if (value) {
                wrapper.classList.add('o_winners_input_success');
                return true;
            }
            
            wrapper.classList.add('o_winners_input_error');
            return false;
        }

        /**
         * Valide le format email
         */
        function isValidEmail(email) {
            const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return regex.test(email);
        }

        /**
         * Affiche un toast de notification
         */
        function showToast(message, type = 'info') {
            // Créer le toast
            const toast = document.createElement('div');
            toast.className = `o_winners_toast o_winners_toast_${type}`;
            toast.textContent = message;
            
            // Ajouter les styles
            toast.style.cssText = `
                position: fixed;
                bottom: 24px;
                right: 24px;
                padding: 16px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                z-index: 9999;
                animation: slideIn 0.3s ease;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                max-width: 300px;
                word-wrap: break-word;
            `;
            
            // Couleurs selon le type
            const colors = {
                info: { bg: '#E3F2FD', text: '#1976D2' },
                success: { bg: '#E8F5E9', text: '#388E3C' },
                error: { bg: '#FFEBEE', text: '#D32F2F' },
                warning: { bg: '#FFF3E0', text: '#F57C00' }
            };
            
            const color = colors[type] || colors.info;
            toast.style.backgroundColor = color.bg;
            toast.style.color = color.text;
            
            // Ajouter au DOM
            document.body.appendChild(toast);
            
            // Supprimer après 3 secondes
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        // ============================================================
        // ANIMATIONS TOASTS
        // ============================================================
        if (!document.getElementById('o_winners_toast_styles')) {
            const style = document.createElement('style');
            style.id = 'o_winners_toast_styles';
            style.textContent = `
                @keyframes slideIn {
                    from {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                @keyframes slideOut {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                }

                @media (max-width: 768px) {
                    .o_winners_toast {
                        bottom: 16px !important;
                        right: 16px !important;
                        left: 16px !important;
                        max-width: none !important;
                    }
                }
            `;
            document.head.appendChild(style);
        }

    });

})();