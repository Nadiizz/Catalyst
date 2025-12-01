/* USUARIOS-FORM.JS - Formulario modularizado para usuarios */

class UsuariosForm {
    static openModal(user = null) {
        const modal = new Modal();
        const isEdit = !!user;
        
        modal.setContent(`
            <form id="usuario-form" class="form-container">
                <div class="form-group">
                    <label class="form-label">Username</label>
                    <input 
                        type="text" 
                        name="username" 
                        class="form-control" 
                        value="${user?.username || ''}" 
                        ${isEdit ? 'readonly' : 'required'} 
                        placeholder="ej: juan.perez"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Email *</label>
                    <input 
                        type="email" 
                        name="email" 
                        class="form-control" 
                        value="${user?.email || ''}" 
                        required 
                        placeholder="ej: juan@empresa.com"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Nombre *</label>
                    <input 
                        type="text" 
                        name="first_name" 
                        class="form-control" 
                        value="${user?.first_name || ''}" 
                        required 
                        placeholder="Nombre"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">Apellido</label>
                    <input 
                        type="text" 
                        name="last_name" 
                        class="form-control" 
                        value="${user?.last_name || ''}" 
                        placeholder="Apellido"
                    >
                </div>

                ${!isEdit ? `
                    <div class="form-group">
                        <label class="form-label">Contraseña *</label>
                        <input 
                            type="password" 
                            name="password" 
                            class="form-control" 
                            required 
                            minlength="8"
                            placeholder="Mínimo 8 caracteres"
                        >
                    </div>

                    <div class="form-group">
                        <label class="form-label">Confirmar Contraseña *</label>
                        <input 
                            type="password" 
                            name="password_confirm" 
                            class="form-control" 
                            required 
                            minlength="8"
                            placeholder="Repite la contraseña"
                        >
                    </div>
                ` : ''}

                <div class="form-group">
                    <label class="form-label">Rol *</label>
                    <select name="role" class="form-control" required>
                        <option value="">Seleccionar rol</option>
                        <option value="admin_cliente" ${user?.role === 'admin_cliente' ? 'selected' : ''}>Admin Cliente</option>
                        <option value="gerente" ${user?.role === 'gerente' ? 'selected' : ''}>Gerente</option>
                        <option value="vendedor" ${user?.role === 'vendedor' ? 'selected' : ''}>Vendedor</option>
                    </select>
                </div>

                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" name="is_active" ${user?.is_active !== false ? 'checked' : ''}>
                        Activo
                    </label>
                </div>

                <p class="text-muted" style="margin: 1rem 0 0 0; font-size: 0.85rem;">
                    ${user?.role === 'gerente' ? '💡 La sucursal de este gerente se asigna desde la sección de Sucursales' : ''}
                </p>
            </form>
        `);
        
        modal.addFooter(`
            <button class="btn btn-secondary" onclick="Modal.close()">Cancelar</button>
            <button class="btn btn-primary" onclick="UsuariosForm.save(${user?.id || null})">
                ${isEdit ? 'Actualizar' : 'Crear'}
            </button>
        `);
        
        modal.show();
        
        // Inicializar custom selects
        setTimeout(() => {
            initializeCustomSelects(document.getElementById('usuario-form'));
        }, 100);
    }

    static async save(id) {
        const form = document.getElementById('usuario-form');
        if (!form) return;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        // Validaciones
        if (!data.username?.trim()) {
            AlertManager.error('Username es requerido');
            return;
        }
        if (!data.email?.trim()) {
            AlertManager.error('Email es requerido');
            return;
        }
        if (!data.first_name?.trim()) {
            AlertManager.error('Nombre es requerido');
            return;
        }
        if (!data.role) {
            AlertManager.error('Rol es requerido');
            return;
        }

        // Si es creación, validar contraseña
        if (!id) {
            if (!data.password) {
                AlertManager.error('Contraseña es requerida');
                return;
            }
            if (!data.password_confirm) {
                AlertManager.error('Confirmación de contraseña es requerida');
                return;
            }
            if (data.password.length < 8) {
                AlertManager.error('Contraseña debe tener mínimo 8 caracteres');
                return;
            }
            if (data.password !== data.password_confirm) {
                AlertManager.error('Las contraseñas no coinciden');
                return;
            }
        }

        // Convertir booleano
        data.is_active = formData.has('is_active');

        try {
            if (id) {
                delete data.password;
                delete data.password_confirm;
                await apiService.updateUser(id, data);
                AlertManager.success('Usuario actualizado correctamente');
            } else {
                await apiService.createUser(data);
                AlertManager.success('Usuario creado correctamente');
            }
            Modal.close();
            // Recargar tabla
            if (typeof loadUsuarios === 'function') {
                await loadUsuarios();
            }
        } catch (error) {
            console.error('Error:', error);
            AlertManager.error('Error al guardar: ' + (error.message || 'Error desconocido'));
        }
    }
}
