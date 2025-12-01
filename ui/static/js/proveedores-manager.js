/* PROVEEDORES-MANAGER.JS */

const proveedoresState = {
    proveedores: [],
    currentPage: 1,
    pageSize: 20,
    filters: { search: '' }
};

document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    await loadProveedores();
});

function setupEventListeners() {
    document.getElementById('btn-new-supplier').addEventListener('click', openNewSupplierModal);
    document.getElementById('btn-refresh').addEventListener('click', () => loadProveedores());

    document.getElementById('search-name').addEventListener('input', (e) => {
        proveedoresState.filters.search = e.target.value;
        proveedoresState.currentPage = 1;
        loadProveedores();
    });

    document.getElementById('filter-status').addEventListener('change', (e) => {
        proveedoresState.filters.is_active = e.target.value;
        proveedoresState.currentPage = 1;
        loadProveedores();
    });
}

async function loadProveedores() {
    try {
        const params = { page: proveedoresState.currentPage, ...proveedoresState.filters };
        const response = await apiService.getSuppliers(params);
        proveedoresState.proveedores = response.results || response;
        renderTable(proveedoresState.proveedores);
        renderPagination(response.count);
    } catch (error) {
        console.error(error);
        AlertManager.error('Error al cargar proveedores');
        renderTable([]);
    }
}

function renderTable(proveedores) {
    const tbody = document.getElementById('proveedores-tbody');
    
    if (!proveedores || proveedores.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">Sin proveedores</td></tr>`;
        return;
    }
    
    tbody.innerHTML = proveedores.map(p => `
        <tr>
            <td><strong>${p.name}</strong></td>
            <td>${p.rut || 'N/A'}</td>
            <td>${p.contact_person || 'N/A'}</td>
            <td>${p.phone || 'N/A'}</td>
            <td>${p.email}</td>
            <td><span class="badge ${p.is_active ? 'badge-success' : 'badge-danger'}">${p.is_active ? 'Activo' : 'Inactivo'}</span></td>
            <td>
                <button class="btn btn-sm btn-outline" onclick="editSupplier(${p.id})">Editar</button>
                <button class="btn btn-sm btn-danger" onclick="deleteSupplier(${p.id})">Eliminar</button>
            </td>
        </tr>
    `).join('');
}

function renderPagination(total) {
    const totalPages = Math.ceil(total / proveedoresState.pageSize);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    for (let i = 1; i <= totalPages; i++) {
        html += `<a href="#" onclick="goToPage(${i})" class="${i === proveedoresState.currentPage ? 'active' : ''}">${i}</a>`;
    }
    pagination.innerHTML = html;
}

function goToPage(page) {
    event.preventDefault();
    proveedoresState.currentPage = page;
    loadProveedores();
}

async function editSupplier(id) {
    try {
        const supplier = await apiService.getSupplier(id);
        openSupplierModal(supplier);
    } catch (error) {
        AlertManager.error('Error al cargar proveedor');
    }
}

async function deleteSupplier(id) {
    if (!confirm('¿Está seguro?')) return;
    try {
        await apiService.deleteSupplier(id);
        AlertManager.success('Proveedor eliminado');
        await loadProveedores();
    } catch (error) {
        AlertManager.error('Error al eliminar');
    }
}

function openNewSupplierModal() {
    ProveedoresForm.openModal(null);
}

async function editSupplier(id) {
    try {
        const supplier = await apiService.getSupplier(id);
        ProveedoresForm.openModal(supplier);
    } catch (error) {
        AlertManager.error('Error al cargar proveedor');
    }
}
