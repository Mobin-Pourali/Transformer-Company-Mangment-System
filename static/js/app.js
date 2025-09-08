// Transformer Company Management Application JavaScript

class CustomerApp {
    constructor() {
        this.customers = [];
        this.filteredCustomers = [];
        this.uniqueCustomers = [];
        this.currentSort = 'customer';
        this.selectedCustomer = '';
        this.eventListeners = new Map(); // Track event listeners for cleanup
        this.isInitialized = false;
        this.init();
    }

    init() {
        if (this.isInitialized) {
            this.cleanup();
        }
        this.bindEvents();
        this.checkDatabaseHealth();
        this.loadUniqueCustomers();
        this.loadCustomers();
        this.loadContractCount();
        this.isInitialized = true;
    }

    bindEvents() {
        // Search functionality
        const searchInput = document.getElementById('search-input');
        const searchHandler = (e) => this.handleSearch(e.target.value);
        searchInput.addEventListener('input', searchHandler);
        this.eventListeners.set('search', { element: searchInput, event: 'input', handler: searchHandler });

        // Sort functionality
        const sortSelect = document.getElementById('sort-select');
        const sortHandler = (e) => this.handleSort(e.target.value);
        sortSelect.addEventListener('change', sortHandler);
        this.eventListeners.set('sort', { element: sortSelect, event: 'change', handler: sortHandler });

        // Customer filter functionality
        const customerFilter = document.getElementById('customer-filter');
        const filterHandler = (e) => this.handleCustomerFilter(e.target.value);
        customerFilter.addEventListener('change', filterHandler);
        this.eventListeners.set('filter', { element: customerFilter, event: 'change', handler: filterHandler });

        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        const refreshHandler = () => this.refreshData();
        refreshBtn.addEventListener('click', refreshHandler);
        this.eventListeners.set('refresh', { element: refreshBtn, event: 'click', handler: refreshHandler });

        // Modal close functionality
        const modal = document.getElementById('customer-modal');
        const closeBtn = modal.querySelector('.close');
        const closeHandler = () => this.closeModal();
        closeBtn.addEventListener('click', closeHandler);
        this.eventListeners.set('modalClose', { element: closeBtn, event: 'click', handler: closeHandler });

        // Close modal when clicking outside
        const windowClickHandler = (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        };
        window.addEventListener('click', windowClickHandler);
        this.eventListeners.set('windowClick', { element: window, event: 'click', handler: windowClickHandler });
    }

