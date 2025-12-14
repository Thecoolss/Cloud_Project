/**
 * CUSTOMER PAGE LOGIC
 * Handles meal browsing, cart management, and checkout
 */

class CustomerOrderSystem {
    constructor() {
        // State management
        this.cart = [];
        this.selectedArea = '';
        this.currentMeals = [];
        
        // Initialize
        this.initialize();
    }

    async initialize() {
        console.log('🚀 Initializing customer order system...');
        
        // Get DOM elements first (before loadCart needs them)
        this.getElements();
        
        // Load cart from localStorage
        this.loadCart();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Test API connection
        await this.testConnection();
        
        // Update cart display
        this.updateCartDisplay();
        
        // Show welcome message
        this.showWelcomeMessage();
    }

    getElements() {
        this.elements = {
            // Area selection
            deliveryArea: document.getElementById('deliveryArea'),
            findMealsBtn: document.getElementById('findMealsBtn'),
            currentArea: document.getElementById('currentArea'),
            
            // Meals display
            loading: document.getElementById('loading'),
            mealsSection: document.getElementById('mealsSection'),
            mealsGrid: document.getElementById('mealsGrid'),
            noMealsMessage: document.getElementById('noMealsMessage'),
            
            // Cart elements
            cartSummary: document.getElementById('cartSummary'),
            cartCount: document.getElementById('cartCount'),
            cartTotalPreview: document.getElementById('cartTotalPreview'),
            cartToggleBtn: document.getElementById('cartToggleBtn'),
            cartBadge: document.getElementById('cartBadge'),
            cartSidebar: document.getElementById('cartSidebar'),
            closeCartBtn: document.getElementById('closeCartBtn'),
            cartItems: document.getElementById('cartItems'),
            cartSubtotal: document.getElementById('cartSubtotal'),
            cartTotal: document.getElementById('cartTotal'),
            checkoutBtn: document.getElementById('checkoutBtn'),
            
            // Checkout modal
            checkoutModal: document.getElementById('checkoutModal'),
            orderForm: document.getElementById('orderForm'),
            customerName: document.getElementById('customerName'),
            phoneNumber: document.getElementById('phoneNumber'),
            deliveryAddress: document.getElementById('deliveryAddress'),
            specialInstructions: document.getElementById('specialInstructions'),
            backToCartBtn: document.getElementById('backToCartBtn'),
            submitOrderBtn: document.getElementById('submitOrderBtn'),
            orderSummary: document.getElementById('orderSummary'),
            orderTotal: document.getElementById('orderTotal'),
            
            // Confirmation modal
            confirmationModal: document.getElementById('confirmationModal'),
            orderNumber: document.getElementById('orderNumber'),
            deliveryTime: document.getElementById('deliveryTime'),
            orderTotalAmount: document.getElementById('orderTotalAmount'),
            newOrderBtn: document.getElementById('newOrderBtn')
        };
    }

