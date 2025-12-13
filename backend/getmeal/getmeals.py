import logging
import json
import azure.functions as func
from azure.data.tables import TableServiceClient
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function: Get meals by delivery area
    GET /api/meals?area=Central
    """
    logging.info('Python HTTP trigger function processed a request.')
    
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
    
    try:
        # Get query parameter
        area = req.params.get('area')
        if not area:
            return func.HttpResponse(
                json.dumps({"error": "Please provide an 'area' parameter"}),
                status_code=400,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )
        
        # Get connection string from environment
        connection_string = os.getenv('AzureStorageConnectionString')
        if not connection_string:
            connection_string = os.getenv('AzureWebJobsStorage')
        
        # Connect to Table Storage
        table_service = TableServiceClient.from_connection_string(connection_string)
        meals_table = table_service.get_table_client('Meals')
        
        # Query meals for the specified area
        # Note: We're querying by DeliveryArea property
        query_filter = f"DeliveryArea eq '{area}' and IsAvailable eq true"
        entities = meals_table.query_entities(query_filter)
        
        # Format the response
        meals = []
        for entity in entities:
            meal_data = {
                'id': entity['RowKey'],
                'name': entity.get('Name', 'Unknown'),
                'description': entity.get('Description', ''),
                'price': float(entity.get('Price', 0)),
                'preparationTime': int(entity.get('PreparationTime', 0)),
                'category': entity.get('Category', 'Main Course'),
                'restaurantId': entity.get('PartitionKey', ''),
                'restaurantName': entity.get('RestaurantName', 'Unknown Restaurant'),
                'area': entity.get('DeliveryArea', area),
                'isVegetarian': entity.get('IsVegetarian', False),
                'calories': entity.get('Calories', 0),
                'imageUrl': entity.get('ImageUrl', '')
            }
            
            # Add blob path if exists
            if 'ImageBlobPath' in entity:
                meal_data['imageBlobPath'] = entity['ImageBlobPath']
            
            meals.append(meal_data)
        
        # Return response
        return func.HttpResponse(
            json.dumps({
                'status': 'success',
                'area': area,
                'count': len(meals),
                'meals': meals
            }, default=str),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )
        
    except Exception as e:
        logging.error(f"Error in getMeals function: {str(e)}")
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