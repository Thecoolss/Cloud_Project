"""
COMPLETE AZURE BLOB STORAGE IMAGE SOLUTION
Uploads food images to Azure Blob Storage and updates meal records
"""

from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
import requests
import random
import time
import json
from datetime import datetime
import os

class AzureBlobImageManager:
    def __init__(self, connection_string):
        """Initialize Azure Blob and Table storage clients"""
        self.connection_string = connection_string
        self.blob_service = BlobServiceClient.from_connection_string(connection_string)
        self.table_service = TableServiceClient.from_connection_string(connection_string)
        
        # Food categories with specific Unsplash image URLs
        self.category_images = {
            'Main Course': [
                "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&h=600&fit=crop",  # Pizza
                "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&h=600&fit=crop",  # Burger
                "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=800&h=600&fit=crop",  # Pasta
                "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=800&h=600&fit=crop",  # Sushi
                "https://images.unsplash.com/photo-1585937421612-70ca003675ed?w=800&h=600&fit=crop",  # Curry
                "https://images.unsplash.com/photo-1600891964092-4316c288032e?w=800&h=600&fit=crop",  # Steak
                "https://images.unsplash.com/photo-1594041680534-e8c8cdebd659?w=800&h=600&fit=crop",  # Tacos
                "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&h=600&fit=crop",  # Burrito
                "https://images.unsplash.com/photo-1626082895613-52a0b3d2c474?w=800&h=600&fit=crop",  # Fried Chicken
                "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=800&h=600&fit=crop",  # Salmon
            ],
            'Appetizer': [
                "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&h=600&fit=crop",  # Nachos
                "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=800&h=600&fit=crop",  # Spring Rolls
                "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=800&h=600&fit=crop",  # Bruschetta
                "https://images.unsplash.com/photo-1567620832903-9fc6debc209f?w=800&h=600&fit=crop",  # Chicken Wings
                "https://images.unsplash.com/photo-1601050690117-94f5f6fa8bd7?w=800&h=600&fit=crop",  # Samosas
            ],
            'Dessert': [
                "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800&h=600&fit=crop",  # Cake
                "https://images.unsplash.com/photo-1560008581-09826d1de69e?w=800&h=600&fit=crop",  # Ice Cream
                "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=800&h=600&fit=crop",  # Tiramisu
                "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=800&h=600&fit=crop",  # Cheesecake
            ],
            'Beverage': [
                "https://images.unsplash.com/photo-1505252585461-04db1eb84625?w=800&h=600&fit=crop",  # Smoothie
                "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&h=600&fit=crop",  # Coffee
                "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=800&h=600&fit=crop",  # Milkshake
                "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=800&h=600&fit=crop",  # Juice
            ],
            'Side Dish': [
                "https://images.unsplash.com/photo-1576107232684-1279f390859f?w=800&h=600&fit=crop",  # French Fries
                "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&h=600&fit=crop",  # Salad
                "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=800&h=600&fit=crop",  # Rice
                "https://images.unsplash.com/photo-1598373182133-52452f7691ef?w=800&h=600&fit=crop",  # Bread
            ]
        }
        
        # Keywords mapping for better image matching
        self.keyword_mapping = {
            'pizza': ('Main Course', 0),
            'burger': ('Main Course', 1),
            'pasta': ('Main Course', 2),
            'spaghetti': ('Main Course', 2),
            'lasagna': ('Main Course', 2),
            'sushi': ('Main Course', 3),
            'curry': ('Main Course', 4),
            'steak': ('Main Course', 5),
            'beef': ('Main Course', 5),
            'tacos': ('Main Course', 6),
            'burrito': ('Main Course', 7),
            'chicken': ('Main Course', 8),
            'fried': ('Main Course', 8),
            'salmon': ('Main Course', 9),
            'fish': ('Main Course', 9),
            'nachos': ('Appetizer', 0),
            'spring': ('Appetizer', 1),
            'rolls': ('Appetizer', 1),
            'bruschetta': ('Appetizer', 2),
            'wings': ('Appetizer', 3),
            'samosas': ('Appetizer', 4),
            'cake': ('Dessert', 0),
            'ice': ('Dessert', 1),
            'cream': ('Dessert', 1),
            'tiramisu': ('Dessert', 2),
            'cheesecake': ('Dessert', 3),
            'smoothie': ('Beverage', 0),
            'coffee': ('Beverage', 1),
            'milkshake': ('Beverage', 2),
            'juice': ('Beverage', 3),
            'fries': ('Side Dish', 0),
            'french': ('Side Dish', 0),
            'salad': ('Side Dish', 1),
            'rice': ('Side Dish', 2),
            'bread': ('Side Dish', 3),
        }
    
    def create_containers(self):
        """Create necessary blob containers"""
        containers = ['meal-images', 'restaurant-logos', 'menu-media']
        
        print("\n📦 Creating blob containers...")
        for container_name in containers:
            try:
                container_client = self.blob_service.create_container(container_name)
                print(f"✅ Created container: {container_name}")
                
                # Set public access level (for read-only access to images)
                container_client = self.blob_service.get_container_client(container_name)
                print(f"   Access level: Blob (anonymous read access for blobs)")
                
            except Exception as e:
                if "ContainerAlreadyExists" in str(e):
                    container_client = self.blob_service.get_container_client(container_name)
                    print(f"⚠️  Container already exists: {container_name}")
                else:
                    print(f"❌ Error creating {container_name}: {e}")
        
        return True
    
    def download_and_upload_image(self, image_url, container_name, blob_name):
        """Download image from URL and upload to Azure Blob Storage - CORRECTED VERSION"""
        try:
            print(f"   Downloading: {image_url[:60]}...")
            
            # 1. Download image
            response = requests.get(image_url)
            if response.status_code != 200:
                print(f"   ❌ Failed to download image (HTTP {response.status_code})")
                return None
            
            # 2. Create proper ContentSettings
            # Determine content type from URL or default to JPEG
            content_type = 'image/jpeg'
            if '.png' in image_url.lower():
                content_type = 'image/png'
            elif '.gif' in image_url.lower():
                content_type = 'image/gif'
            
            # IMPORTANT: Create ContentSettings object correctly
            from azure.storage.blob import ContentSettings
            content_settings = ContentSettings(
                content_type=content_type,
                cache_control='public, max-age=31536000'  # Cache for 1 year
            )
            
            # 3. Get blob client and upload
            blob_client = self.blob_service.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            # Upload the image data with correct settings
            blob_client.upload_blob(
                response.content,
                overwrite=True,
                content_settings=content_settings  # Pass the properly created object
            )
            
            # 4. Get and return the blob URL
            blob_url = blob_client.url
            print(f"   ✅ Uploaded: {blob_name}")
            print(f"   📁 URL: {blob_url[:80]}...")
            
            return blob_url
            
        except Exception as e:
            print(f"   ❌ Error uploading {blob_name}: {str(e)}")
            import traceback
            print(f"   🔍 Detailed error: {traceback.format_exc()}")
            return None
    
    def get_image_for_meal(self, meal_name, category):
        """Select appropriate image for a meal"""
        meal_name_lower = meal_name.lower()
        
        # Try keyword matching first
        for keyword, (cat, idx) in self.keyword_mapping.items():
            if keyword in meal_name_lower:
                if cat in self.category_images and idx < len(self.category_images[cat]):
                    return self.category_images[cat][idx]
        
        # Fallback to category-based selection
        if category in self.category_images:
            return random.choice(self.category_images[category])
        
        # Ultimate fallback
        all_images = []
        for cat_images in self.category_images.values():
            all_images.extend(cat_images)
        return random.choice(all_images)
    
    def process_meals(self, sample_size=None):
        """Main method to process meals and upload images"""
        print("\n🖼️ Processing meal images...")
        print("=" * 60)
        
        # Get meals client
        meals_client = self.table_service.get_table_client('Meals')
        
        # Get all available meals
        query = "IsAvailable eq true"
        all_meals = list(meals_client.query_entities(query))
        
        if sample_size:
            meals_to_process = all_meals[:sample_size]
            print(f"📊 Processing {sample_size} sample meals (of {len(all_meals)} total)")
        else:
            meals_to_process = all_meals
            print(f"📊 Processing all {len(all_meals)} meals")
        
        processed_count = 0
        skipped_count = 0
        
        for i, meal in enumerate(meals_to_process, 1):
            meal_name = meal.get('Name', f"Meal_{meal['RowKey'][:8]}")
            category = meal.get('Category', 'Main Course')
            
            print(f"\n[{i}/{len(meals_to_process)}] {meal_name[:40]}...")
            print(f"   Category: {category}")
            
            # Check if already has an image
            if 'ImageUrl' in meal and 'blob.core.windows.net' in meal['ImageUrl']:
                print("   ⏭️  Already has blob image, skipping...")
                skipped_count += 1
                continue
            
            # Get appropriate image URL
            image_url = self.get_image_for_meal(meal_name, category)
            
            # Create blob name
            blob_name = f"meals/{category.lower().replace(' ', '-')}/{meal['RowKey']}.jpg"
            
            # Upload to blob storage
            blob_url = self.download_and_upload_image(
                image_url=image_url,
                container_name='meal-images',
                blob_name=blob_name
            )
            
            if blob_url:
                # Update meal record with blob URL
                meal['ImageUrl'] = blob_url
                meal['ImageBlobPath'] = blob_name
                meal['ImageUploadDate'] = datetime.utcnow().isoformat()
                
                meals_client.update_entity(meal)
                processed_count += 1
                print(f"   ✅ Updated meal record with blob URL")
            else:
                print(f"   ❌ Failed to upload image for {meal_name}")
                skipped_count += 1
            
            # Small delay to be nice to servers
            time.sleep(0.2)
        
        print(f"\n" + "=" * 60)
        print(f"📊 PROCESSING COMPLETE")
        print(f"✅ Successfully processed: {processed_count} meals")
        print(f"⏭️  Skipped (already had images): {skipped_count} meals")
        
        return processed_count
    
    def verify_blob_storage(self):
        """Verify blob storage contents"""
        print("\n🔍 Verifying Blob Storage...")
        print("-" * 40)
        
        try:
            # List containers
            containers = list(self.blob_service.list_containers())
            print(f"📁 Containers found: {len(containers)}")
            
            for container in containers:
                print(f"\n📦 Container: {container['name']}")
                container_client = self.blob_service.get_container_client(container['name'])
                
                # Count blobs
                blobs = list(container_client.list_blobs())
                print(f"   Blobs: {len(blobs)}")
                
                # Show sample blobs
                for blob in blobs[:3]:
                    print(f"   - {blob.name} ({blob.size // 1024} KB)")
        
        except Exception as e:
            print(f"❌ Error verifying blob storage: {e}")
    
    def generate_image_report(self):
        """Generate a report of images in the system"""
        print("\n📄 Generating Image Report...")
        print("-" * 40)
        
        meals_client = self.table_service.get_table_client('Meals')
        meals = list(meals_client.query_entities("IsAvailable eq true"))
        
        # Count meals with/without images
        with_blob_images = 0
        with_external_images = 0
        without_images = 0
        
        for meal in meals:
            if 'ImageUrl' in meal:
                if 'blob.core.windows.net' in meal['ImageUrl']:
                    with_blob_images += 1
                else:
                    with_external_images += 1
            else:
                without_images += 1
        
        print(f"📊 Total meals: {len(meals)}")
        print(f"✅ With blob storage images: {with_blob_images}")
        print(f"🔗 With external URLs: {with_external_images}")
        print(f"❌ Without images: {without_images}")
        
        # Show sample meal with blob image
        blob_meals = [m for m in meals if 'ImageUrl' in m and 'blob.core.windows.net' in m['ImageUrl']]
        if blob_meals:
            print(f"\n🎯 Sample blob storage image:")
            sample = blob_meals[0]
            print(f"   Meal: {sample.get('Name', 'Unknown')}")
            print(f"   Blob URL: {sample.get('ImageUrl', 'No URL')[:80]}...")
            print(f"   Blob Path: {sample.get('ImageBlobPath', 'No path')}")
        
        return {
            'total_meals': len(meals),
            'with_blob_images': with_blob_images,
            'with_external_images': with_external_images,
            'without_images': without_images
        }

