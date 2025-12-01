/* ORDENES-MANAGER.JS */

const ordenesState = {
    ordenes: [],
    currentPage: 1,
    pageSize: 20,
    filters: { search: '' }
};

document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    await loadOrdenes();
});

function setupEventListeners() {
    document.getElementById('btn-new-order').addEventListener('click', openNewOrderModal);
    document.getElementById('btn-refresh').addEventListener('click', () => loadOrdenes());

    document.getElementById('search-order').addEventListener('input', (e) => {
        ordenesState.filters.search = e.target.value;
        ordenesState.currentPage = 1;
        loadOrdenes();
    });

    document.getElementById('filter-status').addEventListener('change', (e) => {
        ordenesState.filters.status = e.target.value;
        ordenesState.currentPage = 1;
        loadOrdenes();
    });
}

async function loadOrdenes() {
    try {
        const params = { page: ordenesState.currentPage, ...ordenesState.filters };
        const response = await apiService.getOrders(params);
        ordenesState.ordenes = response.results || response;
        renderTable(ordenesState.ordenes);
        renderPagination(response.count);
    } catch (error) {
        console.error('Error loading orders:', error);
        AlertManager.error('Error al cargar órdenes');
        renderTable([]);
    }
}

function renderTable(ordenes) {
    const tbody = document.getElementById('ordenes-tbody');
    
    if (!ordenes || ordenes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Sin órdenes</td></tr>`;
        return;
    }
    
    tbody.innerHTML = ordenes.map(o => `
        <tr>
            <td><strong>${o.order_number}</strong></td>
            <td>${formatters.date(o.created_at)}</td>
            <td>${o.customer_name || 'N/A'}</td>
            <td>${formatters.currency(o.total || 0)}</td>
            <td>
                <span class="badge ${getStatusBadge(o.status)}">
                    ${o.status_display || o.status}
                </span>
            </td>
            <td>${o.delivery_date ? formatters.date(o.delivery_date) : 'Pendiente'}</td>
            <td>
                <button class="btn btn-sm btn-outline" onclick="viewOrder(${o.id})">Ver</button>
                <button class="btn btn-sm btn-danger" onclick="deleteOrder(${o.id})">Eliminar</button>
            </td>
        </tr>
    `).join('');
}

function getStatusBadge(status) {
    const statusMap = {
        'pendiente': 'badge-warning',
        'procesando': 'badge-info',
        'entregada': 'badge-success',
        'cancelada': 'badge-danger'
    };
    return statusMap[status] || 'badge-secondary';
}

function renderPagination(total) {
    const totalPages = Math.ceil(total / ordenesState.pageSize);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    for (let i = 1; i <= totalPages; i++) {
        html += `<a href="#" onclick="goToPage(${i})" class="${i === ordenesState.currentPage ? 'active' : ''}">${i}</a>`;
    }
    pagination.innerHTML = html;
}

function goToPage(page) {
    event.preventDefault();
    ordenesState.currentPage = page;
    loadOrdenes();
}

async function viewOrder(id) {
    try {
        const order = await apiService.getOrder(id);
        const modal = new Modal();
        modal.setContent(`
            <div>
                <h3>Orden #${order.order_number}</h3>
                <p><strong>Cliente:</strong> ${order.customer_name}</p>
                <p><strong>Total:</strong> ${formatters.currency(order.total)}</p>
                <p><strong>Estado:</strong> ${order.status_display}</p>
                <p><strong>Fecha:</strong> ${formatters.date(order.created_at)}</p>
                <p><strong>Entrega:</strong> ${order.delivery_date ? formatters.date(order.delivery_date) : 'Por definir'}</p>
            </div>
        `);
        modal.addFooter(`<button class="btn btn-secondary" onclick="Modal.close()">Cerrar</button>`);
        modal.show();
    } catch (error) {
        AlertManager.error('Error al cargar la orden');
    }
}

async function deleteOrder(id) {
    if (!confirm('¿Está seguro?')) return;
    try {
        await apiService.deleteOrder(id);
        AlertManager.success('Orden eliminada');
        await loadOrdenes();
    } catch (error) {
        console.error('Error deleting order:', error);
        let errorMsg = 'Error al eliminar orden';
        if (error.response && error.response.data) {
            if (typeof error.response.data === 'object') {
                const firstError = Object.values(error.response.data)[0];
                errorMsg = `Error: ${Array.isArray(firstError) ? firstError[0] : firstError}`;
            } else {
                errorMsg = `Error: ${error.response.data}`;
            }
        }
        AlertManager.error(errorMsg);
    }
}

function openNewOrderModal() {
    const modal = new Modal();
    modal.setContent(`<div class="empty-state"><p>Crear órdenes desde e-commerce</p></div>`);
    modal.addFooter(`<button class="btn btn-secondary" onclick="Modal.close()">Cerrar</button>`);
    modal.show();
}
