import logging
import json
import azure.functions as func
from azure.data.tables import TableServiceClient
from datetime import datetime
import uuid
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function: Register a new meal
    POST /api/registerMeal
    """
    logging.info('Python HTTP trigger function processed a request.')
    
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
    
    try:
        # Parse request body
        req_body = req.get_json()
        
        # Validate required fields
        required_fields = ['name', 'description', 'price', 'preparationTime', 'deliveryAreas', 'restaurantName']
        missing_fields = []
        for field in required_fields:
            if field not in req_body:
                missing_fields.append(field)
        
        if missing_fields:
            return func.HttpResponse(
                json.dumps({
                    'status': 'error',
                    'message': f"Missing required fields: {', '.join(missing_fields)}"
                }),
                status_code=400,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                }
            )
        
        # Get connection string
        connection_string = os.getenv('AzureStorageConnectionString')
        if not connection_string:
            connection_string = os.getenv('AzureWebJobsStorage')
        
        # Connect to Table Storage
        table_service = TableServiceClient.from_connection_string(connection_string)
        meals_table = table_service.get_table_client('Meals')
        restaurants_table = table_service.get_table_client('Restaurants')
        
        # Generate a unique restaurant ID if not provided
        # In a real app, you'd get this from authentication
        restaurant_id = req_body.get('restaurantId', str(uuid.uuid4()))
        
        # Create or get restaurant
        try:
            restaurant = restaurants_table.get_entity(
                partition_key=req_body.get('area', 'Central'),
                row_key=restaurant_id
            )
            restaurant_name = restaurant.get('Name', req_body['restaurantName'])
        except:
            # Restaurant doesn't exist, create a simple entry
            restaurant_name = req_body['restaurantName']
        
        # Parse delivery areas
        if isinstance(req_body['deliveryAreas'], list):
            delivery_areas = ','.join(req_body['deliveryAreas'])
            primary_area = req_body['deliveryAreas'][0]
        else:
            delivery_areas = req_body['deliveryAreas']
            primary_area = delivery_areas.split(',')[0] if ',' in delivery_areas else delivery_areas
        
        # Create meal entity
        meal_id = str(uuid.uuid4())
        meal_entity = {
            'PartitionKey': restaurant_id,  # Restaurant ID as partition key
            'RowKey': meal_id,
            'Name': req_body['name'],
            'Description': req_body['description'],
            'Price': float(req_body['price']),
            'PreparationTime': int(req_body['preparationTime']),
            'Category': req_body.get('category', 'Main Course'),
            'IsAvailable': req_body.get('isAvailable', True),
            'IsVegetarian': req_body.get('isVegetarian', False),
            'Calories': req_body.get('calories', 0),
            'DeliveryAreas': delivery_areas,
            'DeliveryArea': primary_area,  # Primary area for querying
            'RestaurantName': restaurant_name,
            'RestaurantId': restaurant_id,
            'CreatedDate': datetime.utcnow().isoformat(),
            'ImageUrl': req_body.get('imageUrl', ''),
            'ImageBlobPath': req_body.get('imageBlobPath', '')
        }
        
        # Insert into table
        meals_table.create_entity(meal_entity)
        
        # Return success response
        return func.HttpResponse(
            json.dumps({
                'status': 'success',
                'message': 'Meal registered successfully',
                'mealId': meal_id,
                'restaurantId': restaurant_id,
                'data': {
                    'id': meal_id,
                    'name': meal_entity['Name'],
                    'price': meal_entity['Price'],
                    'category': meal_entity['Category']
                }
            }),
            status_code=201,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )
        
    except Exception as e:
        logging.error(f"Error in registerMeal function: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                'status': 'error',
                'message': f"Server error: {str(e)}"
            }),
            status_code=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )