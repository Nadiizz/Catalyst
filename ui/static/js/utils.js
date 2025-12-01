// Utilidades generales

// Alertas
class AlertManager {
  static show(message, type = 'info', duration = 5000) {
    // Crear elemento de alerta
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 15px 20px;
      border-radius: 5px;
      z-index: 9999;
      animation: slideIn 0.3s ease-out;
      max-width: 400px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    // Estilos según tipo
    const styles = {
      success: 'background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7;',
      danger: 'background: #fee2e2; color: #7f1d1d; border: 1px solid #fca5a5;',
      warning: 'background: #fef3c7; color: #78350f; border: 1px solid #fcd34d;',
      info: 'background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd;'
    };
    
    alert.style.cssText += styles[type] || styles.info;
    alert.textContent = message;
    
    document.body.appendChild(alert);
    
    // Auto-remove después del tiempo especificado
    setTimeout(() => {
      alert.style.animation = 'slideOut 0.3s ease-in';
      setTimeout(() => alert.remove(), 300);
    }, duration);
    
    return alert;
  }

  static success(message, duration = 5000) {
    return this.show(message, 'success', duration);
  }

  static error(message, duration = 5000) {
    return this.show(message, 'danger', duration);
  }

  static warning(message, duration = 5000) {
    return this.show(message, 'warning', duration);
  }

  static info(message, duration = 5000) {
    return this.show(message, 'info', duration);
  }
}

// Formateo de datos
const formatters = {
  currency(value) {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP'
    }).format(value);
  },

  date(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('es-CL', options);
  },

  dateTime(dateString) {
    const options = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('es-CL', options);
  },

  percentage(value) {
    return `${parseFloat(value).toFixed(2)}%`;
  },

  phone(phone) {
    if (!phone) return '';
    const cleaned = phone.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{2})(\d{4})(\d{4})$/);
    return match ? `+56 ${match[1]} ${match[2]} ${match[3]}` : phone;
  },

  rut(rut) {
    if (!rut) return '';
    const cleaned = rut.replace(/\D/g, '');
    if (cleaned.length < 8) return rut;
    const format = cleaned.slice(0, -1);
    const check = cleaned.slice(-1);
    return `${format.replace(/\B(?=(\d{3})+(?!\d))/g, '.')}-${check}`;
  }
};

// Validación de formularios
const validators = {
  email(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  },

  phone(phone) {
    const regex = /^(\+?56)?[\s]?(9)?[\s]?(\d{4})[\s]?(\d{4})$/;
    return regex.test(phone);
  },

  rut(rut) {
    const cleaned = rut.replace(/\D/g, '');
    if (cleaned.length < 8 || cleaned.length > 9) return false;

    const numbers = cleaned.slice(0, -1);
    const check = cleaned.slice(-1);
    let sum = 0;
    let multiplier = 2;

    for (let i = numbers.length - 1; i >= 0; i--) {
      sum += parseInt(numbers[i]) * multiplier;
      multiplier = multiplier === 9 ? 2 : multiplier + 1;
    }

    const remainder = sum % 11;
    const checkDigit = 11 - remainder;

    return check == (checkDigit === 11 ? '0' : checkDigit === 10 ? 'k' : checkDigit);
  },

  password(password) {
    // Mínimo 8 caracteres, debe contener mayúscula, minúscula y número
    return password.length >= 8 && 
           /[A-Z]/.test(password) && 
           /[a-z]/.test(password) && 
           /\d/.test(password);
  },

  required(value) {
    return value && value.trim() !== '';
  },

  minLength(value, length) {
    return value && value.length >= length;
  },

  maxLength(value, length) {
    return value && value.length <= length;
  }
};

// Modal - Global instance handler
let currentModalInstance = null;

class Modal {
  constructor(id) {
    this.modal = document.getElementById(id) || this.createModal(id);
    this.closeBtn = this.modal.querySelector('.modal-close');
    this.setupListeners();
    currentModalInstance = this;
  }

