/**
 * RESTAURANT PAGE LOGIC
 * Handles meal registration and management
 */

class RestaurantPortal {
    constructor() {
        // State management
        this.registeredMeals = [];
        this.currentRestaurantId = null;
        
        // Initialize
        this.initialize();
    }

    async initialize() {
        console.log('🏪 Initializing restaurant portal...');
        
        // Generate or retrieve restaurant ID
        this.setupRestaurantId();
        
        // Get DOM elements
        this.getElements();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load existing meals
        await this.loadRegisteredMeals();
        
        // Test API connection
        await this.testConnection();
        
        // Show welcome message
        this.showWelcomeMessage();
    }

    setupRestaurantId() {
        // Generate a persistent restaurant ID for this session
        let restaurantId = localStorage.getItem('restaurantId');
        if (!restaurantId) {
            restaurantId = 'restaurant-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('restaurantId', restaurantId);
        }
        this.currentRestaurantId = restaurantId;
        console.log('Restaurant ID:', this.currentRestaurantId);
    }

    getElements() {
        this.elements = {
            // Form elements
            mealForm: document.getElementById('mealForm'),
            mealName: document.getElementById('mealName'),
            restaurantName: document.getElementById('restaurantName'),
            mealDescription: document.getElementById('mealDescription'),
            mealPrice: document.getElementById('mealPrice'),
            prepTime: document.getElementById('prepTime'),
            mealCategory: document.getElementById('mealCategory'),
            isVegetarian: document.getElementById('isVegetarian'),
            isAvailable: document.getElementById('isAvailable'),
            calories: document.getElementById('calories'),
            submitMealBtn: document.getElementById('submitMealBtn'),
            
            // Success modal
            successModal: document.getElementById('successModal'),
            successMealName: document.getElementById('successMealName'),
            successMealId: document.getElementById('successMealId'),
            successMealCategory: document.getElementById('successMealCategory'),
            successMealPrice: document.getElementById('successMealPrice'),
            viewMealsBtn: document.getElementById('viewMealsBtn'),
            addAnotherBtn: document.getElementById('addAnotherBtn'),
            
            // Meals list
            registeredMeals: document.getElementById('registeredMeals'),
            mealsCount: document.getElementById('mealsCount'),
            mealSearch: document.getElementById('mealSearch'),
            categoryFilter: document.getElementById('categoryFilter')
        };
    }

    setupEventListeners() {
        // Form submission
        if (this.elements.mealForm) {
            this.elements.mealForm.addEventListener('submit', (e) => this.registerMeal(e));
        }
        
        // Form reset
        if (this.elements.mealForm) {
            this.elements.mealForm.addEventListener('reset', () => this.resetForm());
        }
        
        // Success modal buttons
        if (this.elements.viewMealsBtn) {
            this.elements.viewMealsBtn.addEventListener('click', () => this.closeSuccessModal());
        }
        if (this.elements.addAnotherBtn) {
            this.elements.addAnotherBtn.addEventListener('click', () => this.closeSuccessModalAndReset());
        }
        
        // Search and filter
        if (this.elements.mealSearch) {
            this.elements.mealSearch.addEventListener('input', () => this.filterMeals());
        }
        if (this.elements.categoryFilter) {
            this.elements.categoryFilter.addEventListener('change', () => this.filterMeals());
        }
        
        // Close modal when clicking outside
        if (this.elements.successModal) {
            this.elements.successModal.addEventListener('click', (e) => {
                if (e.target === this.elements.successModal) {
                    this.closeSuccessModal();
                }
            });
        }
        
        // Real-time form validation
        this.setupFormValidation();
    }

    setupFormValidation() {
        // Real-time price validation
        if (this.elements.mealPrice) {
            this.elements.mealPrice.addEventListener('input', (e) => {
                const value = parseFloat(e.target.value);
                if (value <= 0) {
                    e.target.classList.add('error');
                } else {
                    e.target.classList.remove('error');
                }
            });
        }
        
        // Real-time prep time validation
        if (this.elements.prepTime) {
            this.elements.prepTime.addEventListener('input', (e) => {
                const value = parseInt(e.target.value);
                if (value <= 0) {
                    e.target.classList.add('error');
                } else {
                    e.target.classList.remove('error');
                }
            });
        }
        
        // Auto-save form draft
        if (this.elements.mealForm) {
            this.elements.mealForm.addEventListener('input', () => this.saveFormDraft());
        }
        
        // Load saved draft on page load
        this.loadFormDraft();
    }

