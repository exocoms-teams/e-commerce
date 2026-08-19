/**
 * oa_beauty_theme — Floating AI Chatbot
 * Communicates with /api/chat/message (Odoo JSON-RPC endpoint)
 *
 * Pattern IIFE (identique à newsletter.js / oa_search.js)
 * pour éviter les problèmes de lazy-loading des @odoo-module non importés.
 */

(function () {
    'use strict';

    // Fallback _t compatible Odoo 19 (même pattern que newsletter.js)
    var _t = function (key) {
        return (window.odoo && window.odoo._t) ? window.odoo._t(key) : key;
    };

    var OaChatbot = {
        isOpen: false,
        isTyping: false,
        conversationHistory: [],

        init: function () {
            this.bindEvents();
            var self = this;
            setTimeout(function () {
                var toggle = document.getElementById('oa_chat_toggle');
                if (toggle) {
                    toggle.classList.add('oa-chat-pulse');
                    setTimeout(function () {
                        toggle.classList.remove('oa-chat-pulse');
                    }, 2500);
                }
            }, 3000);
        },

        bindEvents: function () {
            var self = this;

            var toggleBtn = document.getElementById('oa_chat_toggle');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', function () { self.toggleChat(); });
            }

            var closeBtn = document.getElementById('oa_chat_close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function () { self.closeChat(); });
            }

            var sendBtn = document.getElementById('oa_chat_send');
            if (sendBtn) {
                sendBtn.addEventListener('click', function () { self.sendMessage(); });
            }

            var input = document.getElementById('oa_chat_input');
            if (input) {
                input.addEventListener('keydown', function (e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        self.sendMessage();
                    }
                });
            }

            document.querySelectorAll('.oa-chat-chip').forEach(function (chip) {
                chip.addEventListener('click', function (e) {
                    var inp = document.getElementById('oa_chat_input');
                    if (inp) inp.value = e.currentTarget.dataset.msg;
                    self.sendMessage();
                    var qr = document.getElementById('oa_chat_quick_replies');
                    if (qr) qr.style.display = 'none';
                });
            });
        },

        toggleChat: function () {
            if (this.isOpen) {
                this.closeChat();
            } else {
                this.openChat();
            }
        },

        openChat: function () {
            this.isOpen = true;
            var win = document.getElementById('oa_chat_window');
            var toggle = document.getElementById('oa_chat_toggle');
            if (win) {
                win.style.display = 'flex';
                win.classList.add('oa-chat-open');
            }
            if (toggle) {
                var iconOpen = toggle.querySelector('.oa-chat-icon-open');
                var iconClose = toggle.querySelector('.oa-chat-icon-close');
                if (iconOpen) iconOpen.style.display = 'none';
                if (iconClose) iconClose.style.display = 'inline';
            }
            var input = document.getElementById('oa_chat_input');
            if (input) input.focus();
        },

        closeChat: function () {
            this.isOpen = false;
            var win = document.getElementById('oa_chat_window');
            var toggle = document.getElementById('oa_chat_toggle');
            if (win) {
                win.classList.remove('oa-chat-open');
                setTimeout(function () {
                    win.style.display = 'none';
                }, 300);
            }
            if (toggle) {
                var iconOpen = toggle.querySelector('.oa-chat-icon-open');
                var iconClose = toggle.querySelector('.oa-chat-icon-close');
                if (iconOpen) iconOpen.style.display = 'inline';
                if (iconClose) iconClose.style.display = 'none';
            }
        },

        appendMessage: function (text, sender) {
            var messagesEl = document.getElementById('oa_chat_messages');
            if (!messagesEl) return;
            var msg = document.createElement('div');
            msg.className = 'oa-chat-msg oa-chat-msg--' + sender;
            msg.innerHTML = '<p>' + text + '</p>';
            messagesEl.appendChild(msg);
            messagesEl.scrollTop = messagesEl.scrollHeight;
        },

        showTyping: function (show) {
            var indicator = document.getElementById('oa_chat_typing');
            if (indicator) indicator.style.display = show ? 'flex' : 'none';
            var messagesEl = document.getElementById('oa_chat_messages');
            if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
        },

        sendMessage: function () {
            var self = this;
            var input = document.getElementById('oa_chat_input');
            var message = input && input.value ? input.value.trim() : '';
            if (!message || this.isTyping) return;

            input.value = '';
            this.appendMessage(message, 'user');
            this.conversationHistory.push({ role: 'user', text: message });

            this.isTyping = true;
            this.showTyping(true);

            if (!this.isOpen) this.openChat();

            var history = this.conversationHistory.slice();

            fetch('/api/chat/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    id: 1,
                    params: { message: message, history: history }
                })
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                var reply = (data && data.result && data.result.reply)
                    ? data.result.reply
                    : _t("Je suis desole, je n'ai pas pu traiter votre demande. Veuillez reessayer.");
                return new Promise(function (resolve) {
                    setTimeout(function () { resolve(reply); }, 600 + Math.random() * 400);
                });
            })
            .then(function (reply) {
                self.showTyping(false);
                self.appendMessage(reply, 'bot');
                self.conversationHistory.push({ role: 'bot', text: reply });
            })
            .catch(function (e) {
                self.showTyping(false);
                self.appendMessage(_t("Desole, j'ai du mal a me connecter. Veuillez reessayer dans un instant."), 'bot');
                console.error('[OA Chatbot]', e);
            })
            .finally(function () {
                self.isTyping = false;
            });
        }
    };

    function initOaChatbot() {
        if (document.getElementById('oa_chat_toggle') && !window.oaChatbotInitialized) {
            window.oaChatbotInitialized = true;
            OaChatbot.init();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initOaChatbot);
    } else {
        initOaChatbot();
    }

})();
