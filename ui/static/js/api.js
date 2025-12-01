// API Service - Comunicación con el backend
class APIService {
  constructor() {
    this.baseURL = '/api';
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
    this.csrfToken = this.getCsrfToken();
  }

  // Obtener CSRF token del DOM
  getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Headers por defecto
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      ...(this.accessToken && { 'Authorization': `Bearer ${this.accessToken}` }),
      ...(this.csrfToken && { 'X-CSRFToken': this.csrfToken })
    };
    return headers;
  }

  // Métodos HTTP genéricos
  async request(endpoint, method = 'GET', data = null) {
    try {
      const options = {
        method,
        headers: this.getHeaders(),
      };

      if (data) {
        options.body = JSON.stringify(data);
      }

      const response = await fetch(`${this.baseURL}${endpoint}`, options);

      if (!response.ok) {
        if (response.status === 401) {
          // Token expirado
          await this.refreshAccessToken();
          return this.request(endpoint, method, data);
        }
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`HTTP Error: ${response.status} - ${JSON.stringify(errorData)}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  async get(endpoint) {
    return this.request(endpoint, 'GET');
  }

  async post(endpoint, data) {
    return this.request(endpoint, 'POST', data);
  }

  async put(endpoint, data) {
    return this.request(endpoint, 'PUT', data);
  }

  async patch(endpoint, data) {
    return this.request(endpoint, 'PATCH', data);
  }

  async delete(endpoint) {
    return this.request(endpoint, 'DELETE');
  }

  // Autenticación
  async login(username, password) {
    const response = await this.request('/users/login/', 'POST', { username, password });
    
    this.accessToken = response.access;
    this.refreshToken = response.refresh;
    
    localStorage.setItem('access_token', response.access);
    localStorage.setItem('refresh_token', response.refresh);
    localStorage.setItem('user', JSON.stringify(response.user));
    
    return response;
  }

  async register(userData) {
    return this.request('/users/', 'POST', userData);
  }

  async logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    this.accessToken = null;
    this.refreshToken = null;
  }

  async refreshAccessToken() {
    try {
      const response = await fetch(`${this.baseURL}/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: this.refreshToken })
      });

      if (response.ok) {
        const data = await response.json();
        this.accessToken = data.access;
        localStorage.setItem('access_token', data.access);
      } else {
        this.logout();
        window.location.href = '/login/';
      }
    } catch (error) {
      this.logout();
      window.location.href = '/login/';
    }
  }

  async getCurrentUser() {
    return this.request('/users/me/');
  }

  // Usuarios
  async getUsers(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/users/?${query}`);
  }

  async getUser(id) {
    return this.request(`/users/${id}/`);
  }

  async createUser(data) {
    return this.request('/users/', 'POST', data);
  }

  async updateUser(id, data) {
    return this.request(`/users/${id}/`, 'PUT', data);
  }

  async deleteUser(id) {
    return this.request(`/users/${id}/`, 'DELETE');
  }

  async changeUserRole(id, role) {
    return this.request(`/users/${id}/change-role/`, 'POST', { role });
  }

  // Productos
  async getProducts(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/products/?${query}`);
  }

  async getProduct(id) {
    return this.request(`/products/${id}/`);
  }

  async createProduct(data) {
    return this.request('/products/', 'POST', data);
  }

  async updateProduct(id, data) {
    return this.request(`/products/${id}/`, 'PUT', data);
  }

  async deleteProduct(id) {
    return this.request(`/products/${id}/`, 'DELETE');
  }

  async getActiveProducts() {
    return this.request('/products/active/');
  }

  // Sucursales
  async getBranches(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/branches/?${query}`);
  }

  async getBranch(id) {
    return this.request(`/branches/${id}/`);
  }

  async createBranch(data) {
    return this.request('/branches/', 'POST', data);
  }

  async updateBranch(id, data) {
    return this.request(`/branches/${id}/`, 'PUT', data);
  }

  // Inventario
  async getInventory(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/inventory/?${query}`);
  }

  async updateInventory(id, data) {
    return this.request(`/inventory/${id}/`, 'PUT', data);
  }

  async createInventoryMovement(data) {
    return this.request('/inventory-movements/', 'POST', data);
  }

  async syncInventory() {
    return this.request('/inventory/sync_inventory/', 'POST', {});
  }

  // Ventas
  async getSales(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/sales/?${query}`);
  }

  async getSale(id) {
    return this.request(`/sales/${id}/`);
  }

  async createSale(data) {
    return this.request('/sales/', 'POST', data);
  }

  // Órdenes
  async getOrders(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/orders/?${query}`);
  }

  async getOrder(id) {
    return this.request(`/orders/${id}/`);
  }

  async createOrder(data) {
    return this.request('/orders/', 'POST', data);
  }

  // Proveedores
  async getSuppliers(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/suppliers/?${query}`);
  }

  async getSupplier(id) {
    return this.request(`/suppliers/${id}/`);
  }

  async createSupplier(data) {
    return this.request('/suppliers/', 'POST', data);
  }

  // Compras
  async getPurchases(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/purchases/?${query}`);
  }

  async getPurchase(id) {
    return this.request(`/purchases/${id}/`);
  }

  async createPurchase(data) {
    return this.request('/purchases/', 'POST', data);
  }
}

// Instancia global
const apiService = new APIService();
