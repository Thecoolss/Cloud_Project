"""
View orders stored in Azure Table Storage.
"""

from azure.data.tables import TableServiceClient
import json
from datetime import datetime

def view_orders():
    print("ORDER VIEWER")
    print("=" * 70)
    
    print("\nEnter your Azure Storage connection string:")
    print("(From Azure Portal > Storage Account > Access Keys)")
    connection_string = input("Connection string: ").strip()
    
    if not connection_string:
        print("Error: No connection string provided")
        return
    
    try:
        table_service = TableServiceClient.from_connection_string(connection_string)
        orders_table = table_service.get_table_client('Orders')
        
        print("\nConnection successful!")
        print("\nFetching orders...")
        orders = list(orders_table.list_entities())
        
        if not orders:
            print("\nNo orders found in the database.")
            print("Orders will appear here after customers submit orders.")
            return
        
        print(f"\nFound {len(orders)} order(s)")
        print("=" * 70)
        
        for i, order in enumerate(orders, 1):
            print(f"\nORDER #{i}")
            print("-" * 70)
            
            print(f"Order Number: {order.get('OrderNumber', 'N/A')}")
            print(f"Order ID: {order.get('RowKey', 'N/A')}")
            
            print(f"\nCustomer: {order.get('CustomerName', 'N/A')}")
            print(f"Phone: {order.get('Phone', 'N/A')}")
            print(f"Area: {order.get('Area', 'N/A')}")
            print(f"Address: {order.get('DeliveryAddress', 'N/A')}")
            
            instructions = order.get('SpecialInstructions', '')
            if instructions:
                print(f"Special Instructions: {instructions}")
            
            print(f"\nTotal Cost: ${order.get('TotalCost', 0):.2f}")
            print(f"Preparation Time: {order.get('TotalPreparationTime', 0)} minutes")
            print(f"Estimated Delivery: {order.get('EstimatedDeliveryTime', 0)} minutes")
            print(f"Order Date: {order.get('OrderDate', 'N/A')}")
            print(f"Status: {order.get('Status', 'N/A')}")
            
            meals_json = order.get('Meals', '[]')
            try:
                meals = json.loads(meals_json)
                print(f"\nOrdered Items ({len(meals)}):")
                for j, meal in enumerate(meals, 1):
                    print(f"   {j}. {meal.get('name', 'Unknown')}")
                    print(f"      Quantity: {meal.get('quantity', 1)}")
                    print(f"      Price: ${meal.get('price', 0):.2f} each")
                    print(f"      Prep Time: {meal.get('preparationTime', 0)} min")
                    print(f"      Restaurant: {meal.get('restaurantName', 'Unknown')}")
                    if j < len(meals):
                        print()
            except json.JSONDecodeError:
                print(f"\nMeals: {meals_json}")
            
            restaurant_ids = order.get('RestaurantIds', '')
            if restaurant_ids:
                print(f"\nRestaurant IDs: {restaurant_ids}")
            
            print("-" * 70)
        
        print(f"\n" + "=" * 70)
        print("ORDER STATISTICS")
        print("=" * 70)
        
        area_counts = {}
        total_revenue = 0
        statuses = {}
        
        for order in orders:
            area = order.get('Area', 'Unknown')
            area_counts[area] = area_counts.get(area, 0) + 1
            total_revenue += order.get('TotalCost', 0)
            status = order.get('Status', 'Unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"\nOrders by Area:")
        for area, count in sorted(area_counts.items()):
            print(f"   {area}: {count} order(s)")
        
        print(f"\nOrders by Status:")
        for status, count in sorted(statuses.items()):
            print(f"   {status}: {count} order(s)")
        
        print(f"\nTotal Revenue: ${total_revenue:.2f}")
        
        avg_order = total_revenue / len(orders) if orders else 0
        print(f"Average Order Value: ${avg_order:.2f}")
        
        if orders:
            dates = [order.get('OrderDate', '') for order in orders if order.get('OrderDate')]
            if dates:
                dates.sort()
                print(f"\nDate Range:")
                print(f"   First Order: {dates[0]}")
                print(f"   Latest Order: {dates[-1]}")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Check connection string format")
        print("2. Ensure Table Storage is enabled")
        print("3. Verify Orders table exists")
        print("4. Try regenerating access keys in Azure Portal")

def export_orders_to_file():
    """Export orders to a JSON file."""
    print("\nEXPORT ORDERS TO FILE")
    print("=" * 70)
    
    connection_string = input("Connection string: ").strip()
    
    if not connection_string:
        print("Error: No connection string provided")
        return
    
    try:
        table_service = TableServiceClient.from_connection_string(connection_string)
        orders_table = table_service.get_table_client('Orders')
        
        orders = list(orders_table.list_entities())
        
        if not orders:
            print("No orders to export")
            return
        
        orders_data = []
        for order in orders:
            order_dict = {
                'orderNumber': order.get('OrderNumber'),
                'orderId': order.get('RowKey'),
                'customerName': order.get('CustomerName'),
                'phone': order.get('Phone'),
                'area': order.get('Area'),
                'address': order.get('DeliveryAddress'),
                'specialInstructions': order.get('SpecialInstructions'),
                'totalCost': order.get('TotalCost'),
                'prepTime': order.get('TotalPreparationTime'),
                'deliveryTime': order.get('EstimatedDeliveryTime'),
                'orderDate': order.get('OrderDate'),
                'status': order.get('Status'),
                'meals': json.loads(order.get('Meals', '[]')),
                'restaurantIds': order.get('RestaurantIds')
            }
            orders_data.append(order_dict)
        
        filename = f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(orders_data, f, indent=2)
        
        print(f"\nExported {len(orders)} orders to: {filename}")
        
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    print("\nSELECT AN OPTION:")
    print("1. View orders in terminal")
    print("2. Export orders to JSON file")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        view_orders()
    elif choice == "2":
        export_orders_to_file()
    elif choice == "3":
        view_orders()
        print("\n")
        export_orders_to_file()
    else:
        print("Invalid choice")

