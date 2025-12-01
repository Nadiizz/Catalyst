/* SUCURSALES-MANAGER.JS */

const sucursalesState = {
    sucursales: [],
    currentPage: 1,
    pageSize: 20,
    filters: { search: '' }
};

document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    await loadSucursales();
});

function setupEventListeners() {
    document.getElementById('btn-new-branch').addEventListener('click', openNewBranchModal);
    document.getElementById('btn-refresh').addEventListener('click', () => loadSucursales());

    document.getElementById('search-name').addEventListener('input', (e) => {
        sucursalesState.filters.search = e.target.value;
        sucursalesState.currentPage = 1;
        loadSucursales();
    });

    document.getElementById('filter-status').addEventListener('change', (e) => {
        sucursalesState.filters.is_active = e.target.value;
        sucursalesState.currentPage = 1;
        loadSucursales();
    });
}

async function loadSucursales() {
    try {
        const params = { page: sucursalesState.currentPage, ...sucursalesState.filters };
        const response = await apiService.getBranches(params);
        sucursalesState.sucursales = response.results || response;
        renderTable(sucursalesState.sucursales);
        renderPagination(response.count);
    } catch (error) {
        console.error(error);
        AlertManager.error('Error al cargar sucursales');
        renderTable([]);
    }
}

function renderTable(sucursales) {
    const tbody = document.getElementById('sucursales-tbody');
    
    if (!sucursales || sucursales.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Sin sucursales</td></tr>`;
        return;
    }
    
    tbody.innerHTML = sucursales.map(s => {
        // Extraer ciudad de la dirección o mostrar N/A
        const ciudad = s.address ? s.address.split(',')[s.address.split(',').length - 1]?.trim() || 'N/A' : 'N/A';
        
        return `
        <tr>
            <td><strong>${s.name}</strong></td>
            <td>${s.address || 'N/A'}</td>
            <td>${ciudad}</td>
            <td>${s.phone || 'N/A'}</td>
            <td>${s.manager_name || 'Sin asignar'}</td>
            <td><span class="badge ${s.is_active ? 'badge-success' : 'badge-danger'}">${s.is_active ? 'Activa' : 'Inactiva'}</span></td>
            <td>
                <button class="btn btn-sm btn-outline" onclick="editBranch(${s.id})">Editar</button>
                <button class="btn btn-sm btn-danger" onclick="deleteBranch(${s.id})">Eliminar</button>
            </td>
        </tr>
    `}).join('');
}

function renderPagination(total) {
    const totalPages = Math.ceil(total / sucursalesState.pageSize);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    for (let i = 1; i <= totalPages; i++) {
        html += `<a href="#" onclick="goToPage(${i})" class="${i === sucursalesState.currentPage ? 'active' : ''}">${i}</a>`;
    }
    pagination.innerHTML = html;
}

function goToPage(page) {
    event.preventDefault();
    sucursalesState.currentPage = page;
    loadSucursales();
}

async function editBranch(id) {
    try {
        const branch = await apiService.getBranch(id);
        openBranchModal(branch);
    } catch (error) {
        AlertManager.error('Error al cargar sucursal');
    }
}

async function deleteBranch(id) {
    if (!confirm('¿Está seguro?')) return;
    try {
        await apiService.deleteBranch(id);
        AlertManager.success('Sucursal eliminada');
        await loadSucursales();
    } catch (error) {
        AlertManager.error('Error al eliminar');
    }
}

function openNewBranchModal() {
    SucursalesForm.openModal(null);
}

async function editBranch(id) {
    try {
        const branch = await apiService.getBranch(id);
        SucursalesForm.openModal(branch);
    } catch (error) {
        AlertManager.error('Error al cargar sucursal');
    }
}
