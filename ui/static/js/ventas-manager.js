/* VENTAS-MANAGER.JS */

const ventasState = {
    ventas: [],
    currentPage: 1,
    pageSize: 20,
    filters: { search: '' }
};

document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    await loadVentas();
});

function setupEventListeners() {
    document.getElementById('btn-new-sale').addEventListener('click', openNewSaleModal);
    document.getElementById('btn-refresh').addEventListener('click', () => loadVentas());

    document.getElementById('search-receipt').addEventListener('input', (e) => {
        ventasState.filters.search = e.target.value;
        ventasState.currentPage = 1;
        loadVentas();
    });

    document.getElementById('filter-payment-method').addEventListener('change', (e) => {
        ventasState.filters.payment_method = e.target.value;
        ventasState.currentPage = 1;
        loadVentas();
    });
}

async function loadVentas() {
    try {
        const params = { page: ventasState.currentPage, ...ventasState.filters };
        const response = await apiService.getSales(params);
        ventasState.ventas = response.results || response;
        renderTable(ventasState.ventas);
        renderPagination(response.count);
    } catch (error) {
        console.error('Error loading sales:', error);
        AlertManager.error('Error al cargar ventas');
        renderTable([]);
    }
}

function renderTable(ventas) {
    const tbody = document.getElementById('ventas-tbody');
    
    if (!ventas || ventas.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Sin ventas</td></tr>`;
        return;
    }
    
    tbody.innerHTML = ventas.map(v => `
        <tr>
            <td><strong>${v.receipt_number}</strong></td>
            <td>${formatters.date(v.created_at)}</td>
            <td>${v.customer_name || 'N/A'}</td>
            <td>${formatters.currency(v.total || 0)}</td>
            <td>${v.payment_method_display || v.payment_method}</td>
            <td>${v.seller_name || 'N/A'}</td>
            <td>
                <button class="btn btn-sm btn-outline" onclick="viewSale(${v.id})">Ver</button>
                <button class="btn btn-sm btn-danger" onclick="deleteSale(${v.id})">Eliminar</button>
            </td>
        </tr>
    `).join('');
}

function renderPagination(total) {
    const totalPages = Math.ceil(total / ventasState.pageSize);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    for (let i = 1; i <= totalPages; i++) {
        html += `<a href="#" onclick="goToPage(${i})" class="${i === ventasState.currentPage ? 'active' : ''}">${i}</a>`;
    }
    pagination.innerHTML = html;
}

function goToPage(page) {
    event.preventDefault();
    ventasState.currentPage = page;
    loadVentas();
}

async function viewSale(id) {
    try {
        const sale = await apiService.getSale(id);
        const modal = new Modal();
        modal.setContent(`
            <div>
                <h3>Venta #${sale.receipt_number}</h3>
                <p><strong>Cliente:</strong> ${sale.customer_name}</p>
                <p><strong>Total:</strong> ${formatters.currency(sale.total)}</p>
                <p><strong>Fecha:</strong> ${formatters.date(sale.created_at)}</p>
                <p><strong>Método de Pago:</strong> ${sale.payment_method_display}</p>
            </div>
        `);
        modal.addFooter(`<button class="btn btn-secondary" onclick="Modal.close()">Cerrar</button>`);
        modal.show();
    } catch (error) {
        AlertManager.error('Error al cargar la venta');
    }
}

async function deleteSale(id) {
    if (!confirm('¿Está seguro?')) return;
    try {
        await apiService.deleteSale(id);
        AlertManager.success('Venta eliminada');
        await loadVentas();
    } catch (error) {
        console.error('Error deleting sale:', error);
        let errorMsg = 'Error al eliminar venta';
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

function openNewSaleModal() {
    const modal = new Modal();
    modal.setContent(`
        <div class="empty-state">
            <p>Crear ventas desde punto de venta</p>
        </div>
    `);
    modal.addFooter(`<button class="btn btn-secondary" onclick="Modal.close()">Cerrar</button>`);
    modal.show();
}
