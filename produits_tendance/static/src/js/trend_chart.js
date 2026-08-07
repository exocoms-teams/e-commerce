/** @odoo-module **/
/* static/src/js/trend_chart.js
   Courbe de tendance (WIN-52) : initialise Chart.js sur le canvas de la
   fiche produit détaillée, à partir de l'historique déjà agrégé par date
   côté ORM (get_score_history, controllers/dashboard_api.py). */

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WinnersTrendChart = publicWidget.Widget.extend({
    selector: ".o_winners_trend_chart__canvas_wrapper",

    /**
     * @override
     */
    start() {
        const res = this._super(...arguments);
        this._renderChart();
        return res;
    },

    _renderChart() {
        const canvas = this.el.querySelector("canvas");
        if (!canvas) {
            return;
        }

        let history = [];
        try {
            history = JSON.parse(this.el.dataset.history || "[]");
        } catch {
            history = [];
        }
        if (!history.length) {
            return;
        }

        const lineColor = getComputedStyle(this.el)
            .getPropertyValue("--o-winners-chart-line-color")
            .trim();

        this.chart = new Chart(canvas.getContext("2d"), {
            type: "line",
            data: {
                datasets: [
                    {
                        label: "Score de tendance",
                        data: history.map((point) => ({ x: point.date, y: point.score })),
                        borderColor: lineColor,
                        backgroundColor: lineColor,
                        tension: 0.3,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: "time",
                        time: { unit: "day" },
                    },
                    y: {
                        beginAtZero: true,
                    },
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `Score : ${ctx.parsed.y.toFixed(1)}`,
                        },
                    },
                },
            },
        });
    },

    /**
     * @override
     */
    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = undefined;
        }
        this._super(...arguments);
    },
});

export default publicWidget.registry.WinnersTrendChart;
