/** @odoo-module **/

/**
 * O&A Beauty Advisor — Quiz & Recommendation Engine
 * Communicates with /api/advisor/recommend (Odoo JSON-RPC endpoint)
 */

const OaAdvisor = {
    currentStep: 1,
    totalSteps: 5,
    profile: {},

    init() {
        this.bindEvents();
    },

    bindEvents() {
        // Option selection
        document.querySelectorAll('.oa-advisor-option').forEach(btn => {
            btn.addEventListener('click', e => this.selectOption(e.currentTarget));
        });

        // Navigation
        document.getElementById('oa_advisor_next')?.addEventListener('click', () => this.nextStep());
        document.getElementById('oa_advisor_back')?.addEventListener('click', () => this.prevStep());
        document.getElementById('oa_advisor_restart')?.addEventListener('click', () => this.restart());

        // Quick reply chips
        document.querySelectorAll('[data-msg]').forEach(chip => {
            chip.addEventListener('click', e => {
                const input = document.getElementById('oa_chat_input');
                if (input) { input.value = e.currentTarget.dataset.msg; }
                OaChatbot.sendMessage();
            });
        });
    },

    selectOption(btn) {
        const container = btn.closest('.oa-advisor-options');
        container.querySelectorAll('.oa-advisor-option').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');

        // Save to profile
        const field = container.dataset.field;
        this.profile[field] = btn.dataset.value;

        // Enable next
        const nextBtn = document.getElementById('oa_advisor_next');
        if (nextBtn) nextBtn.disabled = false;
    },

    updateProgress() {
        const pct = (this.currentStep / this.totalSteps) * 100;
        const bar = document.getElementById('oa_advisor_progress');
        const label = document.getElementById('oa_advisor_step_label');
        if (bar) bar.style.width = pct + '%';
        if (label) label.textContent = `Step ${this.currentStep} of ${this.totalSteps}`;
    },

    showStep(step) {
        document.querySelectorAll('.oa-advisor-step').forEach(el => el.classList.remove('active'));
        const target = document.querySelector(`.oa-advisor-step[data-step="${step}"]`);
        if (target) target.classList.add('active');

        const nextBtn = document.getElementById('oa_advisor_next');
        const backBtn = document.getElementById('oa_advisor_back');

        if (nextBtn) {
            // Check if this step already has a selection
            const field = target?.querySelector('.oa-advisor-options')?.dataset.field;
            nextBtn.disabled = field && !this.profile[field];
            nextBtn.textContent = step === this.totalSteps ? 'Get My Routine ✨' : 'Next →';
        }
        if (backBtn) backBtn.style.display = step > 1 ? 'inline-block' : 'none';

        this.updateProgress();
    },

    nextStep() {
        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.showStep(this.currentStep);
        } else {
            this.submitQuiz();
        }
    },

    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.showStep(this.currentStep);
        }
    },

    async submitQuiz() {
        const quizEl = document.getElementById('oa_advisor_quiz');
        const loadingEl = document.getElementById('oa_advisor_loading');
        if (quizEl) quizEl.style.display = 'none';
        if (loadingEl) loadingEl.style.display = 'block';

        try {
            const res = await fetch('/api/advisor/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jsonrpc: '2.0', method: 'call', params: this.profile })
            });
            const data = await res.json();
            const result = data.result;

            if (loadingEl) loadingEl.style.display = 'none';
            this.renderResults(result);
        } catch (e) {
            if (loadingEl) loadingEl.innerHTML = '<p class="text-danger">Something went wrong. Please try again.</p>';
            console.error('[OA Advisor]', e);
        }
    },

    renderResults(result) {
        const resultsEl = document.getElementById('oa_advisor_results');
        if (!resultsEl) return;

        // Explanation
        const expEl = document.getElementById('oa_advisor_explanation');
        if (expEl) expEl.innerHTML = `<p class="oa-advisor-explain-text"><i class="fa fa-leaf me-2"></i>${result.explanation}</p>`;

        // Routine Steps
        const routineEl = document.getElementById('oa_advisor_routine');
        if (routineEl && result.routine) {
            routineEl.innerHTML = result.routine.map(s => `
                <div class="oa-advisor-routine-step">
                    <div class="oa-advisor-step-number">${s.step.split(':')[0]}</div>
                    <div class="oa-advisor-step-info">
                        <strong>${s.step.split(':').slice(1).join(':').trim()}</strong>
                        <span>${s.product}</span>
                        <p>${s.desc}</p>
                    </div>
                </div>
            `).join('');
        }

        // Product Cards
        const productsEl = document.getElementById('oa_advisor_products');
        if (productsEl && result.products) {
            productsEl.innerHTML = result.products.map(p => `
                <a href="${p.url}" class="oa-advisor-product-card">
                    <div class="oa-advisor-product-img-wrap">
                        <img src="${p.image_url}" alt="${p.name}" loading="lazy"/>
                    </div>
                    <div class="oa-advisor-product-info">
                        <div class="oa-advisor-product-name">${p.name}</div>
                        <div class="oa-advisor-product-price">€${p.price.toFixed(2)}</div>
                        <div class="oa-advisor-product-cta">View Product →</div>
                    </div>
                </a>
            `).join('');
        }

        resultsEl.style.display = 'block';
        resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },

    restart() {
        this.currentStep = 1;
        this.profile = {};
        document.querySelectorAll('.oa-advisor-option').forEach(b => b.classList.remove('selected'));
        document.getElementById('oa_advisor_results').style.display = 'none';
        document.getElementById('oa_advisor_quiz').style.display = 'block';
        this.showStep(1);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('oa_advisor_quiz')) {
        OaAdvisor.init();
    }
});
