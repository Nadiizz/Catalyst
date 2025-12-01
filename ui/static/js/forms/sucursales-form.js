/* SUCURSALES-FORM.JS - Formulario modularizado para sucursales */

class SucursalesForm {
    static openModal(branch = null) {
        const modal = new Modal();
        const isEdit = !!branch;
        
        modal.setContent(`
            <form id="sucursal-form" class="form-container">
                <div class="form-group">
                    <label class="form-label">Nombre de la Sucursal *</label>
                    <input 
                        type="text" 
                        name="name" 
                        class="form-control" 
                        value="${branch?.name || ''}" 
                        required 
                        placeholder="ej: Sucursal Centro"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Dirección *</label>
                    <textarea 
                        name="address" 
                        class="form-control" 
                        rows="2"
                        required
                        placeholder="Dirección completa de la sucursal"
                    >${branch?.address || ''}</textarea>
                </div>

                <div class="form-group">
                    <label class="form-label">Teléfono</label>
                    <input 
                        type="tel" 
                        name="phone" 
                        class="form-control" 
                        value="${branch?.phone || ''}" 
                        placeholder="ej: +56 9 1234 5678"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Email</label>
                    <input 
                        type="email" 
                        name="email" 
                        class="form-control" 
                        value="${branch?.email || ''}" 
                        placeholder="ej: sucursal@empresa.com"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Gerente (Opcional)</label>
                    <select name="manager" id="manager-select" class="form-control">
                        <option value="">Sin gerente asignado</option>
                    </select>
                </div>

                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" name="is_active" ${branch?.is_active !== false ? 'checked' : ''}>
                        Activa
                    </label>
                </div>
            </form>
        `);
        
        modal.addFooter(`
            <button class="btn btn-secondary" onclick="Modal.close()">Cancelar</button>
            <button class="btn btn-primary" onclick="SucursalesForm.save(${branch?.id || null})">
                ${isEdit ? 'Actualizar' : 'Crear'}
            </button>
        `);
        
        modal.show();
        
        // Cargar gerentes disponibles después de que el modal esté visible
        setTimeout(() => {
            SucursalesForm.loadManagers(branch?.manager);
        }, 150);
    }

    static async loadManagers(selectedManagerId = null) {
        try {
            const managerSelect = document.getElementById('manager-select');
            if (!managerSelect) {
                console.warn('manager-select not found');
                return;
            }

            console.log('Loading managers with role gerente...');
            // Obtener usuarios con rol de gerente
            const response = await apiService.getUsers({ role: 'gerente' });
            console.log('Managers response:', response);
            
            const users = response.results || response;
            console.log('Managers found:', users.length);
            
            // Limpiar opciones excepto la primera
            managerSelect.innerHTML = '<option value="">Sin gerente asignado</option>';
            
            // Agregar usuarios con rol gerente
            if (Array.isArray(users) && users.length > 0) {
                users.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.id;
                    option.textContent = (user.first_name || '') + ' ' + (user.last_name || '');
                    if (selectedManagerId === user.id) {
                        option.selected = true;
                    }
                    managerSelect.appendChild(option);
                });
            } else {
                console.warn('No managers found');
            }

            // Inicializar custom select
            initializeCustomSelects(document.getElementById('sucursal-form'));
        } catch (error) {
            console.error('Error loading managers:', error);
            AlertManager.error('Error al cargar gerentes: ' + error.message);
        }
    }

    static async save(id) {
        const form = document.getElementById('sucursal-form');
        if (!form) return;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        // Validaciones
        if (!data.name?.trim()) {
            AlertManager.error('Nombre es requerido');
            return;
        }
        if (!data.address?.trim()) {
            AlertManager.error('Dirección es requerida');
            return;
        }

        data.is_active = formData.has('is_active');
        
        // Convertir manager a número si está vacío
        if (!data.manager) {
            data.manager = null;
        } else {
            data.manager = parseInt(data.manager);
        }

        try {
            if (id) {
                await apiService.updateBranch(id, data);
                AlertManager.success('Sucursal actualizada correctamente');
            } else {
                await apiService.createBranch(data);
                AlertManager.success('Sucursal creada correctamente');
            }
            Modal.close();
            if (typeof loadSucursales === 'function') {
                await loadSucursales();
            }
        } catch (error) {
            console.error('Error:', error);
            const errorMsg = error.response?.data?.detail || error.message || 'Error desconocido';
            AlertManager.error('Error: ' + errorMsg);
        }
    }
}