    setupEventListeners() {
        // Find meals button
        this.elements.findMealsBtn.addEventListener('click', () => this.loadMeals());
        
        // Allow Enter key in area selector
        this.elements.deliveryArea.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.loadMeals();
        });
        
        // Cart toggle
        this.elements.cartToggleBtn.addEventListener('click', () => this.toggleCart());
        this.elements.closeCartBtn.addEventListener('click', () => this.toggleCart());
        this.elements.cartSummary?.addEventListener('click', () => this.toggleCart());
        
        // Checkout flow
        this.elements.checkoutBtn.addEventListener('click', () => this.showCheckout());
        this.elements.backToCartBtn.addEventListener('click', () => this.hideCheckout());
        
        // Order form submission
        this.elements.orderForm.addEventListener('submit', (e) => this.submitOrder(e));
        
        // New order button
        this.elements.newOrderBtn.addEventListener('click', () => this.resetOrder());
        
        // Modal close buttons
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', () => this.closeAllModals());
        });
        
        // Close modals when clicking outside
        [this.elements.checkoutModal, this.elements.confirmationModal].forEach(modal => {
            modal?.addEventListener('click', (e) => {
                if (e.target === modal) this.closeAllModals();
            });
        });
        
        // Close cart when clicking outside (for mobile)
        document.addEventListener('click', (e) => {
            const cartSidebar = this.elements.cartSidebar;
            const cartToggleBtn = this.elements.cartToggleBtn;
            
            if (cartSidebar?.classList.contains('active') && 
                !cartSidebar.contains(e.target) && 
                !cartToggleBtn.contains(e.target)) {
                this.toggleCart();
            }
        });
    }

    showWelcomeMessage() {
        // Check if it's first visit
        if (!localStorage.getItem('hasVisitedBefore')) {
            showMessage('Welcome to FoodExpress! Select your area to start ordering.', 'info');
            localStorage.setItem('hasVisitedBefore', 'true');
        }
    }

    async testConnection() {
        try {
            const connected = await FoodOrderAPI.testConnection();
            if (!connected) {
                showMessage('⚠️ Cannot connect to server. Using demo mode.', 'warning');
            }
        } catch (error) {
            console.error('Connection test failed:', error);
        }
    }

    async loadMeals() {
        const area = this.elements.deliveryArea.value;
        
        if (!area) {
            showMessage('Please select a delivery area first.', 'error');
            return;
        }
        
        this.selectedArea = area;
        this.elements.currentArea.textContent = area;
        
        // Show loading
        this.elements.loading.style.display = 'block';
        this.elements.mealsSection.style.display = 'none';
        this.elements.noMealsMessage.style.display = 'none';
        
        try {
            // Fetch meals from API
            this.currentMeals = await FoodOrderAPI.getMealsByArea(area);
            
            // Hide loading
            this.elements.loading.style.display = 'none';
            
            if (this.currentMeals.length === 0) {
                this.elements.noMealsMessage.style.display = 'block';
                this.elements.mealsSection.style.display = 'none';
                showMessage(`No meals available in ${area}. Try another area.`, 'info');
                return;
            }
            
            // Display meals
            this.displayMeals();
            this.elements.mealsSection.style.display = 'block';
            
            // Show cart summary if we have items
            if (this.cart.length > 0) {
                this.elements.cartSummary.style.display = 'flex';
            }
            
            // Scroll to meals
            this.elements.mealsSection.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            this.elements.loading.style.display = 'none';
            showMessage(`Error loading meals: ${error.message}`, 'error');
            console.error('Meal loading error:', error);
            
            // Show demo data if API fails
            this.showDemoMeals();
        }
    }

    displayMeals() {
        this.elements.mealsGrid.innerHTML = '';
        
        this.currentMeals.forEach(meal => {
            const isInCart = this.cart.some(item => item.id === meal.id);
            const cartItem = this.cart.find(item => item.id === meal.id);
            
            const mealCard = document.createElement('div');
            mealCard.className = 'meal-card';
            mealCard.innerHTML = `
                <img src="${meal.imageUrl || 'https://via.placeholder.com/300x200?text=Food+Image'}" 
                     alt="${meal.name}" 
                     class="meal-image"
                     onerror="this.src='https://via.placeholder.com/300x200?text=Food+Image'">
                <div class="meal-content">
                    <h3 class="meal-title">${meal.name}</h3>
                    <p class="meal-description">${meal.description}</p>
                    <div class="meal-details">
                        <span class="meal-price">$${meal.price.toFixed(2)}</span>
                        <span class="meal-prep-time">
                            <i class="fas fa-clock"></i> ${meal.preparationTime} min
                        </span>
                    </div>
                    <div class="meal-footer">
                        <span class="restaurant-name">
                            <i class="fas fa-store"></i> ${meal.restaurantName}
                        </span>
                        <button class="add-to-cart-btn ${isInCart ? 'added' : ''}" 
                                data-meal-id="${meal.id}"
                                data-meal-name="${meal.name}"
                                data-meal-price="${meal.price}">
                            ${isInCart ? 
                                `<i class="fas fa-check"></i> ${cartItem.quantity} in Cart` : 
                                `<i class="fas fa-cart-plus"></i> Add to Cart`}
                        </button>
                    </div>
                </div>
            `;
            
            this.elements.mealsGrid.appendChild(mealCard);
        });
        
        // Add event listeners to Add to Cart buttons
        this.addCartButtonListeners();
    }

    addCartButtonListeners() {
        document.querySelectorAll('.add-to-cart-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const btn = e.target.closest('button');
                const mealId = btn.dataset.mealId;
                const mealName = btn.dataset.mealName;
                const mealPrice = parseFloat(btn.dataset.mealPrice);
                
                this.addToCart(mealId, mealName, mealPrice);
            });
        });
    }

    addToCart(mealId, mealName, mealPrice) {
        const existingIndex = this.cart.findIndex(item => item.id === mealId);
        
        if (existingIndex > -1) {
            // Update quantity
            this.cart[existingIndex].quantity += 1;
        } else {
            // Add new item
            this.cart.push({
                id: mealId,
                name: mealName,
                price: mealPrice,
                quantity: 1
            });
        }
        
        // Save to localStorage
        this.saveCart();
        
        // Update display
        this.updateCartDisplay();
        
        // Update the button in the meals grid
        this.updateMealButton(mealId);
        
        // Show success message
        showMessage(`${mealName} added to cart!`, 'success');
        
        // Open cart sidebar on mobile
        if (window.innerWidth < 768) {
            this.elements.cartSidebar.classList.add('active');
        }
    }

    removeFromCart(mealId) {
        const existingIndex = this.cart.findIndex(item => item.id === mealId);
        
        if (existingIndex > -1) {
            const mealName = this.cart[existingIndex].name;
            this.cart.splice(existingIndex, 1);
            
            // Save to localStorage
            this.saveCart();
            
            // Update display
            this.updateCartDisplay();
            
            // Update the button in the meals grid
            this.updateMealButton(mealId);
            
            // Show message
            showMessage(`${mealName} removed from cart`, 'info');
        }
    }

    updateQuantity(mealId, change) {
        const existingIndex = this.cart.findIndex(item => item.id === mealId);
        
        if (existingIndex > -1) {
            this.cart[existingIndex].quantity += change;
            
            // Remove if quantity is 0 or less
            if (this.cart[existingIndex].quantity <= 0) {
                this.cart.splice(existingIndex, 1);
            }
            
            // Save to localStorage
            this.saveCart();
            
            // Update display
            this.updateCartDisplay();
            
            // Update the button in the meals grid
            this.updateMealButton(mealId);
        }
    }

    updateMealButton(mealId) {
        const button = document.querySelector(`.add-to-cart-btn[data-meal-id="${mealId}"]`);
        if (button) {
            const cartItem = this.cart.find(item => item.id === mealId);
            
            if (cartItem) {
                button.innerHTML = `<i class="fas fa-check"></i> ${cartItem.quantity} in Cart`;
                button.classList.add('added');
            } else {
                button.innerHTML = `<i class="fas fa-cart-plus"></i> Add to Cart`;
                button.classList.remove('added');
            }
        }
    }

    updateCartDisplay() {
        // Calculate item count and totals
        const itemCount = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        const subtotal = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const deliveryFee = 2.99;
        const total = subtotal + deliveryFee;
        
        // Update UI elements
        if (this.elements.cartBadge) this.elements.cartBadge.textContent = itemCount;
        if (this.elements.cartCount) this.elements.cartCount.textContent = itemCount;
        if (this.elements.cartTotalPreview) this.elements.cartTotalPreview.textContent = total.toFixed(2);
        if (this.elements.cartSubtotal) this.elements.cartSubtotal.textContent = subtotal.toFixed(2);
        if (this.elements.cartTotal) this.elements.cartTotal.textContent = total.toFixed(2);
        
        // Update cart items display
        this.updateCartItems();
        
        // Update estimated delivery time in cart footer
        this.updateCartDeliveryTime();
        
        // Enable/disable checkout button
        if (this.elements.checkoutBtn) {
            this.elements.checkoutBtn.disabled = this.cart.length === 0;
        }
        
        // Show/hide cart summary
        if (this.elements.cartSummary && this.elements.mealsSection.style.display !== 'none') {
            this.elements.cartSummary.style.display = this.cart.length > 0 ? 'flex' : 'none';
        }
    }
    
    updateCartDeliveryTime() {
        // Find or create delivery time element in cart footer
        const cartFooter = document.querySelector('.cart-footer');
        if (!cartFooter) return;
        
        let deliveryTimeEl = document.getElementById('cartEstimatedTime');
        
        if (this.cart.length === 0) {
            // Remove delivery time if cart is empty
            if (deliveryTimeEl) deliveryTimeEl.remove();
            return;
        }
        
        const estimatedTime = this.calculateEstimatedDeliveryTime();
        
        if (!deliveryTimeEl) {
            // Create new element if it doesn't exist
            deliveryTimeEl = document.createElement('div');
            deliveryTimeEl.id = 'cartEstimatedTime';
            deliveryTimeEl.className = 'cart-delivery-time';
            
            // Insert before the checkout button
            const checkoutBtn = document.getElementById('checkoutBtn');
            if (checkoutBtn) {
                cartFooter.insertBefore(deliveryTimeEl, checkoutBtn);
            }
        }
        
        deliveryTimeEl.innerHTML = `
            <i class="fas fa-clock"></i>
            <span>Estimated Delivery: <strong>${estimatedTime} minutes</strong></span>
        `;
    }

    updateCartItems() {
        const cartItemsEl = this.elements.cartItems;
        if (!cartItemsEl) return;
        
        if (this.cart.length === 0) {
            cartItemsEl.innerHTML = `
                <div class="empty-cart">
                    <i class="fas fa-shopping-basket"></i>
                    <p>Your cart is empty</p>
                    <p>Add some delicious meals!</p>
                </div>
            `;
            return;
        }
        
        cartItemsEl.innerHTML = this.cart.map(item => `
            <div class="cart-item" data-meal-id="${item.id}">
                <div class="cart-item-details">
                    <h4>${item.name}</h4>
                    <p class="cart-item-price">$${item.price.toFixed(2)} each</p>
                </div>
                <div class="cart-item-actions">
                    <button class="quantity-btn decrease-btn" data-meal-id="${item.id}">-</button>
                    <span class="quantity">${item.quantity}</span>
                    <button class="quantity-btn increase-btn" data-meal-id="${item.id}">+</button>
                    <button class="remove-btn" data-meal-id="${item.id}" title="Remove item">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
        
        // Add event listeners to cart buttons
        this.addCartItemListeners();
    }

    addCartItemListeners() {
        // Decrease quantity buttons
        document.querySelectorAll('.decrease-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mealId = e.target.dataset.mealId || e.target.closest('button').dataset.mealId;
                this.updateQuantity(mealId, -1);
            });
        });
        
        // Increase quantity buttons
        document.querySelectorAll('.increase-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mealId = e.target.dataset.mealId || e.target.closest('button').dataset.mealId;
                this.updateQuantity(mealId, 1);
            });
        });
        
        // Remove buttons
        document.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mealId = e.target.dataset.mealId || e.target.closest('button').dataset.mealId;
                this.removeFromCart(mealId);
            });
        });
    }

    toggleCart() {
        if (this.elements.cartSidebar) {
            this.elements.cartSidebar.classList.toggle('active');
        }
    }

    showCheckout() {
        // Update order summary
        this.updateOrderSummary();
        
        // Show checkout modal
        if (this.elements.checkoutModal) {
            this.elements.checkoutModal.style.display = 'flex';
        }
        this.toggleCart();
    }

    hideCheckout() {
        if (this.elements.checkoutModal) {
            this.elements.checkoutModal.style.display = 'none';
        }
    }

    updateOrderSummary() {
        if (!this.elements.orderSummary || !this.elements.orderTotal) return;
        
        const orderItems = this.cart.map(item => `
            <div class="order-item">
                <span>${item.name} x${item.quantity}</span>
                <span>$${(item.price * item.quantity).toFixed(2)}</span>
            </div>
        `).join('');
        
        const subtotal = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const deliveryFee = 2.99;
        const total = subtotal + deliveryFee;
        
        // Calculate estimated delivery time
        const estimatedTime = this.calculateEstimatedDeliveryTime();
        
        this.elements.orderSummary.innerHTML = `
            ${orderItems}
            <div class="order-item">
                <span>Delivery Fee</span>
                <span>$${deliveryFee.toFixed(2)}</span>
            </div>
            <div class="order-item estimated-time">
                <span><i class="fas fa-clock"></i> Estimated Delivery Time</span>
                <span><strong>${estimatedTime} minutes</strong></span>
            </div>
        `;
        
        this.elements.orderTotal.textContent = `$${total.toFixed(2)}`;
    }
    
    calculateEstimatedDeliveryTime() {
        // Get total preparation time from cart items
        let totalPrepTime = 0;
        
        this.cart.forEach(cartItem => {
            const meal = this.currentMeals.find(m => m.id === cartItem.id);
            if (meal && meal.preparationTime) {
                totalPrepTime += meal.preparationTime * cartItem.quantity;
            }
        });
        
        // Add fixed times as per rubric:
        // Estimated Time = sum(preparation times) + fixed pickup time + fixed delivery time
        const fixedPickupTime = 10;  // minutes
        const fixedDeliveryTime = 20; // minutes
        const totalEstimatedTime = totalPrepTime + fixedPickupTime + fixedDeliveryTime;
        
        return totalEstimatedTime;
    }

    async submitOrder(e) {
        e.preventDefault();
        
        // Get form data
        const formData = {
            customerName: this.elements.customerName?.value || '',
            phoneNumber: this.elements.phoneNumber?.value || '',
            deliveryAddress: this.elements.deliveryAddress?.value || '',
            specialInstructions: this.elements.specialInstructions?.value || '',
            area: this.selectedArea || this.elements.deliveryArea?.value || 'Central',
            meals: this.cart.map(item => ({
                mealId: item.id,
                quantity: item.quantity
            }))
        };
        
        // Validate form
        if (!formData.customerName || !formData.phoneNumber || !formData.deliveryAddress) {
            showMessage('Please fill in all required fields.', 'error');
            return;
        }
        
        // Disable submit button
        if (this.elements.submitOrderBtn) {
            this.elements.submitOrderBtn.disabled = true;
            this.elements.submitOrderBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        }
        
        try {
            // Submit order to API
            const result = await FoodOrderAPI.submitOrder(formData);
            
            // Show success message
            this.showConfirmation(result);
            
            // Clear cart
            this.cart = [];
            this.saveCart();
            this.updateCartDisplay();
            
        } catch (error) {
            showMessage(`Order failed: ${error.message}`, 'error');
            console.error('Order submission error:', error);
            
            // Re-enable submit button
            if (this.elements.submitOrderBtn) {
                this.elements.submitOrderBtn.disabled = false;
                this.elements.submitOrderBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Place Order';
            }
        }
    }

    showConfirmation(orderResult) {
        // Update confirmation details
        if (this.elements.orderNumber) this.elements.orderNumber.textContent = orderResult.orderNumber;
        if (this.elements.deliveryTime) this.elements.deliveryTime.textContent = orderResult.deliveryTimeFormatted;
        if (this.elements.orderTotalAmount) {
            this.elements.orderTotalAmount.textContent = `$${orderResult.totalCost.toFixed(2)}`;
        }
        
        // Hide checkout modal
        this.hideCheckout();
        
        // Show confirmation modal
        if (this.elements.confirmationModal) {
            this.elements.confirmationModal.style.display = 'flex';
        }
    }

    resetOrder() {
        // Close all modals
        this.closeAllModals();
        
        // Reset form
        if (this.elements.orderForm) this.elements.orderForm.reset();
        
        // Reset cart sidebar
        this.toggleCart();
        
        // Re-enable submit button
        if (this.elements.submitOrderBtn) {
            this.elements.submitOrderBtn.disabled = false;
            this.elements.submitOrderBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Place Order';
        }
        
        // Clear area selection
        if (this.elements.deliveryArea) this.elements.deliveryArea.value = '';
        
        // Hide meals section
        if (this.elements.mealsSection) this.elements.mealsSection.style.display = 'none';
        
        // Show welcome message again
        showMessage('Select your delivery area to start a new order!', 'info');
    }

    closeAllModals() {
        if (this.elements.checkoutModal) this.elements.checkoutModal.style.display = 'none';
        if (this.elements.confirmationModal) this.elements.confirmationModal.style.display = 'none';
    }

    saveCart() {
        localStorage.setItem('foodOrderCart', JSON.stringify(this.cart));
        localStorage.setItem('selectedArea', this.selectedArea);
    }

    loadCart() {
        const savedCart = localStorage.getItem('foodOrderCart');
        const savedArea = localStorage.getItem('selectedArea');
        
        if (savedCart) {
            try {
                this.cart = JSON.parse(savedCart);
            } catch (e) {
                this.cart = [];
                localStorage.removeItem('foodOrderCart');
            }
        }
        
        if (savedArea && this.elements.deliveryArea) {
            this.selectedArea = savedArea;
            this.elements.deliveryArea.value = savedArea;
        }
    }

    showDemoMeals() {
        // Demo data for testing when API is unavailable
        this.currentMeals = [
            {
                id: 'demo-1',
                name: 'Margherita Pizza',
                description: 'Classic pizza with tomato sauce and mozzarella',
                price: 12.99,
                preparationTime: 25,
                category: 'Main Course',
                restaurantName: 'Demo Italian Restaurant',
                imageUrl: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&h=300&fit=crop'
            },
            {
                id: 'demo-2',
                name: 'Chicken Burger',
                description: 'Grilled chicken burger with fresh vegetables',
                price: 10.99,
                preparationTime: 15,
                category: 'Main Course',
                restaurantName: 'Demo Burger Joint',
                imageUrl: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop'
            },
            {
                id: 'demo-3',
                name: 'Chocolate Milkshake',
                description: 'Rich chocolate milkshake with whipped cream',
                price: 5.99,
                preparationTime: 8,
                category: 'Beverage',
                restaurantName: 'Demo Dessert Cafe',
                imageUrl: 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400&h=300&fit=crop'
            }
        ];
        
        this.elements.loading.style.display = 'none';
        this.displayMeals();
        this.elements.mealsSection.style.display = 'block';
        
        showMessage('Using demo data. Real meals will load when connected to server.', 'warning');
    }
}

// Initialize the system when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on the customer page
    if (document.getElementById('findMealsBtn')) {
        window.customerSystem = new CustomerOrderSystem();
    }
});