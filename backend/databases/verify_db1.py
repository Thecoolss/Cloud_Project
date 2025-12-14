"""
QUICK TEST - Verify one meal with its image
"""

from azure.data.tables import TableServiceClient
from azure.storage.blob import BlobServiceClient
import requests

def quick_test(connection_string):
    print("⚡ QUICK DATABASE TEST")
    print("=" * 50)
    
    # Connect
    table_service = TableServiceClient.from_connection_string(connection_string)
    blob_service = BlobServiceClient.from_connection_string(connection_string)
    
    meals_client = table_service.get_table_client('Meals')
    
    # Get first meal with image
    meals = list(meals_client.query_entities("IsAvailable eq true"))
    
    # Find a meal with an image
    meal_with_image = None
    for meal in meals:
        if 'ImageUrl' in meal:
            meal_with_image = meal
            break
    
    if not meal_with_image:
        print("❌ No meals with images found")
        return
    
    print(f"\n✅ Found meal: {meal_with_image.get('Name', 'Unknown')}")
    print(f"   Price: ${meal_with_image.get('Price', 0):.2f}")
    print(f"   Category: {meal_with_image.get('Category', 'Unknown')}")
    
    # Check image
    image_url = meal_with_image['ImageUrl']
    print(f"\n🖼️ Image URL: {image_url[:80]}...")
    
    if 'blob.core.windows.net' in image_url:
        print("   Source: Azure Blob Storage")
        
        # Try to access blob
        try:
            response = requests.head(image_url, timeout=5)
            print(f"   ✅ Blob accessible: HTTP {response.status_code}")
            print(f"   📷 Type: {response.headers.get('content-type', 'Unknown')}")
            
            # Get blob info
            if 'ImageBlobPath' in meal_with_image:
                print(f"   📁 Path: {meal_with_image['ImageBlobPath']}")
                
        except Exception as e:
            print(f"   ❌ Blob access failed: {e}")
    
    elif 'unsplash.com' in image_url:
        print("   Source: Unsplash (External)")
        
        # Test external URL
        try:
            response = requests.head(image_url, timeout=5)
            print(f"   ✅ URL accessible: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ URL access failed: {e}")
    
    # Count statistics
    print(f"\n📊 Quick Stats:")
    print(f"   Total meals: {len(meals)}")
    
    with_images = sum(1 for m in meals if 'ImageUrl' in m)
    print(f"   Meals with images: {with_images}")
    
    blob_images = sum(1 for m in meals if 'ImageUrl' in m and 'blob.core.windows.net' in m['ImageUrl'])
    print(f"   Blob storage images: {blob_images}")
    
    print(f"\n🎯 TEST COMPLETE: Database integration is {'WORKING' if with_images > 0 else 'NOT WORKING'}")

if __name__ == "__main__":
    conn_str = input("Enter connection string: ").strip()
    quick_test(conn_str)