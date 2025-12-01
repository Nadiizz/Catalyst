/* INVENTARIO-MANAGER.JS */

const inventarioState = {
    items: [],
    currentPage: 1,
    pageSize: 20,
    filters: { search: '', status: '' }
};

document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    await loadInventario();
});

function setupEventListeners() {
    document.getElementById('btn-adjust-stock').addEventListener('click', openAdjustStockModal);
    document.getElementById('btn-refresh').addEventListener('click', () => loadInventario());

    document.getElementById('search-product').addEventListener('input', (e) => {
        inventarioState.filters.search = e.target.value;
        inventarioState.currentPage = 1;
        loadInventario();
    });

    document.getElementById('filter-status').addEventListener('change', (e) => {
        inventarioState.filters.status = e.target.value;
        inventarioState.currentPage = 1;
        loadInventario();
    });
    
    // Event delegation para botones Ajustar
    const tbody = document.getElementById('inventario-tbody');
    if (tbody) {
        tbody.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-adjust')) {
                const id = parseInt(e.target.getAttribute('data-id'));
                adjustStock(id);
            }
        });
    }
}

async function loadInventario() {
    try {
        const params = { page: inventarioState.currentPage, ...inventarioState.filters };
        const response = await apiService.getInventory(params);
        inventarioState.items = response.results || response;
        renderTable(inventarioState.items);
        renderPagination(response.count);
    } catch (error) {
        console.error('Error loading inventory:', error);
        AlertManager.error('Error al cargar inventario');
        renderTable([]);
    }
}

function renderTable(items) {
    const tbody = document.getElementById('inventario-tbody');
    
    if (!items || items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted">Sin inventario</td></tr>`;
        return;
    }
    
    tbody.innerHTML = items.map(i => `
        <tr data-inventory-id="${i.id}">
            <td><strong>${i.product_name}</strong></td>
            <td><code>${i.product_code}</code></td>
            <td>${i.branch_name}</td>
            <td>
                <span class="badge ${getStockBadge(i.stock, i.reorder_point)}">
                    ${i.stock} unidades
                </span>
            </td>
            <td>${i.reorder_point}</td>
            <td>${getStockStatus(i.stock, i.reorder_point)}</td>
            <td>${formatters.date(i.updated_at)}</td>
            <td>
                <button class="btn btn-sm btn-outline btn-adjust" data-id="${i.id}">Ajustar</button>
            </td>
        </tr>
    `).join('');
}

function getStockBadge(stock, reorder) {
    if (stock === 0) return 'badge-danger';
    if (stock < reorder) return 'badge-warning';
    return 'badge-success';
}

function getStockStatus(stock, reorder) {
    if (stock === 0) return '<span class="badge badge-danger">Agotado</span>';
    if (stock < reorder) return '<span class="badge badge-warning">Stock Bajo</span>';
    return '<span class="badge badge-success">Normal</span>';
}

function renderPagination(total) {
    const totalPages = Math.ceil(total / inventarioState.pageSize);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    for (let i = 1; i <= totalPages; i++) {
        html += `<a href="#" onclick="goToPage(${i})" class="${i === inventarioState.currentPage ? 'active' : ''}">${i}</a>`;
    }
    pagination.innerHTML = html;
}

function goToPage(page) {
    event.preventDefault();
    inventarioState.currentPage = page;
    loadInventario();
}

function openAdjustStockModal() {
    const modal = new Modal();
    const currentInventory = inventarioState.items[0];
    
    modal.setContent(`
        <form id="adjust-form" class="form-container">
            <div class="form-group">
                <label class="form-label">Inventario *</label>
                <select name="inventory_id" class="form-control" required>
                    <option value="">Seleccionar inventario...</option>
                    ${inventarioState.items.map(i => 
                        `<option value="${i.id}">
                            ${i.product_name} - ${i.branch_name} (Stock actual: ${i.stock})
                        </option>`
                    ).join('')}
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">Tipo de Movimiento *</label>
                <select name="movement_type" class="form-control" required>
                    <option value="">Seleccionar tipo...</option>
                    <option value="entrada">Entrada (Compra/Reabastecimiento)</option>
                    <option value="salida">Salida (Venta/Descuento)</option>
                    <option value="ajuste">Ajuste de Inventario</option>
                    <option value="devolucion">Devolución</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">Cantidad *</label>
                <input 
                    type="number" 
                    name="quantity" 
                    class="form-control" 
                    placeholder="Cantidad a registrar" 
                    required
                    min="1"
                >
            </div>
            
            <div class="form-group">
                <label class="form-label">Referencia</label>
                <input 
                    type="text" 
                    name="reference" 
                    class="form-control" 
                    placeholder="Nº de compra, venta, etc. (opcional)"
                >
            </div>
            
            <div class="form-group">
                <label class="form-label">Notas</label>
                <textarea 
                    name="notes" 
                    class="form-control" 
                    rows="3"
                    placeholder="Notas adicionales sobre el movimiento (opcional)"
                ></textarea>
            </div>
        </form>
    `);
    
    modal.addFooter(`
        <button class="btn btn-secondary" id="btn-cancel-adjust">Cancelar</button>
        <button class="btn btn-primary" id="btn-save-adjust">Registrar Movimiento</button>
    `);
    
    // Agregar listeners después de un pequeño delay para asegurar que el modal esté visible
    setTimeout(() => {
        const cancelBtn = document.getElementById('btn-cancel-adjust');
        const saveBtn = document.getElementById('btn-save-adjust');
        
        if (cancelBtn) cancelBtn.addEventListener('click', () => Modal.close());
        if (saveBtn) saveBtn.addEventListener('click', saveAdjustment);
        
        // Inicializar custom selects
        initializeCustomSelects(document.getElementById('adjust-form'));
    }, 100);
    
    modal.show();
}

