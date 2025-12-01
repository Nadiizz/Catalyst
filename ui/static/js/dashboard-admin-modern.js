// Dashboard Admin - Moderno con Gráficos
class DashboardAdmin {
    constructor() {
        this.currentRange = 7;
        this.chartManager = window.chartManager;
        this.init();
    }

    init() {
        this.attachEventListeners();
        this.loadDashboardData();
        this.generateSampleCharts();
    }

    attachEventListeners() {
        // Date filter buttons
        document.querySelectorAll('.date-filter').forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (e.target.closest('.date-filter').dataset.range) {
                    document.querySelectorAll('.date-filter[data-range]').forEach(b => b.classList.remove('active'));
                    e.target.closest('.date-filter').classList.add('active');
                    this.currentRange = parseInt(e.target.closest('.date-filter').dataset.range);
                    this.loadDashboardData();
                }
            });
        });

        // Refresh button
        document.getElementById('btn-refresh')?.addEventListener('click', () => {
            this.loadDashboardData();
        });

        // Sidebar navigation
        document.querySelectorAll('.sidebar-menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });

        // Chart type switcher
        document.querySelectorAll('.chart-option-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const parent = e.target.closest('.chart-card');
                const buttons = parent.querySelectorAll('.chart-option-btn');
                buttons.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    }

    switchSection(section) {
        // Update sidebar
        document.querySelectorAll('.sidebar-menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update header
        const titles = {
            'overview': 'Vista General',
            'sales': 'Análisis de Ventas',
            'products': 'Gestión de Productos',
            'inventory': 'Control de Inventario',
            'users': 'Administración de Usuarios',
            'reports': 'Reportes'
        };

        document.getElementById('section-title').textContent = titles[section];
        document.getElementById('breadcrumb-section').textContent = titles[section];

        // Hide all sections, show active
        document.querySelectorAll('.dashboard-section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(`${section}-section`)?.classList.add('active');
    }

    loadDashboardData() {
        console.log(`Cargando datos del dashboard (últimos ${this.currentRange} días)...`);
        
        // Aquí iría la llamada a la API
        // Por ahora usamos datos de demostración
        this.updateMetrics();
        this.updateCharts();
        this.updateActivity();
    }

    updateMetrics() {
        // Datos de ejemplo
        const metrics = {
            sales: Math.random() * 50000 + 10000,
            orders: Math.floor(Math.random() * 150 + 50),
            products: Math.floor(Math.random() * 500 + 100),
            customers: Math.floor(Math.random() * 300 + 50)
        };

        document.getElementById('metric-sales').textContent = `$${metrics.sales.toFixed(2)}`;
        document.getElementById('metric-orders').textContent = metrics.orders.toString();
        document.getElementById('metric-products').textContent = metrics.products.toString();
        document.getElementById('metric-customers').textContent = metrics.customers.toString();
    }

    updateCharts() {
        // Destruir gráficos anteriores
        this.chartManager.destroyAll();

        // Gráfico de ventas
        const salesData = this.generateSalesData();
        this.chartManager.createLineChart(
            'salesChart',
            'Ventas Diarias',
            salesData,
            '#6366f1',
            'rgba(99, 102, 241, 0.1)'
        );

        // Gráfico de productos más vendidos
        const topProducts = ['Laptop', 'Mouse', 'Teclado', 'Monitor', 'Webcam'];
        this.chartManager.createBarChart(
            'productsChart',
            topProducts,
            [{
                label: 'Unidades Vendidas',
                data: [85, 72, 65, 58, 52]
            }]
        );

        // Gráfico de órdenes
        const orderStatus = ['Completadas', 'Pendientes', 'Canceladas'];
        this.chartManager.createDoughnutChart(
            'ordersChart',
            orderStatus,
            [320, 145, 25],
            ['#10b981', '#f59e0b', '#ef4444']
        );

        // Gráfico de ingresos por sucursal
        const branches = ['Sucursal 1', 'Sucursal 2', 'Sucursal 3', 'Sucursal 4'];
        this.chartManager.createBarChart(
            'branchesChart',
            branches,
            [{
                label: 'Ingresos ($)',
                data: [12500, 15000, 9800, 11200]
            }]
        );
    }

    generateSalesData() {
        const data = [];
        for (let i = 0; i < this.currentRange; i++) {
            data.push(Math.random() * 8000 + 2000);
        }
        return data;
    }

    updateActivity() {
        const activities = [
            { type: 'Venta', description: 'Venta completada por John Doe', date: 'Hace 2 horas', status: 'Completada' },
            { type: 'Inventario', description: 'Stock actualizado en Sucursal 1', date: 'Hace 4 horas', status: 'Completada' },
            { type: 'Usuario', description: 'Nuevo usuario registrado: Jane Smith', date: 'Hace 1 día', status: 'Completada' },
            { type: 'Orden', description: 'Orden #12345 en revisión', date: 'Hace 1 día', status: 'Pendiente' },
            { type: 'Reporte', description: 'Reporte semanal generado', date: 'Hace 2 días', status: 'Completada' },
        ];

        const tbody = document.getElementById('activity-tbody');
        tbody.innerHTML = activities.map(activity => `
            <tr>
                <td>
                    <span class="status-badge ${activity.type.toLowerCase()}">
                        ${this.getActivityIcon(activity.type)} ${activity.type}
                    </span>
                </td>
                <td>${activity.description}</td>
                <td>${activity.date}</td>
                <td>
                    <span class="status-badge ${activity.status.toLowerCase() === 'completada' ? 'active' : 'pending'}">
                        ${activity.status}
                    </span>
                </td>
            </tr>
        `).join('');
    }

    getActivityIcon(type) {
        const icons = {
            'Venta': '💰',
            'Inventario': '📦',
            'Usuario': '👤',
            'Orden': '📋',
            'Reporte': '📊'
        };
        return icons[type] || '📝';
    }

    generateSampleCharts() {
        // Este método se llama después de que los datos se cargan
        setTimeout(() => this.updateCharts(), 500);
    }
}

// Inicializar dashboard cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DashboardAdmin();
});
