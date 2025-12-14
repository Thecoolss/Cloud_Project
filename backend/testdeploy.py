"""
Test script for Azure Functions
Run this to verify your functions work correctly
"""

import requests
import json
import sys

def test_functions(base_url):
    """Test all Azure Functions endpoints"""
    print("🧪 Testing Azure Functions")
    print("=" * 50)
    
    # Test 1: Get meals for Central area
    print("\n1. Testing GET /api/meals?area=Central")
    try:
        response = requests.get(f"{base_url}/meals?area=Central", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Found {data.get('count', 0)} meals")
            
            if data.get('meals'):
                print(f"   📊 Sample meal: {data['meals'][0]['name']} - ${data['meals'][0]['price']}")
            else:
                print("   ⚠️ No meals returned")
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Register a meal
    print("\n2. Testing POST /api/registerMeal")
    try:
        meal_data = {
            "name": "Test Burger",
            "description": "A delicious test burger",
            "price": 12.99,
            "preparationTime": 20,
            "deliveryAreas": ["Central", "North"],
            "restaurantName": "Test Restaurant",
            "category": "Main Course",
            "isAvailable": True
        }
        
        response = requests.post(
            f"{base_url}/registerMeal",
            json=meal_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Success! Meal ID: {data.get('mealId')}")
            TEST_MEAL_ID = data.get('mealId')
        else:
            print(f"   ❌ Failed: {response.text}")
            TEST_MEAL_ID = None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        TEST_MEAL_ID = None
    
    # Test 3: Submit an order
    print("\n3. Testing POST /api/submitOrder")
    try:
        order_data = {
            "customerName": "Test Customer",
            "deliveryAddress": "123 Test St, Test City",
            "area": "Central",
            "phoneNumber": "555-0123",
            "meals": [
                {"mealId": TEST_MEAL_ID or "test-id", "quantity": 1}
            ] if TEST_MEAL_ID else [
                {"mealId": "test-meal-1", "quantity": 2}
            ]
        }
        
        response = requests.post(
            f"{base_url}/submitOrder",
            json=order_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Success! Order Number: {data.get('orderNumber')}")
            print(f"   💰 Total: ${data.get('totalCost', 0):.2f}")
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testing complete!")

def main():
    """Main function"""
    print("Azure Functions Tester")
    print("=" * 50)
    
    # Get base URL
    print("\nEnter the base URL of your Azure Functions")
    print("Examples:")
    print("  For local testing: http://localhost:7071/api")
    print("  For Azure: https://your-function-app.azurewebsites.net/api")
    
    base_url = input("\nBase URL (without trailing slash): ").strip()
    
    if not base_url:
        print("❌ No URL provided")
        sys.exit(1)
    
    # Test the functions
    test_functions(base_url)
    
    # Show next steps
    print("\n📋 Next steps for your frontend:")
    print(f"   const API_BASE_URL = '{base_url}'")
    print("\n📁 Update your frontend JavaScript with this URL")

if __name__ == "__main__":
    main()