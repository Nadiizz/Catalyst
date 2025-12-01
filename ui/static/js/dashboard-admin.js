/* ============================================================
   DASHBOARD-ADMIN.JS - Lógica para el dashboard admin
   ============================================================ */

document.addEventListener('DOMContentLoaded', async () => {
    await loadDashboardData();
    
    document.getElementById('btn-refresh').addEventListener('click', loadDashboardData);
});

async function loadDashboardData() {
    try {
        // Cargar productos activos
        let products = await apiService.getActiveProducts();
        if (!Array.isArray(products)) {
            products = products && products.results ? products.results : [];
        }
        document.getElementById('total-products').textContent = products.length;

        // Cargar ventas del día
        let sales = await apiService.getSales({ 
            created_at__date: new Date().toISOString().split('T')[0] 
        });
        if (!Array.isArray(sales)) {
            sales = sales && sales.results ? sales.results : [];
        }
        const totalSales = Array.isArray(sales) ? sales.reduce((sum, sale) => sum + parseFloat(sale.total || 0), 0) : 0;
        document.getElementById('total-sales').textContent = formatters.currency(totalSales);

        // Cargar órdenes pendientes
        let orders = await apiService.getOrders({ status: 'pendiente' });
        if (!Array.isArray(orders)) {
            orders = orders && orders.results ? orders.results : [];
        }
        document.getElementById('total-orders').textContent = orders.length;

        // Cargar usuarios activos
        let users = await apiService.getUsers({ is_active: true });
        if (!Array.isArray(users)) {
            users = users && users.results ? users.results : [];
        }
        document.getElementById('total-users').textContent = users.length;

        // Ventas recientes
        loadRecentSales(Array.isArray(sales) ? sales.slice(0, 5) : []);

        // Órdenes pendientes
        loadPendingOrders(Array.isArray(orders) ? orders.slice(0, 10) : []);

        // Productos bajo stock
        await loadLowStock();

        AlertManager.success('Dashboard actualizado');
    } catch (error) {
        console.error('Error loading dashboard:', error);
        AlertManager.error('Error al cargar los datos del dashboard');
    }
}

function loadRecentSales(sales) {
    const tbody = document.getElementById('recent-sales');
    
    if (!sales || sales.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">No hay ventas</td></tr>`;
        return;
    }
    
    tbody.innerHTML = sales.map(sale => `
        <tr>
            <td>${sale.receipt_number || 'N/A'}</td>
            <td>${formatters.currency(sale.total || 0)}</td>
            <td>${formatters.date(sale.created_at)}</td>
            <td>
                <a href="/ventas/${sale.id}/" class="btn btn-sm btn-outline">Ver</a>
            </td>
        </tr>
    `).join('');
}

function loadPendingOrders(orders) {
    const tbody = document.getElementById('pending-orders');
    
    if (!orders || orders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No hay órdenes pendientes</td></tr>`;
        return;
    }
    
    tbody.innerHTML = orders.map(order => `
        <tr>
            <td>${order.order_number || 'N/A'}</td>
            <td>${order.customer_name || 'N/A'}</td>
            <td>${formatters.currency(order.total || 0)}</td>
            <td>
                <span class="badge badge-warning">${order.status_display || order.status}</span>
            </td>
            <td>
                <a href="/ordenes/${order.id}/" class="btn btn-sm btn-outline">Ver</a>
            </td>
        </tr>
    `).join('');
}

async function loadLowStock() {
    try {
        let inventory = await apiService.getInventory();
        if (!Array.isArray(inventory)) {
            inventory = inventory && inventory.results ? inventory.results : [];
        }
        
        const lowStock = Array.isArray(inventory) 
            ? inventory.filter(item => item.stock <= item.reorder_point).slice(0, 5)
            : [];
        
        const tbody = document.getElementById('low-stock');
        
        if (!lowStock || lowStock.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">Stock normal</td></tr>`;
            return;
        }
        
        tbody.innerHTML = lowStock.map(item => `
            <tr>
                <td>${item.product_name || 'N/A'}</td>
                <td><strong>${item.stock}</strong></td>
                <td>${item.branch_name || 'N/A'}</td>
                <td>
                    <a href="/inventario/${item.id}/" class="btn btn-sm btn-outline">Actualizar</a>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading low stock:', error);
        document.getElementById('low-stock').innerHTML = `
            <tr><td colspan="4" class="text-center text-danger">Error al cargar inventario</td></tr>
        `;
    }
}
