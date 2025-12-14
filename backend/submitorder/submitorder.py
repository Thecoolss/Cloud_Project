import logging
import json
import azure.functions as func
from azure.data.tables import TableServiceClient
from azure.storage.queue import QueueClient
from azure.core.exceptions import ResourceExistsError
from datetime import datetime
import uuid
import os


def _get_storage_connection_string() -> str:
    """
    Retrieve the storage connection string from configuration.
    """
    connection_string = os.getenv('AzureWebJobsStorage') or os.getenv('AzureStorageConnectionString')
    if not connection_string:
        raise RuntimeError("Storage connection string is not configured.")
    return connection_string


def _ensure_queue(queue_name: str, connection_string: str) -> QueueClient:
    """
    Get a QueueClient and create the queue if it does not exist.
    """
    queue_client = QueueClient.from_connection_string(connection_string, queue_name=queue_name)
    try:
        queue_client.create_queue()
    except ResourceExistsError:
        pass
    return queue_client


def _send_invalid_order(reason: str, order_payload: dict) -> None:
    """
    Send invalid requests to the dedicated queue for later inspection.
    """
    try:
        connection_string = _get_storage_connection_string()
        queue_client = _ensure_queue("invalid-orders", connection_string)
        queue_client.send_message(json.dumps({
            'id': str(uuid.uuid4()),
            'reason': reason,
            'orderData': order_payload,
            'timestamp': datetime.utcnow().isoformat()
        }))
        logging.info("Sent invalid order to queue: %s", reason)
    except Exception as queue_error:
        logging.error("Failed to record invalid order: %s", queue_error)


def _enqueue_preparing_notification(order_payload: dict) -> None:
    """
    Enqueue a notification for the order with a 15 second delay so a queue-triggered
    function can notify the user via Azure Notification Hubs.
    """
    try:
        connection_string = _get_storage_connection_string()
        queue_client = _ensure_queue("order-notifications", connection_string)
        queue_client.send_message(
            json.dumps(order_payload),
            visibility_timeout=15  # delay notification
        )
        logging.info("Enqueued order notification for order %s", order_payload.get("orderNumber"))
    except Exception as queue_error:
        logging.error("Failed to enqueue notification: %s", queue_error)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function: Submit a customer order
    POST /api/submitOrder
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
        
        # Validate required fields (treat missing or empty values as invalid)
        required_fields = ['customerName', 'deliveryAddress', 'area', 'meals']
        missing_fields = [field for field in required_fields if not req_body.get(field)]
        
        if missing_fields:
            _send_invalid_order(
                reason=f"Missing required fields: {', '.join(missing_fields)}",
                order_payload=req_body
            )
            
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
        
        # Validate meals array
        if not isinstance(req_body['meals'], list) or len(req_body['meals']) == 0:
            reason = "Meals must be a non-empty array"
            _send_invalid_order(reason=reason, order_payload=req_body)
            
            return func.HttpResponse(
                json.dumps({
                    'status': 'error',
                    'message': reason
                }),
                status_code=400,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                }
            )
        
        # Get connection string
        connection_string = _get_storage_connection_string()
        
        # Connect to Table Storage
        table_service = TableServiceClient.from_connection_string(connection_string)
        meals_table = table_service.get_table_client('Meals')
        orders_table = table_service.get_table_client('Orders')
        
        # Calculate order details
        total_cost = 0.0
        total_preparation_time = 0
        meal_details = []
        restaurant_ids = set()
        
        for meal_item in req_body['meals']:
            try:
                # Get meal details from database
                # Note: We need to know which restaurant this meal belongs to
                # For simplicity, we'll search for the meal
                meal_id = meal_item.get('mealId')
                quantity = meal_item.get('quantity', 1)
                
                # In a real app, you'd have the restaurant ID
                # For now, we'll get the first meal that matches
                meals = list(meals_table.query_entities(f"RowKey eq '{meal_id}'"))
                
                if meals:
                    meal = meals[0]
                    meal_price = float(meal.get('Price', 0))
                    meal_prep_time = int(meal.get('PreparationTime', 0))
                    
                    total_cost += meal_price * quantity
                    total_preparation_time += meal_prep_time * quantity
                    restaurant_ids.add(meal.get('PartitionKey', 'unknown'))
                    
                    meal_details.append({
                        'mealId': meal_id,
                        'name': meal.get('Name', 'Unknown'),
                        'price': meal_price,
                        'quantity': quantity,
                        'preparationTime': meal_prep_time,
                        'restaurantName': meal.get('RestaurantName', 'Unknown')
                    })
                else:
                    logging.warning(f"Meal not found: {meal_id}")
                    
            except Exception as e:
                logging.error(f"Error processing meal item: {e}")
        
        # Calculate delivery time
        fixed_pickup_time = 10  # minutes
        fixed_delivery_time = 20  # minutes
        estimated_delivery = total_preparation_time + fixed_pickup_time + fixed_delivery_time
        
        # Generate order details
        order_id = str(uuid.uuid4())
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{order_id[:6].upper()}"
        
        # Create order entity
        order_entity = {
            'PartitionKey': req_body['area'],
            'RowKey': order_id,
            'CustomerName': req_body['customerName'],
            'DeliveryAddress': req_body['deliveryAddress'],
            'Area': req_body['area'],
            'Phone': req_body.get('phoneNumber', ''),
            'SpecialInstructions': req_body.get('specialInstructions', ''),
            'Meals': json.dumps(meal_details),
            'TotalCost': total_cost,
            'TotalPreparationTime': total_preparation_time,
            'EstimatedDeliveryTime': estimated_delivery,
            'OrderDate': datetime.utcnow().isoformat(),
            'Status': 'Pending',
            'OrderNumber': order_number,
            'RestaurantIds': ','.join(restaurant_ids) if restaurant_ids else 'unknown'
        }
        
        # Save to Orders table
        orders_table.create_entity(order_entity)

        # Queue a notification to be sent after a short delay
        notification_message = {
            'orderId': order_id,
            'orderNumber': order_number,
            'customerName': req_body['customerName'],
            'area': req_body['area'],
            'status': 'Preparing',
            'message': f"Your order {order_number} is being prepared.",
            'timestamp': datetime.utcnow().isoformat()
        }
        _enqueue_preparing_notification(notification_message)
        
        # Return success response
        return func.HttpResponse(
            json.dumps({
                'status': 'success',
                'message': 'Order submitted successfully',
                'orderId': order_id,
                'orderNumber': order_number,
                'totalCost': total_cost,
                'estimatedDeliveryTime': estimated_delivery,
                'deliveryTimeFormatted': f"{estimated_delivery} minutes",
                'data': {
                    'customerName': req_body['customerName'],
                    'area': req_body['area'],
                    'mealCount': len(meal_details),
                    'orderDate': order_entity['OrderDate']
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
        logging.error(f"Error in submitOrder function: {str(e)}")
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
