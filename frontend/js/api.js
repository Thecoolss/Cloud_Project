/**
 * API COMMUNICATION LAYER
 * Handles all communication with Azure Functions backend
 */

// CONFIGURATION - UPDATE THIS WITH YOUR AZURE FUNCTIONS URL
const API_BASE_URL = 'https://clood-functions-619.azurewebsites.net/api';
// Example: https://foodorder-functions-1234.azurewebsites.net/api

// Headers for all API requests
const API_HEADERS = {
    'Content-Type': 'application/json',
};

class FoodOrderAPI {
    /**
     * Test API connection
     * @returns {Promise<boolean>} True if connection successful
     */
    static async testConnection() {
        try {
            console.log('🔗 Testing API connection...');
            
            const response = await fetch(`${API_BASE_URL}/meals?area=Central`, {
                method: 'GET',
                headers: API_HEADERS
            });
            
            const connected = response.ok;
            console.log(connected ? '✅ API connection successful' : '❌ API connection failed');
            return connected;
            
        } catch (error) {
            console.error('❌ API connection test failed:', error);
            return false;
        }
    }

    /**
     * Get meals by delivery area
     * @param {string} area - Delivery area (Central, North, South, etc.)
     * @returns {Promise<Array>} Array of meal objects
     */
    static async getMealsByArea(area) {
        try {
            console.log(`📡 Fetching meals for area: ${area}`);
            
            const response = await fetch(`${API_BASE_URL}/meals?area=${encodeURIComponent(area)}`, {
                method: 'GET',
                headers: API_HEADERS
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${await response.text()}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'error') {
                throw new Error(data.message);
            }
            
            console.log(`✅ Found ${data.count || 0} meals in ${area}`);
            return data.meals || [];
            
        } catch (error) {
            console.error('❌ Error fetching meals:', error);
            throw error;
        }
    }

    /**
     * Register a new meal (Restaurant function)
     * @param {Object} mealData - Meal information
     * @returns {Promise<Object>} Created meal with ID
     */
    static async registerMeal(mealData) {
        try {
            console.log('📡 Registering new meal:', mealData.name);
            
            // Get selected delivery areas
            const deliveryAreas = Array.from(document.querySelectorAll('input[name="deliveryArea"]:checked'))
                .map(checkbox => checkbox.value);
            
            if (deliveryAreas.length === 0) {
                throw new Error('Please select at least one delivery area');
            }
            
            const mealPayload = {
                name: mealData.name,
                description: mealData.description,
                price: parseFloat(mealData.price),
                preparationTime: parseInt(mealData.preparationTime),
                deliveryAreas: deliveryAreas,
                restaurantName: mealData.restaurantName,
                category: mealData.category,
                isVegetarian: mealData.isVegetarian || false,
                isAvailable: mealData.isAvailable !== false,
                calories: mealData.calories || 0
            };
            
            const response = await fetch(`${API_BASE_URL}/registerMeal`, {
                method: 'POST',
                headers: API_HEADERS,
                body: JSON.stringify(mealPayload)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${await response.text()}`);
            }
            
            const result = await response.json();
            
            if (result.status === 'error') {
                throw new Error(result.message);
            }
            
            console.log('✅ Meal registered successfully:', result.mealId);
            return result;
            
        } catch (error) {
            console.error('❌ Error registering meal:', error);
            throw error;
        }
    }

    /**
     * Submit an order (Customer function)
     * @param {Object} orderData - Order information
     * @returns {Promise<Object>} Order confirmation
     */
    static async submitOrder(orderData) {
        try {
            console.log('📡 Submitting order for:', orderData.customerName);
            
            const response = await fetch(`${API_BASE_URL}/submitOrder`, {
                method: 'POST',
                headers: API_HEADERS,
                body: JSON.stringify(orderData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${await response.text()}`);
            }
            
            const result = await response.json();
            
            if (result.status === 'error') {
                throw new Error(result.message);
            }
            
            console.log('✅ Order submitted successfully:', result.orderNumber);
            return result;
            
        } catch (error) {
            console.error('❌ Error submitting order:', error);
            throw error;
        }
    }

    /**
     * Get recent registered meals (for restaurant dashboard)
     * @returns {Promise<Array>} Array of recent meals
     */
    static async getRecentMeals() {
        try {
            // This would query all meals for the restaurant
            // For now, we'll get all meals and filter client-side
            const response = await fetch(`${API_BASE_URL}/meals?area=Central`, {
                method: 'GET',
                headers: API_HEADERS
            });
            
            if (!response.ok) {
                return [];
            }
            
            const data = await response.json();
            return data.meals || [];
            
        } catch (error) {
            console.error('❌ Error fetching recent meals:', error);
            return [];
        }
    }
}

// Make API available globally
window.FoodOrderAPI = FoodOrderAPI;

// Helper function to show messages
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        <span>${message}</span>
        <button class="close-message">&times;</button>
    `;
    
    // Add to top of page
    document.body.prepend(messageDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
    
    // Close button
    messageDiv.querySelector('.close-message').addEventListener('click', () => {
        messageDiv.remove();
    });
}

// Make showMessage available globally
window.showMessage = showMessage;