/* PROVEEDORES-FORM.JS - Formulario modularizado para proveedores */

class ProveedoresForm {
    static openModal(supplier = null) {
        const modal = new Modal();
        const isEdit = !!supplier;
        
        modal.setContent(`
            <form id="proveedor-form" class="form-container">
                <div class="form-group">
                    <label class="form-label">Nombre del Proveedor *</label>
                    <input 
                        type="text" 
                        name="name" 
                        class="form-control" 
                        value="${supplier?.name || ''}" 
                        required 
                        placeholder="ej: Distribuidora ABC"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">RUT *</label>
                    <input 
                        type="text" 
                        name="rut" 
                        class="form-control" 
                        value="${supplier?.rut || ''}" 
                        required 
                        placeholder="ej: 12.345.678-9"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Email *</label>
                    <input 
                        type="email" 
                        name="email" 
                        class="form-control" 
                        value="${supplier?.email || ''}" 
                        required 
                        placeholder="contacto@proveedor.com"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Teléfono</label>
                    <input 
                        type="tel" 
                        name="phone" 
                        class="form-control" 
                        value="${supplier?.phone || ''}" 
                        placeholder="+56 9 1234 5678"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Dirección</label>
                    <textarea 
                        name="address" 
                        class="form-control" 
                        rows="2"
                        placeholder="Dirección del proveedor"
                    >${supplier?.address || ''}</textarea>
                </div>

                <div class="form-group">
                    <label class="form-label">Persona de Contacto</label>
                    <input 
                        type="text" 
                        name="contact_person" 
                        class="form-control" 
                        value="${supplier?.contact_person || ''}" 
                        placeholder="Nombre del contacto"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Términos de Pago</label>
                    <input 
                        type="text" 
                        name="payment_terms" 
                        class="form-control" 
                        value="${supplier?.payment_terms || ''}" 
                        placeholder="ej: 30 días"
                    >
                </div>

                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" name="is_active" ${supplier?.is_active !== false ? 'checked' : ''}>
                        Activo
                    </label>
                </div>
            </form>
        `);
        
        modal.addFooter(`
            <button class="btn btn-secondary" onclick="Modal.close()">Cancelar</button>
            <button class="btn btn-primary" onclick="ProveedoresForm.save(${supplier?.id || null})">
                ${isEdit ? 'Actualizar' : 'Crear'}
            </button>
        `);
        
        modal.show();
    }

    static async save(id) {
        const form = document.getElementById('proveedor-form');
        if (!form) return;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        // Validaciones
        if (!data.name?.trim()) {
            AlertManager.error('Nombre es requerido');
            return;
        }
        if (!data.rut?.trim()) {
            AlertManager.error('RUT es requerido');
            return;
        }
        if (!data.email?.trim()) {
            AlertManager.error('Email es requerido');
            return;
        }

        data.is_active = formData.has('is_active');

        try {
            if (id) {
                await apiService.updateSupplier(id, data);
                AlertManager.success('Proveedor actualizado correctamente');
            } else {
                await apiService.createSupplier(data);
                AlertManager.success('Proveedor creado correctamente');
            }
            Modal.close();
            if (typeof loadProveedores === 'function') {
                await loadProveedores();
            }
        } catch (error) {
            console.error('Error:', error);
            const errorMsg = error.response?.data?.detail || error.message || 'Error desconocido';
            AlertManager.error('Error: ' + errorMsg);
        }
    }
}