    showWelcomeMessage() {
        // Check if it's first visit to restaurant page
        if (!localStorage.getItem('hasVisitedRestaurantBefore')) {
            showMessage('Welcome to the Restaurant Portal! Register your meals to reach customers.', 'info');
            localStorage.setItem('hasVisitedRestaurantBefore', 'true');
        }
    }

    async testConnection() {
        try {
            const connected = await FoodOrderAPI.testConnection();
            if (!connected) {
                showMessage('⚠️ Cannot connect to server. You can still fill out the form.', 'warning');
            }
        } catch (error) {
            console.error('Connection test failed:', error);
        }
    }

    async registerMeal(e) {
        e.preventDefault();
        
        // Validate form
        if (!this.validateForm()) {
            return;
        }
        
        // Get form data
        const formData = this.getFormData();
        
        // Check if at least one delivery area is selected
        const deliveryAreas = this.getSelectedDeliveryAreas();
        if (deliveryAreas.length === 0) {
            showMessage('Please select at least one delivery area.', 'error');
            return;
        }
        
        formData.deliveryAreas = deliveryAreas;
        formData.restaurantId = this.currentRestaurantId;
        
        // Disable submit button
        if (this.elements.submitMealBtn) {
            this.elements.submitMealBtn.disabled = true;
            this.elements.submitMealBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registering...';
        }
        
        try {
            // Register meal via API
            const result = await FoodOrderAPI.registerMeal(formData);
            
            // Show success modal
            this.showSuccessModal(result, formData);
            
            // Add to local meals list
            this.addMealToList({
                id: result.mealId,
                name: formData.name,
                description: formData.description,
                price: parseFloat(formData.price),
                category: formData.category,
                restaurantName: formData.restaurantName,
                preparationTime: parseInt(formData.preparationTime),
                isVegetarian: formData.isVegetarian,
                isAvailable: formData.isAvailable,
                calories: formData.calories
            });
            
            // Update meals count
            this.updateMealsCount();
            
            // Clear form draft
            this.clearFormDraft();
            
        } catch (error) {
            showMessage(`Registration failed: ${error.message}`, 'error');
            console.error('Meal registration error:', error);
            
            // Re-enable submit button
            if (this.elements.submitMealBtn) {
                this.elements.submitMealBtn.disabled = false;
                this.elements.submitMealBtn.innerHTML = '<i class="fas fa-save"></i> Register Meal';
            }
            
            // Show demo success for testing
            if (error.message.includes('Cannot connect')) {
                this.showDemoSuccess(formData);
            }
        }
    }

    getFormData() {
        return {
            name: this.elements.mealName?.value.trim() || '',
            restaurantName: this.elements.restaurantName?.value.trim() || '',
            description: this.elements.mealDescription?.value.trim() || '',
            price: this.elements.mealPrice?.value || '0',
            preparationTime: this.elements.prepTime?.value || '0',
            category: this.elements.mealCategory?.value || 'Main Course',
            isVegetarian: this.elements.isVegetarian?.checked || false,
            isAvailable: this.elements.isAvailable?.checked !== false,
            calories: this.elements.calories?.value || 0
        };
    }

    getSelectedDeliveryAreas() {
        return Array.from(document.querySelectorAll('input[name="deliveryArea"]:checked'))
            .map(checkbox => checkbox.value);
    }