  createModal(id) {
    const modal = document.createElement('div');
    modal.id = id || 'app-modal';
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title"></h2>
          <button class="modal-close">×</button>
        </div>
        <div class="modal-body"></div>
      </div>
    `;
    document.body.appendChild(modal);
    return modal;
  }

  setupListeners() {
    this.closeBtn?.addEventListener('click', () => this.close());
    this.modal.addEventListener('click', (e) => {
      if (e.target === this.modal) this.close();
    });
  }

  show(title = '', content = '') {
    const titleEl = this.modal.querySelector('.modal-title');
    const bodyEl = this.modal.querySelector('.modal-body');

    if (title) titleEl.textContent = title;
    if (content) bodyEl.innerHTML = content;

    this.modal.classList.add('show');
  }

  close() {
    this.modal.classList.remove('show');
  }

  setContent(html) {
    const bodyEl = this.modal.querySelector('.modal-body');
    bodyEl.innerHTML = html;
  }

  addFooter(html) {
    let footer = this.modal.querySelector('.modal-footer');
    if (!footer) {
      footer = document.createElement('div');
      footer.className = 'modal-footer';
      this.modal.querySelector('.modal-content').appendChild(footer);
    }
    footer.innerHTML = html;
  }

  static close() {
    if (currentModalInstance) {
      currentModalInstance.close();
    }
  }
}

// Tabla dinámica
class DataTable {
  constructor(containerId, columns, data = []) {
    this.container = document.getElementById(containerId);
    this.columns = columns;
    this.data = data;
    this.render();
  }

  render() {
    const table = document.createElement('table');
    table.className = 'table';

    // Header
    const thead = table.createTHead();
    const headerRow = thead.insertRow();
    this.columns.forEach(col => {
      const th = document.createElement('th');
      th.textContent = col.label;
      headerRow.appendChild(th);
    });

    // Body
    const tbody = table.createTBody();
    this.data.forEach(row => {
      const tr = tbody.insertRow();
      this.columns.forEach(col => {
        const td = tr.insertCell();
        const value = row[col.key];
        td.innerHTML = col.render ? col.render(value, row) : value || '';
      });
    });

    this.container.innerHTML = '';
    this.container.appendChild(table);
  }

  update(data) {
    this.data = data;
    this.render();
  }

  addRow(row) {
    this.data.push(row);
    this.render();
  }

  removeRow(index) {
    this.data.splice(index, 1);
    this.render();
  }
}

// Form Manager
class FormManager {
  constructor(formId) {
    this.form = document.getElementById(formId);
    this.errors = {};
  }

  validate() {
    this.errors = {};
    const inputs = this.form.querySelectorAll('[required]');

    inputs.forEach(input => {
      if (!input.value.trim()) {
        this.addError(input.name, 'Este campo es requerido');
      }

      // Validaciones específicas
      if (input.type === 'email' && input.value && !validators.email(input.value)) {
        this.addError(input.name, 'Email inválido');
      }
    });

    return Object.keys(this.errors).length === 0;
  }

  addError(fieldName, message) {
    if (!this.errors[fieldName]) {
      this.errors[fieldName] = [];
    }
    this.errors[fieldName].push(message);
    this.showFieldError(fieldName, message);
  }

  showFieldError(fieldName, message) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    if (!field) return;

    let errorEl = field.parentElement.querySelector('.form-error');
    if (!errorEl) {
      errorEl = document.createElement('small');
      errorEl.className = 'form-error';
      field.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = message;
  }

  clearErrors() {
    const errorEls = this.form.querySelectorAll('.form-error');
    errorEls.forEach(el => el.remove());
    this.errors = {};
  }

  getValues() {
    const values = {};
    const inputs = this.form.querySelectorAll('input, select, textarea');

    inputs.forEach(input => {
      if (input.type === 'checkbox') {
        values[input.name] = input.checked;
      } else if (input.type === 'radio') {
        if (input.checked) values[input.name] = input.value;
      } else {
        values[input.name] = input.value;
      }
    });

    return values;
  }

  setValues(values) {
    Object.keys(values).forEach(key => {
      const input = this.form.querySelector(`[name="${key}"]`);
      if (!input) return;

      if (input.type === 'checkbox') {
        input.checked = values[key];
      } else if (input.type === 'radio') {
        const radio = this.form.querySelector(`[name="${key}"][value="${values[key]}"]`);
        if (radio) radio.checked = true;
      } else {
        input.value = values[key];
      }
    });
  }

  reset() {
    this.form.reset();
    this.clearErrors();
  }
}

// Utilidades de strings
const stringUtils = {
  capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  },

  truncate(str, length = 50) {
    return str.length > length ? str.substring(0, length) + '...' : str;
  },

  slugify(str) {
    return str
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^\w\-]+/g, '')
      .replace(/\-\-+/g, '-')
      .trim('-');
  }
};
