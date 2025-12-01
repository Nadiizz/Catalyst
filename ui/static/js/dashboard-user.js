/* ============================================================
   DASHBOARD-USER.JS - Lógica para el dashboard de usuario
   ============================================================ */

document.addEventListener('DOMContentLoaded', async () => {
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (currentUser.role === 'vendedor') {
        await loadVendorDashboard();
    } else {
        await loadCustomerDashboard();
    }
    
    document.getElementById('btn-refresh').addEventListener('click', () => {
        location.reload();
    });
});

async function loadVendorDashboard() {
    try {
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
        
        // Mis ventas
        let sales = await apiService.getSales();
        if (!Array.isArray(sales)) {
            sales = sales && sales.results ? sales.results : [];
        }
        
        const mySales = Array.isArray(sales) ? sales.filter(s => s.seller === currentUser.id) : [];
        
        document.getElementById('my-sales').textContent = mySales.length;
        
        const totalSales = mySales.reduce((sum, sale) => sum + parseFloat(sale.total || 0), 0);
        document.getElementById('my-total').textContent = formatters.currency(totalSales);

        // Mis órdenes (si también es cliente)
        let orders = await apiService.getOrders({ user: currentUser.id });
        if (!Array.isArray(orders)) {
            orders = orders && orders.results ? orders.results : [];
        }
        
        document.getElementById('my-orders').textContent = orders.length;

        const pendingOrders = Array.isArray(orders) ? orders.filter(o => o.status === 'pendiente').length : 0;
        document.getElementById('pending-total').textContent = pendingOrders;

        // Mostrar ventas recientes
        loadMySales(Array.isArray(mySales) ? mySales.slice(0, 10) : []);
        loadMyOrders(Array.isArray(orders) ? orders.slice(0, 10) : []);

        AlertManager.success('Dashboard actualizado');
    } catch (error) {
        console.error('Error loading vendor dashboard:', error);
        AlertManager.error('Error al cargar el dashboard');
    }
}

async function loadCustomerDashboard() {
    try {
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
        
        // Mis órdenes
        let orders = await apiService.getOrders({ user: currentUser.id });
        
        // Validar que orders sea un array
        if (!Array.isArray(orders)) {
            orders = orders && orders.results ? orders.results : [];
        }
        
        document.getElementById('my-orders').textContent = orders.length;

        const totalSpent = Array.isArray(orders) ? orders.reduce((sum, order) => sum + parseFloat(order.total || 0), 0) : 0;
        document.getElementById('my-total').textContent = formatters.currency(totalSpent);

        const pendingOrders = Array.isArray(orders) ? orders.filter(o => o.status === 'pendiente').length : 0;
        document.getElementById('pending-total').textContent = pendingOrders;

        // Ocultar sección de ventas para clientes
        const salesTable = document.getElementById('my-sales-table');
        if (salesTable && salesTable.parentElement && salesTable.parentElement.parentElement) {
            salesTable.parentElement.parentElement.remove();
        }

        // Mostrar órdenes
        loadMyOrders(Array.isArray(orders) ? orders.slice(0, 10) : []);

        AlertManager.success('Dashboard actualizado');
    } catch (error) {
        console.error('Error loading customer dashboard:', error);
        AlertManager.error('Error al cargar el dashboard');
    }
}

function loadMySales(sales) {
    const tbody = document.getElementById('my-sales-body');
    
    if (!sales || sales.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No hay ventas registradas</td></tr>`;
        return;
    }
    
    tbody.innerHTML = sales.map(sale => `
        <tr>
            <td><strong>${sale.receipt_number || 'N/A'}</strong></td>
            <td>${formatters.currency(sale.total || 0)}</td>
            <td>${sale.payment_method_display || sale.payment_method}</td>
            <td>${formatters.date(sale.created_at)}</td>
            <td>
                <a href="/ventas/${sale.id}/" class="btn btn-sm btn-outline">Detalles</a>
            </td>
        </tr>
    `).join('');
}

function loadMyOrders(orders) {
    const tbody = document.getElementById('my-orders-body');
    
    if (!orders || orders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No hay órdenes</td></tr>`;
        return;
    }
    
    tbody.innerHTML = orders.map(order => `
        <tr>
            <td><strong>${order.order_number || 'N/A'}</strong></td>
            <td>${formatters.currency(order.total || 0)}</td>
            <td>
                <span class="badge badge-${determineBadgeClass(order.status)}">
                    ${order.status_display || order.status}
                </span>
            </td>
            <td>${formatters.date(order.created_at)}</td>
            <td>
                <a href="/ordenes/${order.id}/" class="btn btn-sm btn-outline">Ver</a>
            </td>
        </tr>
    `).join('');
}

function determineBadgeClass(status) {
    const statusMap = {
        'entregada': 'success',
        'cancelada': 'danger',
        'pendiente': 'warning',
        'procesando': 'info'
    };
    
    return statusMap[status] || 'warning';
}
