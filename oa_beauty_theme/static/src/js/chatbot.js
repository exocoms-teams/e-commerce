// O&A Beauty Chatbot - Floating AI Customer Assistant
// Communicates with /api/chat/message (Odoo JSON-RPC endpoint)

import { _t } from "@web/core/l10n/translation";

const OaChatbot = {
    isOpen: false,
    isTyping: false,
    conversationHistory: [],

    init() {
        this.bindEvents();
        setTimeout(() => {
            const toggle = document.getElementById('oa_chat_toggle');
            if (toggle) toggle.classList.add('oa-chat-pulse');
            setTimeout(() => toggle?.classList.remove('oa-chat-pulse'), 2500);
        }, 3000);
    },

    bindEvents() {
        document.getElementById('oa_chat_toggle')?.addEventListener('click', () => this.toggleChat());
        document.getElementById('oa_chat_close')?.addEventListener('click', () => this.closeChat());
        document.getElementById('oa_chat_send')?.addEventListener('click', () => this.sendMessage());

        const input = document.getElementById('oa_chat_input');
        input?.addEventListener('keydown', e => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        document.querySelectorAll('.oa-chat-chip').forEach(chip => {
            chip.addEventListener('click', e => {
                const input = document.getElementById('oa_chat_input');
                if (input) input.value = e.currentTarget.dataset.msg;
                this.sendMessage();
                const qr = document.getElementById('oa_chat_quick_replies');
                if (qr) qr.style.display = 'none';
            });
        });
    },

    toggleChat() {
        this.isOpen ? this.closeChat() : this.openChat();
    },

    openChat() {
        this.isOpen = true;
        const win = document.getElementById('oa_chat_window');
        const toggle = document.getElementById('oa_chat_toggle');
        if (win) {
            win.style.display = 'flex';
            win.classList.add('oa-chat-open');
        }
        if (toggle) {
            toggle.querySelector('.oa-chat-icon-open').style.display = 'none';
            toggle.querySelector('.oa-chat-icon-close').style.display = 'inline';
        }
        document.getElementById('oa_chat_input')?.focus();
    },

    closeChat() {
        this.isOpen = false;
        const win = document.getElementById('oa_chat_window');
        const toggle = document.getElementById('oa_chat_toggle');
        if (win) {
            win.classList.remove('oa-chat-open');
            setTimeout(() => {
                win.style.display = 'none';
            }, 300);
        }
        if (toggle) {
            toggle.querySelector('.oa-chat-icon-open').style.display = 'inline';
            toggle.querySelector('.oa-chat-icon-close').style.display = 'none';
        }
    },

    appendMessage(text, sender) {
        const messagesEl = document.getElementById('oa_chat_messages');
        if (!messagesEl) return;

        const msg = document.createElement('div');
        msg.className = `oa-chat-msg oa-chat-msg--${sender}`;
        msg.innerHTML = `<p>${text}</p>`;
        messagesEl.appendChild(msg);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    },

    showTyping(show) {
        const indicator = document.getElementById('oa_chat_typing');
        if (indicator) indicator.style.display = show ? 'flex' : 'none';
        const messagesEl = document.getElementById('oa_chat_messages');
        if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
    },

    async sendMessage() {
        const input = document.getElementById('oa_chat_input');
        const message = input?.value?.trim();
        if (!message || this.isTyping) return;

        input.value = '';
        this.appendMessage(message, 'user');
        this.conversationHistory.push({ role: 'user', text: message });

        this.isTyping = true;
        this.showTyping(true);

        if (!this.isOpen) this.openChat();

        try {
            const res = await fetch('/api/chat/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: { message, history: this.conversationHistory } })
            });
            const data = await res.json();
            const reply = data?.result?.reply || _t("Je suis désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer.");

            await new Promise(r => setTimeout(r, 600 + Math.random() * 400));

            this.showTyping(false);
            this.appendMessage(reply, 'bot');
            this.conversationHistory.push({ role: 'bot', text: reply });
        } catch (e) {
            this.showTyping(false);
            this.appendMessage(_t("Désolé, j'ai du mal à me connecter. Veuillez réessayer dans un instant."), 'bot');
            console.error('[OA Chatbot]', e);
        } finally {
            this.isTyping = false;
        }
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