    validateForm() {
        // Check required fields
        const requiredFields = [
            { element: this.elements.mealName, name: 'Meal Name' },
            { element: this.elements.restaurantName, name: 'Restaurant Name' },
            { element: this.elements.mealDescription, name: 'Description' },
            { element: this.elements.mealPrice, name: 'Price' },
            { element: this.elements.prepTime, name: 'Preparation Time' },
            { element: this.elements.mealCategory, name: 'Category' }
        ];
        
        const missingFields = [];
        
        requiredFields.forEach(field => {
            if (!field.element?.value.trim()) {
                missingFields.push(field.name);
                field.element?.classList.add('error');
            } else {
                field.element?.classList.remove('error');
            }
        });
        
        // Validate price
        if (this.elements.mealPrice?.value) {
            const price = parseFloat(this.elements.mealPrice.value);
            if (price <= 0) {
                missingFields.push('Valid Price (must be greater than 0)');
                this.elements.mealPrice.classList.add('error');
            }
        }
        
        // Validate prep time
        if (this.elements.prepTime?.value) {
            const prepTime = parseInt(this.elements.prepTime.value);
            if (prepTime <= 0) {
                missingFields.push('Valid Preparation Time (must be greater than 0)');
                this.elements.prepTime.classList.add('error');
            }
        }
        
        if (missingFields.length > 0) {
            showMessage(`Please fill in: ${missingFields.join(', ')}`, 'error');
            return false;
        }
        
        return true;
    }

    showSuccessModal(result, formData) {
        // Update modal content
        if (this.elements.successMealName) this.elements.successMealName.textContent = formData.name;
        if (this.elements.successMealId) this.elements.successMealId.textContent = result.mealId;
        if (this.elements.successMealCategory) this.elements.successMealCategory.textContent = formData.category;
        if (this.elements.successMealPrice) {
            this.elements.successMealPrice.textContent = `$${parseFloat(formData.price).toFixed(2)}`;
        }
        
        // Show modal
        if (this.elements.successModal) {
            this.elements.successModal.style.display = 'flex';
        }
        
        // Re-enable submit button
        if (this.elements.submitMealBtn) {
            this.elements.submitMealBtn.disabled = false;
            this.elements.submitMealBtn.innerHTML = '<i class="fas fa-save"></i> Register Meal';
        }
        
        // Play success sound (optional)
        this.playSuccessSound();
    }

    playSuccessSound() {
        // Simple success sound using Web Audio API
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (e) {
            // Sound not supported or blocked
            console.log('Audio not available');
        }
    }

    showDemoSuccess(formData) {
        // Demo success for testing when API is unavailable
        const demoMealId = 'demo-' + Date.now();
        
        this.showSuccessModal({
            mealId: demoMealId,
            status: 'success',
            message: 'Meal registered (demo mode)'
        }, formData);
        
        // Add to local meals list
        this.addMealToList({
            id: demoMealId,
            name: formData.name,
            description: formData.description,
            price: parseFloat(formData.price),
            category: formData.category,
            restaurantName: formData.restaurantName,
            preparationTime: parseInt(formData.preparationTime),
            isVegetarian: formData.isVegetarian,
            isAvailable: formData.isAvailable,
            calories: formData.calories
        });
        
        showMessage('Demo mode: Meal saved locally. Will sync when connected to server.', 'warning');
    }

    closeSuccessModal() {
        if (this.elements.successModal) {
            this.elements.successModal.style.display = 'none';
        }
        
        // Scroll to meals list
        if (this.elements.registeredMeals) {
            this.elements.registeredMeals.scrollIntoView({ behavior: 'smooth' });
        }
    }

    closeSuccessModalAndReset() {
        this.closeSuccessModal();
        this.resetForm();
        
        // Scroll to form
        if (this.elements.mealForm) {
            this.elements.mealForm.scrollIntoView({ behavior: 'smooth' });
        }
    }

    resetForm() {
        // Clear all checkboxes
        document.querySelectorAll('input[name="deliveryArea"]').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        // Remove error classes
        document.querySelectorAll('.error').forEach(element => {
            element.classList.remove('error');
        });
        
        // Reset vegetarian and available checkboxes
        if (this.elements.isVegetarian) this.elements.isVegetarian.checked = false;
        if (this.elements.isAvailable) this.elements.isAvailable.checked = true;
        
        // Clear calories
        if (this.elements.calories) this.elements.calories.value = '';
        
        // Clear form draft
        this.clearFormDraft();
    }

