/* PRODUCTOS-MANAGER.JS */

const productosState = {
    productos: [],
    currentPage: 1,
    pageSize: 20,
    filters: { search: '', status: '' }
};

document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    await loadProductos();
});

function setupEventListeners() {
    document.getElementById('btn-new-product').addEventListener('click', openNewProductModal);
    document.getElementById('btn-refresh').addEventListener('click', () => loadProductos());

    document.getElementById('search-name').addEventListener('input', (e) => {
        productosState.filters.search = e.target.value;
        productosState.currentPage = 1;
        loadProductos();
    });

    document.getElementById('filter-status').addEventListener('change', (e) => {
        productosState.filters.status = e.target.value;
        productosState.currentPage = 1;
        loadProductos();
    });
    
    // Usar event delegation para los botones de la tabla
    const tbody = document.getElementById('productos-tbody');
    tbody.addEventListener('click', async (e) => {
        if (e.target.classList.contains('btn-edit')) {
            const id = parseInt(e.target.getAttribute('data-id'));
            await editProduct(id);
        } else if (e.target.classList.contains('btn-delete')) {
            const id = parseInt(e.target.getAttribute('data-id'));
            await deleteProduct(id);
        }
    });
}

async function loadProductos() {
    try {
        const params = { page: productosState.currentPage, ...productosState.filters };
        const response = await apiService.getProducts(params);
        productosState.productos = response.results || response;
        renderTable(productosState.productos);
        renderPagination(response.count);
    } catch (error) {
        console.error(error);
        AlertManager.error('Error al cargar productos');
        renderTable([]);
    }
}

function renderTable(productos) {
    const tbody = document.getElementById('productos-tbody');
    
    if (!productos || productos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">Sin productos</td></tr>`;
        return;
    }
    
    tbody.innerHTML = productos.map(p => `
        <tr data-product-id="${p.id}">
            <td>${p.sku || 'N/A'}</td>
            <td>${p.name}</td>
            <td>${formatters.currency(p.price || 0)}</td>
            <td><span class="badge ${(p.stock || 0) < 10 ? 'badge-warning' : 'badge-success'}">${p.stock || 0}</span></td>
            <td><span class="badge ${p.is_active ? 'badge-success' : 'badge-danger'}">${p.is_active ? 'Activo' : 'Inactivo'}</span></td>
            <td>
                <div class="table-actions">
                    <button class="btn btn-sm btn-outline btn-edit" data-id="${p.id}">Editar</button>
                    <button class="btn btn-sm btn-danger btn-delete" data-id="${p.id}">Eliminar</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function renderPagination(total) {
    const totalPages = Math.ceil(total / productosState.pageSize);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    for (let i = 1; i <= totalPages; i++) {
        html += `<a href="#" onclick="goToPage(${i})" class="${i === productosState.currentPage ? 'active' : ''}">${i}</a>`;
    }
    pagination.innerHTML = html;
}

function goToPage(page) {
    event.preventDefault();
    productosState.currentPage = page;
    loadProductos();
}

async function editProduct(id) {
    try {
        const product = await apiService.getProduct(id);
        ProductosForm.openModal(product);
    } catch (error) {
        AlertManager.error('Error al cargar el producto');
    }
}

async function deleteProduct(id) {
    console.log('Eliminando producto:', id);
    if (!confirm('¿Está seguro de que desea eliminar este producto? Esta acción no se puede deshacer.')) {
        console.log('Eliminación cancelada por el usuario');
        return;
    }
    
    try {
        console.log('Llamando API para eliminar...');
        const result = await apiService.deleteProduct(id);
        console.log('Resultado de eliminación:', result);
        
        AlertManager.success('Producto eliminado correctamente');
        
        // Dar un pequeño tiempo para que se vea el mensaje
        await new Promise(resolve => setTimeout(resolve, 500));
        
        console.log('Recargando tabla...');
        await loadProductos();
    } catch (error) {
        console.error('Error completo al eliminar:', error);
        console.error('Status:', error.response?.status);
        console.error('Data:', error.response?.data);
        
        const errorMsg = error.response?.data?.detail || 
                        error.response?.data?.non_field_errors?.[0] ||
                        error.message || 
                        'Error desconocido al eliminar';
        AlertManager.error('Error: ' + errorMsg);
    }
}

function openNewProductModal() {
    ProductosForm.openModal(null);
}