    async checkDatabaseHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            const dbStatusElement = document.getElementById('db-status');
            if (data.success && data.database === 'connected') {
                dbStatusElement.textContent = 'Connected';
                dbStatusElement.style.color = '#38a169';
            } else {
                dbStatusElement.textContent = 'Disconnected';
                dbStatusElement.style.color = '#e53e3e';
            }
        } catch (error) {
            console.error('Health check failed:', error);
            const dbStatusElement = document.getElementById('db-status');
            dbStatusElement.textContent = 'Error';
            dbStatusElement.style.color = '#e53e3e';
        }
    }

    async loadUniqueCustomers() {
        try {
            const response = await fetch('/api/customers/unique');
            const data = await response.json();

            if (data.success) {
                this.uniqueCustomers = data.customers;
                this.populateCustomerFilter();
                this.updateCustomerCount(data.count);
            } else {
                console.error('Failed to load unique customers:', data.error);
            }
        } catch (error) {
            console.error('Error loading unique customers:', error);
        }
    }

    async loadCustomers() {
        this.showLoading();
        this.hideError();
        this.hideNoCustomers();

        try {
            const response = await fetch('/api/customers');
            const data = await response.json();

            if (data.success) {
                this.customers = data.customers;
                this.filteredCustomers = [...this.customers];
                this.updateCustomerCount(data.count);
                this.renderCustomers();
                this.hideLoading();
            } else {
                throw new Error(data.error || 'Failed to load customers');
            }
        } catch (error) {
            console.error('Error loading customers:', error);
            this.showError('Failed to load customers. Please try again.');
            this.hideLoading();
        }
    }

    populateCustomerFilter() {
        const customerFilter = document.getElementById('customer-filter');
        customerFilter.innerHTML = '<option value="">All Customers</option>';
        
        this.uniqueCustomers.forEach(customer => {
            const option = document.createElement('option');
            option.value = customer;
            option.textContent = customer;
            customerFilter.appendChild(option);
        });
    }

    handleSearch(searchTerm) {
        if (!searchTerm.trim()) {
            this.filteredCustomers = this.filterByCustomer(this.customers);
        } else {
            const term = searchTerm.toLowerCase();
            const customerFiltered = this.filterByCustomer(this.customers);
            this.filteredCustomers = customerFiltered.filter(customer => 
                customer.customer?.toLowerCase().includes(term) ||
                customer.contracts.some(contract => 
                    contract.contract?.toLowerCase().includes(term) ||
                    contract.serial?.toString().includes(term) ||
                    contract.power?.toString().includes(term)
                )
            );
        }
        this.renderCustomers();
    }

    handleCustomerFilter(customerName) {
        this.selectedCustomer = customerName;
        this.filteredCustomers = this.filterByCustomer(this.customers);
        this.renderCustomers();
    }

    filterByCustomer(customers) {
        if (!this.selectedCustomer) {
            return customers;
        }
        return customers.filter(customer => customer.customer === this.selectedCustomer);
    }

    handleSort(sortBy) {
        this.currentSort = sortBy;
        this.filteredCustomers.sort((a, b) => {
            let aVal, bVal;

            if (sortBy === 'customer') {
                aVal = (a.customer || '').toString().toLowerCase();
                bVal = (b.customer || '').toString().toLowerCase();
            } else if (sortBy === 'unique_contracts') {
                aVal = a.unique_contracts || 0;
                bVal = b.unique_contracts || 0;
            } else if (sortBy === 'total_transformers') {
                aVal = a.total_transformers || 0;
                bVal = b.total_transformers || 0;
            } else if (sortBy === 'total_power') {
                aVal = a.total_power || 0;
                bVal = b.total_power || 0;
            } else {
                aVal = (a.customer || '').toString().toLowerCase();
                bVal = (b.customer || '').toString().toLowerCase();
            }

            if (aVal < bVal) return -1;
            if (aVal > bVal) return 1;
            return 0;
        });

        this.renderCustomers();
    }

    renderCustomers() {
        const customerList = document.getElementById('customer-list');
        
        if (this.filteredCustomers.length === 0) {
            this.showNoCustomers();
            return;
        }

        // Clear existing content and event listeners
        customerList.innerHTML = '';
        
        const customerCards = this.filteredCustomers.map(customer => this.createCustomerCard(customer));
        customerList.innerHTML = customerCards.join('');
        
        // Add click event listeners to customer cards with proper cleanup tracking
        this.filteredCustomers.forEach((customer, index) => {
            const card = customerList.children[index];
            const clickHandler = () => this.showCustomerModal(customer);
            card.addEventListener('click', clickHandler);
            
            // Store reference for potential cleanup
            card._clickHandler = clickHandler;
        });
    }

    createCustomerCard(customer) {
        const contractsList = customer.contracts.map(contract => 
            `<div class="contract-item">
                <div class="contract-header">
                    <span class="contract-name">${contract.contract}</span>
                    <span class="contract-stats">
                        <span class="transformer-count">${contract.transformer_count} ترانسفورماتور</span>
                        <span class="contract-power">${contract.total_power.toFixed(1)} MVA</span>
                    </span>
                </div>
                <div class="transformers-list">
                    ${contract.transformers.map(transformer => 
                        `<div class="transformer-item">
                            <span class="transformer-serial">#${transformer.serial}</span>
                            <span class="transformer-power">${transformer.power} MVA</span>
                        </div>`
                    ).join('')}
                </div>
            </div>`
        ).join('');

        return `
            <div class="customer-card" data-customer="${customer.customer}">
                <div class="customer-card-header">
                    <div class="customer-name">${customer.customer}</div>
                    <div class="customer-stats">
                        <div class="stat-badge contract-badge">
                            <span class="number">${customer.unique_contracts}</span>
                            <span class="label">قرارداد</span>
                        </div>
                        <div class="stat-badge transformer-badge">
                            <span class="number">${customer.total_transformers}</span>
                            <span class="label">ترانسفورماتور</span>
                        </div>
                        <div class="stat-badge power-badge">
                            <span class="number">${customer.total_power.toFixed(1)}</span>
                            <span class="label">مگاوات</span>
                        </div>
                    </div>
                </div>
                <div class="customer-info">
                    <div class="contracts-section">
                        <h4>قرارداد های مشتری</h4>
                        <div class="contracts-list">
                            ${contractsList}
                        </div>
                    </div>
                </div>
            </div>

        `;
    }

    showCustomerModal(customer) {
        const modal = document.getElementById('customer-modal');

        // Populate modal with customer data
        document.getElementById('modal-title').textContent = `${customer.customer}`;
        document.getElementById('modal-contract').textContent = `${customer.unique_contracts} قرارداد`;
        document.getElementById('modal-power').textContent = `${customer.total_power.toFixed(1)} مگاوات`;
        document.getElementById('modal-serial').textContent = `${customer.total_transformers} ترانسفورماتور`;

        // Create detailed contract list for modal
        const contractsList = customer.contracts.map(contract => 
            `<div class="modal-contract-item">
                <div class="modal-contract-header">
                    <strong>${contract.contract}</strong>
                    <span class="modal-contract-stats">${contract.transformer_count} ترانسفورماتور, ${contract.total_power.toFixed(1)} مگاوات</span>
                </div>
                <div class="modal-transformers-list">
                    ${contract.transformers.map(transformer => 
                        `<div class="modal-transformer-item">
                            <span class="modal-serial">#${transformer.serial}</span>
                            <span class="modal-transformer-power">${transformer.power} مگاوات</span>
                        </div>`
                    ).join('')}
                </div>
            </div>`
        ).join('');

        // Add contract list to modal
        const modalBody = modal.querySelector('.modal-body');
        let contractListElement = modalBody.querySelector('.contracts-detail');
        if (!contractListElement) {
            contractListElement = document.createElement('div');
            contractListElement.className = 'contracts-detail';
            modalBody.appendChild(contractListElement);
        }
        contractListElement.innerHTML = `
            <h4>تمام قرارداد و ترانسفورماتورها:</h4>
            <div class="modal-contracts-list">
                ${contractsList}
            </div>
        `;

        // Show modal
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    closeModal() {
        const modal = document.getElementById('customer-modal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    updateContractCount(count) {
        const countElement = document.getElementById('contract-count');
        countElement.textContent = count;
    }

    updateCustomerCount(count) {
        const countElement = document.getElementById('customer-count');
        countElement.textContent = count;
    }

    refreshData() {
        this.loadUniqueCustomers();
        this.loadCustomers();
    }

    showLoading() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('customer-list').style.display = 'none';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('customer-list').style.display = 'grid';
    }

    showError(message) {
        const errorElement = document.getElementById('error-message');
        const errorText = document.getElementById('error-text');
        errorText.textContent = message;
        errorElement.style.display = 'block';
        document.getElementById('customer-list').style.display = 'none';
    }

    hideError() {
        document.getElementById('error-message').style.display = 'none';
    }

    showNoCustomers() {
        document.getElementById('no-customers').style.display = 'block';
        document.getElementById('customer-list').style.display = 'none';
    }

    hideNoCustomers() {
        document.getElementById('no-customers').style.display = 'none';
    }

    cleanup() {
        // Remove all tracked event listeners
        this.eventListeners.forEach(({ element, event, handler }) => {
            element.removeEventListener(event, handler);
        });
        this.eventListeners.clear();
        
        // Clear data arrays
        this.customers = [];
        this.filteredCustomers = [];
        this.uniqueCustomers = [];
        
        // Reset state
        this.currentSort = 'customer';
        this.selectedCustomer = '';
        this.isInitialized = false;
    }

    async loadContractCount() {
        try {
            const response = await fetch('/api/customers/contracts');
            const data = await response.json();
    
            if (data.success) {
                this.updateContractCount(data.count);
            } else {
                console.error('Failed to load contract count:', data.error);
            }
        } catch (error) {
            console.error('Error loading contract count:', error);
        }
    }

}

// Global app instance
let appInstance = null;

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (appInstance) {
        appInstance.cleanup();
    }
    appInstance = new CustomerApp();
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (!appInstance) return;
    
    // ESC key to close modal
    if (e.key === 'Escape') {
        const modal = document.getElementById('customer-modal');
        if (modal && modal.style.display === 'block') {
            appInstance.closeModal();
        }
    }
    
    // Ctrl/Cmd + R to refresh
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        appInstance.refreshData();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (appInstance) {
        appInstance.cleanup();
        appInstance = null;
    }
});