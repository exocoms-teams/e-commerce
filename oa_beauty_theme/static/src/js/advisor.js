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

function initOaAdvisor() {
    if (document.getElementById('oa_advisor_quiz') && !window.oaAdvisorInitialized) {
        window.oaAdvisorInitialized = true;
        OaAdvisor.init();
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initOaAdvisor);
} else {
    initOaAdvisor();
}
