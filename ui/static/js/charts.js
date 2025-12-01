// Chart.js - Configuración y utilidades para gráficos
class ChartManager {
    constructor() {
        this.charts = {};
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#cbd5e1',
                        font: { size: 12, weight: '500' },
                        padding: 15,
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.8)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#e2e8f0',
                    borderColor: '#475569',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                }
            },
            scales: {
                y: {
                    ticks: {
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: 'rgba(71, 85, 105, 0.2)',
                        drawBorder: false,
                    }
                },
                x: {
                    ticks: {
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: 'rgba(71, 85, 105, 0.2)',
                        drawBorder: false,
                    }
                }
            }
        };
    }

    createLineChart(canvasId, label, data, borderColor = '#6366f1', backgroundColor = 'rgba(99, 102, 241, 0.1)') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateLabels(data.length),
                datasets: [{
                    label: label,
                    data: data,
                    borderColor: borderColor,
                    backgroundColor: backgroundColor,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: borderColor,
                    pointBorderColor: '#0f172a',
                    pointBorderWidth: 2,
                    pointHoverRadius: 6,
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    filler: {
                        propagate: true
                    }
                }
            }
        });
    }

    createBarChart(canvasId, labels, datasets) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const colors = ['#6366f1', '#ec4899', '#8b5cf6', '#06b6d4'];
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets.map((dataset, idx) => ({
                    label: dataset.label,
                    data: dataset.data,
                    backgroundColor: colors[idx % colors.length],
                    borderRadius: 6,
                    borderSkipped: false,
                }))
            },
            options: {
                ...this.defaultOptions,
                indexAxis: 'x'
            }
        });
    }

    createDoughnutChart(canvasId, labels, data, colors = ['#6366f1', '#ec4899', '#8b5cf6', '#06b6d4']) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors.slice(0, data.length),
                    borderColor: '#1e293b',
                    borderWidth: 2,
                    hoverBorderColor: '#f1f5f9',
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#cbd5e1',
                            padding: 15,
                        }
                    }
                }
            }
        });
    }

    createRadarChart(canvasId, labels, datasets) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const colors = ['#6366f1', '#ec4899'];
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: datasets.map((dataset, idx) => ({
                    label: dataset.label,
                    data: dataset.data,
                    borderColor: colors[idx],
                    backgroundColor: `${colors[idx]}20`,
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: colors[idx],
                    pointHoverRadius: 6,
                }))
            },
            options: {
                ...this.defaultOptions,
                scales: {
                    r: {
                        ticks: {
                            color: '#cbd5e1'
                        },
                        grid: {
                            color: 'rgba(71, 85, 105, 0.2)',
                        }
                    }
                }
            }
        });
    }

    generateLabels(count, startDate = null) {
        const labels = [];
        const date = startDate || new Date();
        date.setDate(date.getDate() - count);

        for (let i = 0; i < count; i++) {
            date.setDate(date.getDate() + 1);
            labels.push(date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }));
        }
        return labels;
    }

    updateChart(canvasId, newData) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].data.datasets[0].data = newData;
            this.charts[canvasId].update();
        }
    }

    destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
            delete this.charts[canvasId];
        }
    }

    destroyAll() {
        Object.keys(this.charts).forEach(key => {
            this.charts[key].destroy();
            delete this.charts[key];
        });
    }
}

// Instancia global
const chartManager = new ChartManager();
