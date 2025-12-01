/* USUARIOS-MANAGER.JS */

const usuariosState = {
    usuarios: [],
    currentPage: 1,
    pageSize: 20,
    filters: { search: '', role: '' }
};

document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    await loadUsuarios();
});

function setupEventListeners() {
    document.getElementById('btn-new-user').addEventListener('click', openNewUserModal);
    document.getElementById('btn-refresh').addEventListener('click', () => loadUsuarios());

    document.getElementById('search-name').addEventListener('input', (e) => {
        usuariosState.filters.search = e.target.value;
        usuariosState.currentPage = 1;
        loadUsuarios();
    });

    document.getElementById('search-email').addEventListener('input', (e) => {
        usuariosState.filters.email = e.target.value;
        usuariosState.currentPage = 1;
        loadUsuarios();
    });

    document.getElementById('filter-role').addEventListener('change', (e) => {
        usuariosState.filters.role = e.target.value;
        usuariosState.currentPage = 1;
        loadUsuarios();
    });
}

async function loadUsuarios() {
    try {
        const params = { page: usuariosState.currentPage, ...usuariosState.filters };
        const response = await apiService.getUsers(params);
        usuariosState.usuarios = response.results || response;
        renderTable(usuariosState.usuarios);
        renderPagination(response.count);
    } catch (error) {
        console.error(error);
        AlertManager.error('Error al cargar usuarios');
        renderTable([]);
    }
}

function renderTable(usuarios) {
    const tbody = document.getElementById('usuarios-tbody');
    
    if (!usuarios || usuarios.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Sin usuarios</td></tr>`;
        return;
    }
    
    const roleBadges = {
        'admin_cliente': { class: 'role-admin', label: '👨‍💼 Admin Cliente' },
        'gerente': { class: 'role-gerente', label: '📊 Gerente' },
        'vendedor': { class: 'role-vendedor', label: '🛒 Vendedor' },
        'super_admin': { class: 'role-super', label: '🔐 Super Admin' }
    };
    
    tbody.innerHTML = usuarios.map(u => {
        const roleBadge = roleBadges[u.role] || { class: 'role-gerente', label: u.role };
        const statusClass = u.is_active ? 'status-active' : 'status-inactive';
        const statusLabel = u.is_active ? '✓ Activo' : '✕ Inactivo';
        
        return `
            <tr>
                <td><strong>${u.username}</strong></td>
                <td>${u.email}</td>
                <td>${u.first_name} ${u.last_name}</td>
                <td><span class="role-badge ${roleBadge.class}">${roleBadge.label}</span></td>
                <td><span class="user-status ${statusClass}">${statusLabel}</span></td>
                <td>
                    <select class="form-control role-selector" onchange="changeUserRole(${u.id}, this.value, '${u.username}')">
                        <option value="">-- Cambiar rol --</option>
                        <option value="admin_cliente" ${u.role === 'admin_cliente' ? 'selected' : ''}>Admin Cliente</option>
                        <option value="gerente" ${u.role === 'gerente' ? 'selected' : ''}>Gerente</option>
                        <option value="vendedor" ${u.role === 'vendedor' ? 'selected' : ''}>Vendedor</option>
                    </select>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline" onclick="editUser(${u.id})">✏️ Editar</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteUser(${u.id})">🗑️ Eliminar</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
    
    // Inicializar custom selects para los selectores de rol
    setTimeout(() => {
        initializeCustomSelects(document.getElementById('usuarios-tbody'));
    }, 50);
}

async function changeUserRole(userId, newRole, username) {
    if (!newRole) return;
    
    if (!confirm(`¿Cambiar rol de ${username} a ${newRole}?`)) return;
    
    try {
        console.log(`Changing user ${userId} role to ${newRole}`);
        const response = await apiService.changeUserRole(userId, newRole);
        console.log('Response:', response);
        AlertManager.success('Rol actualizado exitosamente');
        await loadUsuarios();
    } catch (error) {
        console.error('Error changing role:', error);
        let errorMsg = 'Error al cambiar el rol';
        
        if (error.response?.data?.message) {
            errorMsg = error.response.data.message;
        } else if (error.response?.data?.detail) {
            errorMsg = error.response.data.detail;
        } else if (error.message) {
            errorMsg = error.message;
        }
        
        AlertManager.error(errorMsg);
        // Recargar para resetear el select
        await loadUsuarios();
    }
}

function renderPagination(total) {
    const totalPages = Math.ceil(total / usuariosState.pageSize);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    for (let i = 1; i <= totalPages; i++) {
        html += `<a href="#" onclick="goToPage(${i})" class="${i === usuariosState.currentPage ? 'active' : ''}">${i}</a>`;
    }
    pagination.innerHTML = html;
}

function goToPage(page) {
    event.preventDefault();
    usuariosState.currentPage = page;
    loadUsuarios();
}

async function editUser(id) {
    try {
        const user = await apiService.getUser(id);
        openUserModal(user);
    } catch (error) {
        AlertManager.error('Error al cargar el usuario');
    }
}

async function deleteUser(id) {
    if (!confirm('¿Está seguro?')) return;
    try {
        await apiService.deleteUser(id);
        AlertManager.success('Usuario eliminado');
        await loadUsuarios();
    } catch (error) {
        AlertManager.error('Error al eliminar');
    }
}

function openNewUserModal() {
    UsuariosForm.openModal(null);
}

function editUser(id) {
    apiService.getUser(id)
        .then(user => UsuariosForm.openModal(user))
        .catch(error => AlertManager.error('Error al cargar el usuario'));
}
