// Custom Select Dropdown
class CustomSelect {
    constructor(selectElement) {
        this.select = selectElement;
        this.container = null;
        this.trigger = null;
        this.menu = null;
        this.isOpen = false;
        
        // No inicializar si ya está convertido
        if (this.select.parentNode?.classList.contains('custom-select-container')) {
            return;
        }
        
        this.init();
    }

    init() {
        // Crear contenedor
        this.container = document.createElement('div');
        this.container.className = 'custom-select-container';

        // Crear disparador
        this.trigger = document.createElement('div');
        this.trigger.className = 'custom-select-trigger';
        this.trigger.textContent = this.select.options[this.select.selectedIndex].text;

        // Crear menú
        this.menu = document.createElement('div');
        this.menu.className = 'custom-select-menu';

        // Agregar opciones
        Array.from(this.select.options).forEach((option, index) => {
            const item = document.createElement('div');
            item.className = 'custom-select-item';
            if (index === this.select.selectedIndex) {
                item.classList.add('active');
            }
            item.textContent = option.text;
            item.dataset.value = option.value;
            item.addEventListener('click', () => this.selectOption(index));
            this.menu.appendChild(item);
        });

        // Ensamblar
        this.container.appendChild(this.trigger);
        this.container.appendChild(this.menu);

        // Reemplazar select original
        this.select.style.display = 'none';
        this.select.parentNode.insertBefore(this.container, this.select);

        // Event listeners
        this.trigger.addEventListener('click', () => this.toggle());
        document.addEventListener('click', (e) => this.handleClickOutside(e));
    }

    toggle() {
        this.isOpen ? this.close() : this.open();
    }

    open() {
        this.isOpen = true;
        this.menu.classList.add('active');
        this.trigger.classList.add('active');
    }

    close() {
        this.isOpen = false;
        this.menu.classList.remove('active');
        this.trigger.classList.remove('active');
    }

    selectOption(index) {
        this.select.selectedIndex = index;
        this.trigger.textContent = this.select.options[index].text;

        // Actualizar items activos
        Array.from(this.menu.children).forEach((item, i) => {
            item.classList.toggle('active', i === index);
        });

        // Disparar evento change
        this.select.dispatchEvent(new Event('change', { bubbles: true }));
        this.close();
    }

    handleClickOutside(e) {
        if (!this.container.contains(e.target)) {
            this.close();
        }
    }
}

// Función auxiliar para inicializar selects dinámicamente
function initializeCustomSelects(container = document) {
    container.querySelectorAll('select.form-control').forEach(select => {
        // Verificar si ya está convertido
        if (!select.parentNode?.classList.contains('custom-select-container')) {
            new CustomSelect(select);
        }
    });
}

// Inicializar todos los selects al cargar
document.addEventListener('DOMContentLoaded', () => {
    initializeCustomSelects();
});