async function adjustStock(inventoryId) {
    try {
        // Obtener información del inventario
        const inventory = inventarioState.items.find(i => i.id === inventoryId);
        if (!inventory) {
            AlertManager.error('Inventario no encontrado');
            return;
        }
        
        const modal = new Modal();
        modal.setContent(`
            <form id="adjust-single-form" class="form-container">
                <div class="form-group">
                    <label class="form-label">Producto</label>
                    <input type="text" class="form-control" value="${inventory.product_name}" disabled>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Sucursal</label>
                    <input type="text" class="form-control" value="${inventory.branch_name}" disabled>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Stock Actual</label>
                    <input type="text" class="form-control" value="${inventory.stock} unidades" disabled>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Tipo de Movimiento *</label>
                    <select name="movement_type" class="form-control" required>
                        <option value="">Seleccionar tipo...</option>
                        <option value="entrada">Entrada (Compra/Reabastecimiento)</option>
                        <option value="salida">Salida (Venta/Descuento)</option>
                        <option value="ajuste">Ajuste de Inventario</option>
                        <option value="devolucion">Devolución</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Cantidad *</label>
                    <input 
                        type="number" 
                        name="quantity" 
                        class="form-control" 
                        placeholder="Cantidad a registrar" 
                        required
                        min="1"
                    >
                </div>
                
                <div class="form-group">
                    <label class="form-label">Referencia</label>
                    <input 
                        type="text" 
                        name="reference" 
                        class="form-control" 
                        placeholder="Nº de compra, venta, etc. (opcional)"
                    >
                </div>
                
                <div class="form-group">
                    <label class="form-label">Notas</label>
                    <textarea 
                        name="notes" 
                        class="form-control" 
                        rows="3"
                        placeholder="Notas adicionales (opcional)"
                    ></textarea>
                </div>
            </form>
        `);
        
        modal.addFooter(`
            <button class="btn btn-secondary" id="btn-cancel-single">Cancelar</button>
            <button class="btn btn-primary" id="btn-save-single">Registrar</button>
        `);
        
        setTimeout(() => {
            const cancelBtn = document.getElementById('btn-cancel-single');
            const saveBtn = document.getElementById('btn-save-single');
            
            if (cancelBtn) cancelBtn.addEventListener('click', () => Modal.close());
            if (saveBtn) saveBtn.addEventListener('click', () => saveSingleAdjustment(inventoryId));
            
            // Inicializar custom selects
            initializeCustomSelects(document.getElementById('adjust-single-form'));
        }, 100);
        
        modal.show();
    } catch (error) {
        console.error('Error:', error);
        AlertManager.error('Error al abrir formulario de ajuste');
    }
}

async function saveAdjustment() {
    const form = document.getElementById('adjust-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Validación
    if (!data.inventory_id) {
        AlertManager.error('Error: Debe seleccionar un inventario');
        return;
    }
    if (!data.movement_type) {
        AlertManager.error('Error: Debe seleccionar tipo de movimiento');
        return;
    }
    if (!data.quantity || parseInt(data.quantity) === 0) {
        AlertManager.error('Error: Cantidad debe ser diferente de 0');
        return;
    }
    
    try {
        const inventoryId = parseInt(data.inventory_id);
        const movementData = {
            inventory: inventoryId,
            movement_type: data.movement_type,
            quantity: parseInt(data.quantity),
            reference: data.reference || '',
            notes: data.notes || ''
        };
        
        console.log('Registrando movimiento:', movementData);
        await apiService.createInventoryMovement(movementData);
        
        AlertManager.success('Movimiento registrado correctamente');
        Modal.close();
        await loadInventario();
    } catch (error) {
        console.error('Error saving adjustment:', error);
        let errorMsg = 'Error al registrar movimiento';
        if (error.response?.data?.detail) {
            errorMsg = error.response.data.detail;
        } else if (error.response?.data?.non_field_errors?.[0]) {
            errorMsg = error.response.data.non_field_errors[0];
        }
        AlertManager.error(errorMsg);
    }
}

async function saveSingleAdjustment(inventoryId) {
    const form = document.getElementById('adjust-single-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Validación
    if (!data.movement_type) {
        AlertManager.error('Error: Debe seleccionar tipo de movimiento');
        return;
    }
    if (!data.quantity || parseInt(data.quantity) === 0) {
        AlertManager.error('Error: Cantidad debe ser diferente de 0');
        return;
    }
    
    try {
        const movementData = {
            inventory: inventoryId,
            movement_type: data.movement_type,
            quantity: parseInt(data.quantity),
            reference: data.reference || '',
            notes: data.notes || ''
        };
        
        console.log('Registrando movimiento:', movementData);
        await apiService.createInventoryMovement(movementData);
        
        AlertManager.success('Movimiento registrado correctamente');
        Modal.close();
        await loadInventario();
    } catch (error) {
        console.error('Error saving adjustment:', error);
        let errorMsg = 'Error al registrar movimiento';
        if (error.response?.data?.detail) {
            errorMsg = error.response.data.detail;
        } else if (error.response?.data?.non_field_errors?.[0]) {
            errorMsg = error.response.data.non_field_errors[0];
        }
        AlertManager.error(errorMsg);
    }
}
