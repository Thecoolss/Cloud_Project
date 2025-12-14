"""
FOOD ORDER PLATFORM - AZURE TABLE DATA SETUP
Simple script to create tables and populate with realistic data
"""

import os
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError
from faker import Faker
import uuid
import random
from datetime import datetime

class AzureTableSetup:
    def __init__(self, connection_string):
        """Initialize with your Azure Storage connection string"""
        print("🔧 Initializing Azure Table setup...")
        self.connection_string = connection_string
        self.table_service = TableServiceClient.from_connection_string(connection_string)
        self.fake = Faker()
        
        # Define 3 delivery areas (minimum requirement)
        self.delivery_areas = ['Central', 'North', 'South']
        
        # Restaurant types for variety
        self.restaurant_types = [
            'Italian', 'Mexican', 'Chinese', 'Indian', 'American',
            'Japanese', 'Thai', 'Mediterranean', 'Vegetarian', 'Fast Food'
        ]
        
        # Meal data templates
        self.meal_templates = {
            'Italian': [
                ('Margherita Pizza', 12.99, 'Classic pizza with tomato and mozzarella', 20),
                ('Spaghetti Carbonara', 14.50, 'Pasta with eggs, cheese, and pancetta', 25),
                ('Lasagna', 16.75, 'Layered pasta with meat and cheese', 30),
                ('Tiramisu', 8.99, 'Coffee-flavored Italian dessert', 15),
                ('Garlic Bread', 5.99, 'Toasted bread with garlic butter', 10)
            ],
            'Mexican': [
                ('Chicken Burrito', 11.99, 'Grilled chicken with rice and beans', 15),
                ('Beef Tacos', 9.99, 'Three soft tacos with seasoned beef', 12),
                ('Guacamole & Chips', 7.50, 'Fresh avocado dip with tortilla chips', 10),
                ('Enchiladas', 13.99, 'Corn tortillas with chicken and cheese', 20),
                ('Churros', 6.50, 'Fried dough pastry with cinnamon sugar', 10)
            ],
            'Chinese': [
                ('Kung Pao Chicken', 13.99, 'Spicy stir-fried chicken with peanuts', 18),
                ('Vegetable Spring Rolls', 6.99, 'Crispy rolls with vegetables', 12),
                ('Beef Chow Mein', 14.50, 'Stir-fried noodles with beef', 20),
                ('Sweet & Sour Pork', 15.99, 'Crispy pork in tangy sauce', 22),
                ('Egg Fried Rice', 8.99, 'Rice stir-fried with eggs and vegetables', 15)
            ],
            'Indian': [
                ('Chicken Tikka Masala', 16.50, 'Grilled chicken in creamy tomato sauce', 25),
                ('Vegetable Samosa', 5.99, 'Spiced potato filled pastry', 10),
                ('Butter Chicken', 17.99, 'Tender chicken in rich butter sauce', 28),
                ('Garlic Naan', 4.50, 'Leavened bread with garlic butter', 8),
                ('Mango Lassi', 4.99, 'Sweet yogurt drink with mango', 5)
            ],
            'American': [
                ('Classic Cheeseburger', 11.99, 'Beef patty with cheese and veggies', 15),
                ('BBQ Ribs', 18.99, 'Slow-cooked ribs with BBQ sauce', 35),
                ('Caesar Salad', 9.99, 'Romaine lettuce with Caesar dressing', 10),
                ('Buffalo Wings', 12.50, 'Crispy chicken wings with hot sauce', 20),
                ('Chocolate Milkshake', 6.99, 'Creamy chocolate milkshake', 8)
            ]
        }
    
    def create_tables(self):
        """Create the necessary tables in Azure Table Storage"""
        print("\n📊 CREATING TABLES...")
        tables = ['Restaurants', 'Meals', 'Orders']
        
        for table_name in tables:
            try:
                # Create table if it doesn't exist
                table_client = self.table_service.create_table_if_not_exists(table_name)
                print(f"✅ Table '{table_name}' is ready")
            except Exception as e:
                print(f"❌ Error creating table '{table_name}': {e}")
    
    def create_restaurant(self, area, restaurant_number):
        """Create a single restaurant entity"""
        restaurant_type = random.choice(self.restaurant_types)
        
        # Generate realistic restaurant name
        if restaurant_type == 'Italian':
            name = f"{self.fake.last_name()} {random.choice(['Trattoria', 'Ristorante', 'Pizzeria'])}"
        elif restaurant_type == 'Mexican':
            name = f"{random.choice(['El', 'La'])} {self.fake.last_name()} {random.choice(['Cantina', 'Taqueria', 'Restaurante'])}"
        elif restaurant_type == 'Chinese':
            name = f"{random.choice(['Golden', 'Happy', 'Dragon'])} {restaurant_type}"
        else:
            name = f"{self.fake.company()} {restaurant_type}"
        
        return {
            'PartitionKey': area,  # Area as partition key for efficient querying
            'RowKey': str(uuid.uuid4()),  # Unique restaurant ID
            'Name': name,
            'Description': f"{restaurant_type} cuisine specializing in fresh ingredients",
            'CuisineType': restaurant_type,
            'Address': self.fake.street_address(),
            'Phone': self.fake.phone_number(),
            'DeliveryFee': round(random.uniform(0, 4.99), 2),
            'MinOrder': round(random.uniform(10, 20), 2),
            'Rating': round(random.uniform(3.5, 5.0), 1),
            'OpeningHours': '10:00 AM - 10:00 PM',
            'IsActive': True,
            'CreatedDate': datetime.utcnow().isoformat()
        }
    
    def create_meal(self, restaurant, meal_template):
        """Create a single meal entity"""
        name, price, description, prep_time = meal_template
        
        return {
            'PartitionKey': restaurant['RowKey'],  # Restaurant ID as partition key
            'RowKey': str(uuid.uuid4()),  # Unique meal ID
            'Name': name,
            'Description': description,
            'Price': price,
            'PreparationTime': prep_time,
            'Category': self.get_category_from_name(name),
            'IsAvailable': True,
            'IsVegetarian': random.choice([True, False]),
            'Calories': random.randint(300, 1200),
            'CreatedDate': datetime.utcnow().isoformat(),
            'RestaurantId': restaurant['RowKey'],
            'RestaurantName': restaurant['Name'],
            'DeliveryArea': restaurant['PartitionKey']  # Copy area for easy querying
        }
    
    def get_category_from_name(self, meal_name):
        """Determine category based on meal name"""
        meal_name_lower = meal_name.lower()
        if any(word in meal_name_lower for word in ['pizza', 'burger', 'tacos', 'pasta', 'chicken', 'beef', 'fish']):
            return 'Main Course'
        elif any(word in meal_name_lower for word in ['bread', 'rolls', 'samosa', 'wings', 'guacamole']):
            return 'Appetizer'
        elif any(word in meal_name_lower for word in ['cake', 'tiramisu', 'churros', 'dessert']):
            return 'Dessert'
        elif any(word in meal_name_lower for word in ['shake', 'lassi', 'drink']):
            return 'Beverage'
        else:
            return 'Main Course'
    
    def seed_data(self):
        """Main method to seed all data"""
        print("\n🌱 SEEDING DATA...")
        print("=" * 50)
        
        # Step 1: Create tables
        self.create_tables()
        
        # Step 2: Create table clients
        restaurants_client = self.table_service.get_table_client('Restaurants')
        meals_client = self.table_service.get_table_client('Meals')
        
        total_restaurants = 0
        total_meals = 0
        
        # Step 3: Create restaurants and meals for each area
        for area in self.delivery_areas:
            print(f"\n📍 Processing {area} area...")
            
            # Create 10-12 restaurants per area
            restaurants_in_area = []
            for i in range(12):  # 12 restaurants per area (exceeds 10 requirement)
                restaurant = self.create_restaurant(area, i+1)
                restaurants_in_area.append(restaurant)
                
                # Upload restaurant to table
                try:
                    restaurants_client.create_entity(restaurant)
                    total_restaurants += 1
                except ResourceExistsError:
                    # Entity exists, try update
                    restaurants_client.update_entity(restaurant)
                    total_restaurants += 1
                
                # Create meals for this restaurant
                cuisine_type = restaurant['CuisineType']
                if cuisine_type in self.meal_templates:
                    templates = self.meal_templates[cuisine_type]
                else:
                    templates = self.meal_templates['American']  # Default
                
                # Create 5-8 meals per restaurant
                for template in templates[:random.randint(5, 8)]:
                    meal = self.create_meal(restaurant, template)
                    
                    try:
                        meals_client.create_entity(meal)
                        total_meals += 1
                    except ResourceExistsError:
                        meals_client.update_entity(meal)
                        total_meals += 1
            
            print(f"   Added {len(restaurants_in_area)} restaurants with meals")
        
        # Step 4: Print summary
        print("\n" + "=" * 50)
        print("📊 DATA SEEDING COMPLETE")
        print("=" * 50)
        print(f"✅ Delivery Areas: {', '.join(self.delivery_areas)}")
        print(f"✅ Total Restaurants: {total_restaurants}")
        print(f"✅ Total Meals: {total_meals}")
        print(f"✅ Average per area: {total_restaurants/len(self.delivery_areas):.0f} restaurants")
        print(f"✅ Average per restaurant: {total_meals/total_restaurants:.1f} meals")
        print("\n🎯 REQUIREMENTS CHECK:")
        print(f"   ✓ At least 3 delivery areas: {len(self.delivery_areas)} areas")
        print(f"   ✓ At least 10 restaurants per area: {total_restaurants/len(self.delivery_areas):.0f} per area")
        print(f"   ✓ Realistic meal data: {total_meals} meals created")
        
        return total_restaurants, total_meals
    
    def verify_data(self):
        """Quick verification of seeded data"""
        print("\n🔍 VERIFYING DATA...")
        print("-" * 30)
        
        restaurants_client = self.table_service.get_table_client('Restaurants')
        meals_client = self.table_service.get_table_client('Meals')
        
        # Count restaurants by area
        for area in self.delivery_areas:
            query = f"PartitionKey eq '{area}'"
            restaurants = list(restaurants_client.query_entities(query))
            print(f"{area}: {len(restaurants)} restaurants")
            
            # Count meals for first restaurant as sample
            if restaurants:
                restaurant_id = restaurants[0]['RowKey']
                meal_query = f"PartitionKey eq '{restaurant_id}'"
                meals = list(meals_client.query_entities(meal_query))
                print(f"  Sample: {restaurants[0]['Name']} - {len(meals)} meals")
                
                # Show sample meal
                if meals:
                    meal = meals[0]
                    print(f"    Meal: {meal['Name']} - ${meal['Price']} ({meal['Category']})")
        
        # Total counts
        all_restaurants = list(restaurants_client.query_entities("IsActive eq true"))
        all_meals = list(meals_client.query_entities("IsAvailable eq true"))
        
        print(f"\n📈 TOTAL:")
        print(f"Restaurants: {len(all_restaurants)}")
        print(f"Meals: {len(all_meals)}")

