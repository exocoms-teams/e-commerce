/* ============================================
   CHART UTILITIES
   Create and manage charts
   ============================================ */

class ChartManager {
    static charts = {};

    /**
     * Create spending chart
     */
    static createSpendingChart(ctx, data) {
        const labels = Object.keys(data).reverse();
        const amounts = labels.map(label => data[label].amount);
        const counts = labels.map(label => data[label].count);

        if (this.charts.spending) {
            this.charts.spending.destroy();
        }

        this.charts.spending = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Spending ($)',
                        data: amounts,
                        backgroundColor: 'rgba(102, 126, 234, 0.7)',
                        borderColor: '#667eea',
                        borderWidth: 2,
                        borderRadius: 8,
                        tension: 0.4
                    },
                    {
                        label: 'Purchases',
                        data: counts,
                        backgroundColor: 'rgba(240, 147, 251, 0.7)',
                        borderColor: '#f093fb',
                        borderWidth: 2,
                        borderRadius: 8,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Amount ($)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Count'
                        }
                    }
                }
            }
        });
    }

    /**
     * Create category chart
     */
    static createCategoryChart(ctx, categories) {
        const labels = categories.map(c => c.name);
        const data = categories.map(c => c.count);

        if (this.charts.category) {
            this.charts.category.destroy();
        }

        this.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [
                    {
                        data: data,
                        backgroundColor: [
                            '#667eea',
                            '#764ba2',
                            '#f093fb',
                            '#48dbfb',
                            '#ff6b6b',
                            '#ffa502',
                            '#1dd1a1',
                            '#5f27cd'
                        ],
                        borderColor: '#fff',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    /**
     * Create price distribution chart
     */
    static createPriceChart(ctx, distribution) {
        const labels = Object.keys(distribution);
        const data = Object.values(distribution);

        if (this.charts.price) {
            this.charts.price.destroy();
        }

        this.charts.price = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Number of Purchases',
                        data: data,
                        backgroundColor: '#48dbfb',
                        borderColor: '#1ba0e1',
                        borderWidth: 2,
                        borderRadius: 8
                    }
                ]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    /**
     * Create trend chart
     */
    static createTrendChart(ctx, data) {
        const labels = Object.keys(data).reverse();
        const amounts = labels.map(label => data[label].amount);

        if (this.charts.trend) {
            this.charts.trend.destroy();
        }

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Spending Trend',
                        data: amounts,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 6,
                        pointBackgroundColor: '#667eea',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Amount ($)'
                        }
                    }
                }
            }
        });
    }

    /**
     * Create frequency chart
     */
    static createFrequencyChart(ctx, data) {
        const labels = Object.keys(data).reverse();
        const counts = labels.map(label => data[label].count);

        if (this.charts.frequency) {
            this.charts.frequency.destroy();
        }

        this.charts.frequency = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Purchase Frequency',
                        data: counts,
                        borderColor: '#f093fb',
                        backgroundColor: 'rgba(240, 147, 251, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointBackgroundColor: '#f093fb',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Purchases'
                        }
                    }
                }
            }
        });
    }

    /**
     * Destroy all charts
     */
    static destroyAll() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// Simple Chart.js alternative if not loaded
if (typeof Chart === 'undefined') {
    console.warn('⚠️ Chart.js not loaded. Charts will be disabled.');
}