    saveFormDraft() {
        const draft = {
            mealName: this.elements.mealName?.value || '',
            restaurantName: this.elements.restaurantName?.value || '',
            mealDescription: this.elements.mealDescription?.value || '',
            mealPrice: this.elements.mealPrice?.value || '',
            prepTime: this.elements.prepTime?.value || '',
            mealCategory: this.elements.mealCategory?.value || '',
            isVegetarian: this.elements.isVegetarian?.checked || false,
            isAvailable: this.elements.isAvailable?.checked !== false,
            calories: this.elements.calories?.value || '',
            deliveryAreas: this.getSelectedDeliveryAreas()
        };
        
        localStorage.setItem('mealFormDraft', JSON.stringify(draft));
    }

    loadFormDraft() {
        const draft = localStorage.getItem('mealFormDraft');
        if (draft) {
            try {
                const data = JSON.parse(draft);
                
                // Fill form fields
                if (this.elements.mealName) this.elements.mealName.value = data.mealName || '';
                if (this.elements.restaurantName) this.elements.restaurantName.value = data.restaurantName || '';
                if (this.elements.mealDescription) this.elements.mealDescription.value = data.mealDescription || '';
                if (this.elements.mealPrice) this.elements.mealPrice.value = data.mealPrice || '';
                if (this.elements.prepTime) this.elements.prepTime.value = data.prepTime || '';
                if (this.elements.mealCategory) this.elements.mealCategory.value = data.mealCategory || '';
                if (this.elements.isVegetarian) this.elements.isVegetarian.checked = data.isVegetarian || false;
                if (this.elements.isAvailable) this.elements.isAvailable.checked = data.isAvailable !== false;
                if (this.elements.calories) this.elements.calories.value = data.calories || '';
                
                // Check delivery areas
                if (data.deliveryAreas && Array.isArray(data.deliveryAreas)) {
                    document.querySelectorAll('input[name="deliveryArea"]').forEach(checkbox => {
                        checkbox.checked = data.deliveryAreas.includes(checkbox.value);
                    });
                }
                
                showMessage('Loaded saved draft from previous session', 'info');
                
            } catch (e) {
                console.error('Error loading form draft:', e);
            }
        }
    }

    clearFormDraft() {
        localStorage.removeItem('mealFormDraft');
    }

    async loadRegisteredMeals() {
        try {
            // Show loading
            if (this.elements.registeredMeals) {
                this.elements.registeredMeals.innerHTML = `
                    <div class="loading">
                        <i class="fas fa-spinner fa-spin"></i> Loading meals...
                    </div>
                `;
            }
            
            // Load meals from API
            this.registeredMeals = await FoodOrderAPI.getRecentMeals();
            
            // Filter to show only meals from this restaurant (in a real app)
            // For demo, show all meals
            this.displayMeals();
            
            // Update meals count
            this.updateMealsCount();
            
        } catch (error) {
            console.error('Error loading meals:', error);
            
            // Show demo meals
            this.showDemoMeals();
        }
    }