def main():
    """Main execution - simple and straightforward"""
    print("""
    🍽️  FOOD ORDER PLATFORM - DATA SETUP
    ===================================
    This script will:
    1. Create Restaurants, Meals, and Orders tables
    2. Populate with realistic restaurant data
    3. Create meal items for each restaurant
    4. Verify all data is properly stored
    ===================================
    """)
    
    # Get connection string
    print("🔑 Step 1: Provide your Azure Storage connection string")
    print("   (Get it from Azure Portal → Storage Account → Access Keys)")
    print("   Format: DefaultEndpointsProtocol=https;AccountName=...")
    print("-" * 50)
    
    connection_string = input("📋 Paste connection string: ").strip()
    
    if not connection_string:
        print("\n❌ No connection string provided. Exiting...")
        return
    
    # Create setup instance
    setup = AzureTableSetup(connection_string)
    
    try:
        # Seed the data
        restaurant_count, meal_count = setup.seed_data()
        
        # Verify
        setup.verify_data()
        
        # Success message
        print(f"""
        \n🎉 SUCCESS! Your Azure Table Storage is now ready.
        =============================================
        NEXT STEPS:
        1. Go to Azure Portal to verify:
           - Navigate to your Storage Account
           - Click 'Tables' in left menu
           - Open 'Restaurants' and 'Meals' tables
           
        2. Test queries:
           - Use Azure Storage Explorer (optional)
           - Or run the test script below
        
        3. Save connection string for later:
           AZURE_STORAGE_CONNECTION_STRING="{connection_string}"
        =============================================
        """)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check your connection string is correct")
        print("2. Ensure Table Storage is enabled on your account")
        print("3. Check network connectivity")

if __name__ == "__main__":
    main()