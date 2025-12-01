/* PRODUCTOS-FORM.JS - Formulario modularizado para productos */

class ProductosForm {
    static currentModal = null;
    static currentProductId = null;

    static openModal(product = null) {
        this.currentProductId = product?.id || null;
        const isEdit = !!product;
        
        const modal = new Modal();
        this.currentModal = modal;
        
        modal.setContent(`
            <form id="producto-form" class="form-container">
                <div class="form-group">
                    <label class="form-label">SKU (Código) *</label>
                    <input 
                        type="text" 
                        name="sku" 
                        class="form-control" 
                        value="${product?.sku || ''}" 
                        required 
                        placeholder="ej: PROD-001"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Nombre del Producto *</label>
                    <input 
                        type="text" 
                        name="name" 
                        class="form-control" 
                        value="${product?.name || ''}" 
                        required 
                        placeholder="ej: Laptop HP 15"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Descripción</label>
                    <textarea 
                        name="description" 
                        class="form-control" 
                        rows="3"
                        placeholder="Descripción del producto"
                    >${(product?.description || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</textarea>
                </div>

                <div class="form-group">
                    <label class="form-label">Categoría *</label>
                    <select name="category" class="form-control" required>
                        <option value="">Seleccionar categoría</option>
                        <option value="Electrónica" ${product?.category === 'Electrónica' ? 'selected' : ''}>Electrónica</option>
                        <option value="Accesorios" ${product?.category === 'Accesorios' ? 'selected' : ''}>Accesorios</option>
                        <option value="Periféricos" ${product?.category === 'Periféricos' ? 'selected' : ''}>Periféricos</option>
                    </select>
                </div>

                <div class="form-group">
                    <label class="form-label">Precio de Venta *</label>
                    <input 
                        type="number" 
                        name="price" 
                        class="form-control" 
                        value="${product?.price || ''}" 
                        step="0.01" 
                        min="0"
                        required 
                        placeholder="0.00"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Costo *</label>
                    <input 
                        type="number" 
                        name="cost" 
                        class="form-control" 
                        value="${product?.cost || ''}" 
                        step="0.01" 
                        min="0"
                        required 
                        placeholder="0.00"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Stock ${isEdit ? '- Total: ' + (product?.stock || 0) + ' unidades' : 'Inicial: 0'}</label>
                    <p class="text-muted" style="margin: 0.5rem 0 0 0; font-size: 0.85rem;">
                        ${isEdit ? 'El stock se gestiona desde la sección de Inventario' : 'Se puede ajustar desde la sección de Inventario después de crear'}
                    </p>
                </div>

                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" name="is_active" ${product?.is_active !== false ? 'checked' : ''}>
                        Activo
                    </label>
                </div>
            </form>
        `);
        
        modal.addFooter(`
            <button class="btn btn-secondary" id="btn-form-cancel">Cancelar</button>
            <button class="btn btn-primary" id="btn-form-save">
                ${isEdit ? 'Actualizar' : 'Crear'}
            </button>
        `);
        
        // Agregar event listeners después de que el modal esté visible
        setTimeout(() => {
            const cancelBtn = document.getElementById('btn-form-cancel');
            const saveBtn = document.getElementById('btn-form-save');
            const categorySelect = document.querySelector('#producto-form select[name="category"]');
            
            if (cancelBtn) {
                cancelBtn.addEventListener('click', () => Modal.close());
            }
            
            if (saveBtn) {
                saveBtn.addEventListener('click', () => ProductosForm.save());
            }
            
            // Inicializar custom select para categoría
            if (categorySelect) {
                initializeCustomSelects(document.getElementById('producto-form'));
            }
        }, 100);
        
        modal.show();
    }

    static async save() {
        const form = document.getElementById('producto-form');
        if (!form) return;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        // Validaciones
        if (!data.sku?.trim()) {
            AlertManager.error('SKU es requerido');
            return;
        }
        if (!data.name?.trim()) {
            AlertManager.error('Nombre es requerido');
            return;
        }
        if (!data.category) {
            AlertManager.error('Categoría es requerida');
            return;
        }
        if (!data.price || parseFloat(data.price) <= 0) {
            AlertManager.error('Precio debe ser mayor a 0');
            return;
        }
        if (!data.cost || parseFloat(data.cost) < 0) {
            AlertManager.error('Costo es requerido');
            return;
        }

        // Convertir valores
        data.is_active = formData.has('is_active');
        data.price = parseFloat(data.price);
        data.cost = parseFloat(data.cost);

        try {
            const id = this.currentProductId;
            if (id) {
                console.log(`Actualizando producto ${id}:`, data);
                await apiService.updateProduct(id, data);
                AlertManager.success('Producto actualizado correctamente');
            } else {
                console.log('Creando nuevo producto:', data);
                await apiService.createProduct(data);
                AlertManager.success('Producto creado correctamente');
            }
            Modal.close();
            if (typeof loadProductos === 'function') {
                await loadProductos();
            }
        } catch (error) {
            console.error('Error completo:', error);
            console.error('Response data:', error.response?.data);
            const errorMsg = error.response?.data?.detail || 
                           error.response?.data?.non_field_errors?.[0] ||
                           error.message || 
                           'Error desconocido';
            AlertManager.error('Error: ' + errorMsg);
        }
    }
}