    displayMeals() {
        if (!this.elements.registeredMeals) return;
        
        if (this.registeredMeals.length === 0) {
            this.elements.registeredMeals.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-utensils"></i>
                    <h3>No meals registered yet</h3>
                    <p>Register your first meal using the form</p>
                </div>
            `;
            return;
        }
        
        this.elements.registeredMeals.innerHTML = this.registeredMeals.map(meal => `
            <div class="meal-list-item" data-category="${meal.category}" data-name="${meal.name.toLowerCase()}">
                <div class="meal-list-info">
                    <h4>${meal.name}</h4>
                    <p>${meal.description.substring(0, 60)}${meal.description.length > 60 ? '...' : ''}</p>
                    <div class="meal-tags">
                        <span class="tag tag-category">${meal.category}</span>
                        ${meal.isVegetarian ? '<span class="tag tag-vegetarian">Vegetarian</span>' : ''}
                        ${!meal.isAvailable ? '<span class="tag tag-unavailable">Unavailable</span>' : ''}
                    </div>
                </div>
                <div class="meal-list-right">
                    <div class="meal-list-price">$${meal.price.toFixed(2)}</div>
                    <div class="meal-list-meta">
                        <span class="meta-item">
                            <i class="fas fa-clock"></i> ${meal.preparationTime} min
                        </span>
                        <span class="meta-item">
                            <i class="fas fa-store"></i> ${meal.restaurantName}
                        </span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    addMealToList(meal) {
        // Add to beginning of array
        this.registeredMeals.unshift(meal);
        
        // Update display
        this.displayMeals();
        
        // Trigger animation for new item
        this.animateNewMeal(meal.id);
    }

    animateNewMeal(mealId) {
        // Add animation class to new meal item
        setTimeout(() => {
            const newMealItem = document.querySelector(`[data-meal-id="${mealId}"]`);
            if (newMealItem) {
                newMealItem.classList.add('new-meal');
                setTimeout(() => {
                    newMealItem.classList.remove('new-meal');
                }, 1000);
            }
        }, 100);
    }

    filterMeals() {
        const searchTerm = this.elements.mealSearch?.value.toLowerCase() || '';
        const categoryFilter = this.elements.categoryFilter?.value || '';
        
        // Get all meal items
        const mealItems = this.elements.registeredMeals?.querySelectorAll('.meal-list-item');
        if (!mealItems) return;
        
        let visibleCount = 0;
        
        mealItems.forEach(item => {
            const mealName = item.dataset.name || '';
            const mealCategory = item.dataset.category || '';
            
            const matchesSearch = !searchTerm || mealName.includes(searchTerm);
            const matchesCategory = !categoryFilter || mealCategory === categoryFilter;
            
            if (matchesSearch && matchesCategory) {
                item.style.display = 'flex';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });
        
        // Show message if no meals match
        if (visibleCount === 0 && this.registeredMeals.length > 0) {
            this.elements.registeredMeals.innerHTML += `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <p>No meals match your search criteria</p>
                    <button class="btn btn-secondary" onclick="restaurantPortal.clearFilters()">
                        Clear Filters
                    </button>
                </div>
            `;
        }
    }

    clearFilters() {
        if (this.elements.mealSearch) this.elements.mealSearch.value = '';
        if (this.elements.categoryFilter) this.elements.categoryFilter.value = '';
        this.filterMeals();
    }

    updateMealsCount() {
        if (this.elements.mealsCount) {
            this.elements.mealsCount.textContent = this.registeredMeals.length;
        }
    }

    showDemoMeals() {
        // Demo data for testing when API is unavailable
        this.registeredMeals = [
            {
                id: 'demo-1',
                name: 'Margherita Pizza',
                description: 'Classic pizza with tomato sauce and mozzarella cheese',
                price: 12.99,
                preparationTime: 25,
                category: 'Main Course',
                restaurantName: 'Demo Italian Restaurant',
                isVegetarian: true,
                isAvailable: true,
                calories: 850
            },
            {
                id: 'demo-2',
                name: 'Chicken Alfredo',
                description: 'Creamy pasta with grilled chicken',
                price: 14.99,
                preparationTime: 20,
                category: 'Main Course',
                restaurantName: 'Demo Italian Restaurant',
                isVegetarian: false,
                isAvailable: true,
                calories: 920
            },
            {
                id: 'demo-3',
                name: 'Chocolate Lava Cake',
                description: 'Warm chocolate cake with molten center',
                price: 7.99,
                preparationTime: 15,
                category: 'Dessert',
                restaurantName: 'Demo Italian Restaurant',
                isVegetarian: true,
                isAvailable: true,
                calories: 450
            }
        ];
        
        this.displayMeals();
        this.updateMealsCount();
        
        showMessage('Using demo data. Real meals will load when connected to server.', 'warning');
    }
}

// Initialize the portal when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on the restaurant page
    if (document.getElementById('mealForm')) {
        window.restaurantPortal = new RestaurantPortal();
    }
});

// Make clearFilters available globally
window.clearFilters = function() {
    if (window.restaurantPortal) {
        window.restaurantPortal.clearFilters();
    }
};