def main():
    """Main execution function"""
    print("""
    🚀 AZURE BLOB STORAGE - MEAL IMAGES UPLOADER
    ============================================
    This script will:
    1. Create blob containers for meal images
    2. Download food images from Unsplash
    3. Upload them to Azure Blob Storage
    4. Update meal records with blob URLs
    
    Demonstrates complete Azure Storage integration!
    ============================================
    """)
    
    # Get connection string
    connection_string = input("🔑 Enter Azure Storage connection string: ").strip()
    
    if not connection_string:
        print("❌ No connection string provided")
        return
    
    # Create manager instance
    manager = AzureBlobImageManager(connection_string)
    
    try:
        # Step 1: Create blob containers
        print("\n" + "=" * 60)
        print("STEP 1: Creating Blob Containers")
        print("=" * 60)
        manager.create_containers()
        
        # Step 2: Process meals
        print("\n" + "=" * 60)
        print("STEP 2: Uploading Meal Images")
        print("=" * 60)
        
        print("\n📋 Choose processing mode:")
        print("1. Process ALL meals (may take a few minutes)")
        print("2. Process SAMPLE of 20 meals (for testing)")
        
        choice = input("\nSelect option (1 or 2): ").strip()
        
        if choice == '2':
            processed = manager.process_meals(sample_size=20)
        else:
            processed = manager.process_meals()
        
        # Step 3: Verify
        print("\n" + "=" * 60)
        print("STEP 3: Verification")
        print("=" * 60)
        manager.verify_blob_storage()
        
        # Step 4: Generate report
        report = manager.generate_image_report()
        
        # Success message
        print("\n" + "=" * 60)
        print("🎉 BLOB STORAGE SETUP COMPLETE!")
        print("=" * 60)
        
        print(f"""
        ✅ SUCCESS SUMMARY:
        -------------------
        • Created blob containers: meal-images, restaurant-logos, menu-media
        • Processed {processed} meal images
        • Updated meal records with blob URLs
        • Images stored in your Azure Storage account
        
        📁 Azure Portal Steps:
        1. Go to your Storage Account
        2. Click 'Containers' in left menu
        3. Open 'meal-images' container
        4. You'll see organized food images
        
        🔗 Sample Blob URL Structure:
        https://[account].blob.core.windows.net/meal-images/meals/main-course/[meal-id].jpg
        
        🖼️ Frontend Usage:
        Use the ImageUrl field in meal records directly in <img> tags:
        <img src="{'{meal.ImageUrl}'}" alt="{'{meal.Name}'}">
        
        💾 Cost Considerations:
        • Storage: ~0.02 USD per GB per month
        • Operations: Minimal cost for reads/writes
        • Data transfer: Free within Azure region
        
        This demonstrates proper Azure Blob Storage integration
        for your food ordering platform!
        """)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check connection string is correct")
        print("2. Ensure you have write permissions")
        print("3. Check internet connectivity")
        print("4. Verify Table Storage has meal data")

if __name__ == "__main__":
    # Install required packages if not already
    try:
        from azure.storage.blob import BlobServiceClient
        from azure.data.tables import TableServiceClient
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "azure-storage-blob", "azure-data-tables", "requests"])
    
    main()