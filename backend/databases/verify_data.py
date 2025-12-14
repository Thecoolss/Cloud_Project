"""
QUICK VERIFICATION SCRIPT
Run this to check your data without clicking in Azure Portal
"""

from azure.data.tables import TableServiceClient

def verify_data():
    print("🔍 QUICK DATA VERIFICATION")
    print("=" * 50)
    
    # Get your connection string
    print("\n📋 Step 1: Enter your connection string")
    print("(From Azure Portal → Storage Account → Access Keys)")
    connection_string = input("Connection string: ").strip()
    
    if not connection_string:
        print("❌ No connection string provided")
        return
    
    try:
        # Connect to tables
        table_service = TableServiceClient.from_connection_string(connection_string)
        
        # Get table clients
        restaurants_client = table_service.get_table_client('Restaurants')
        meals_client = table_service.get_table_client('Meals')
        
        print("\n✅ Connection successful!")
        
        # Count restaurants by area
        print("\n📊 RESTAURANT COUNT BY AREA:")
        areas = ['Central', 'North', 'South']
        
        for area in areas:
            query = f"PartitionKey eq '{area}'"
            restaurants = list(restaurants_client.query_entities(query))
            print(f"  {area}: {len(restaurants)} restaurants")
            
            # Show first restaurant in each area
            if restaurants:
                first_restaurant = restaurants[0]
                print(f"    Sample: {first_restaurant.get('Name', 'No name')}")
        
        # Count total restaurants
        all_restaurants = list(restaurants_client.query_entities("IsActive eq true"))
        print(f"\n📈 TOTAL RESTAURANTS: {len(all_restaurants)}")
        
        # Count meals
        print("\n🍛 MEAL COUNT:")
        all_meals = list(meals_client.query_entities("IsAvailable eq true"))
        print(f"  Total Meals: {len(all_meals)}")
        
        # Count by category
        categories = {}
        for meal in all_meals[:100]:  # Check first 100 meals
            cat = meal.get('Category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📋 MEAL CATEGORIES:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} meals")
        
        # Show sample meals
        print("\n🎯 SAMPLE MEALS (first 5):")
        for i, meal in enumerate(all_meals[:5]):
            print(f"  {i+1}. {meal.get('Name', 'No name')}")
            print(f"     Price: ${meal.get('Price', 0):.2f}")
            print(f"     Restaurant: {meal.get('RestaurantName', 'Unknown')[:30]}...")
            print(f"     Area: {meal.get('DeliveryArea', 'Unknown')}")
            print()
        
        # Verify requirements
        print("\n" + "=" * 50)
        print("✅ REQUIREMENTS VERIFICATION:")
        
        total_restaurants = len(all_restaurants)
        if total_restaurants >= 30:
            print(f"✓ At least 30 restaurants: {total_restaurants}")
        else:
            print(f"✗ Need 30 restaurants, have: {total_restaurants}")
        
        total_meals = len(all_meals)
        if total_meals >= 150:
            print(f"✓ At least 150 meals: {total_meals}")
        else:
            print(f"✗ Need 150 meals, have: {total_meals}")
        
        # Check each area has at least 10 restaurants
        print("\n📍 AREA DISTRIBUTION CHECK:")
        for area in areas:
            query = f"PartitionKey eq '{area}'"
            count = len(list(restaurants_client.query_entities(query)))
            if count >= 10:
                print(f"✓ {area}: {count} restaurants (meets 10+ requirement)")
            else:
                print(f"✗ {area}: {count} restaurants (needs 10+)")
        
        print("\n" + "=" * 50)
        print("🎉 VERIFICATION COMPLETE!")
        
        if total_restaurants >= 30 and total_meals >= 150:
            print("✅ ALL REQUIREMENTS MET!")
        else:
            print("⚠️  Some requirements not met. Run the seeding script again.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 TROUBLESHOOTING:")
        print("1. Check connection string format")
        print("2. Ensure Table Storage is enabled")
        print("3. Try regenerating access keys")

if __name__ == "__main__":
    verify_data()