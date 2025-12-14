# Cloud Project – Food Ordering on Azure

End-to-end food ordering prototype built on Azure Functions with Table Storage, Queues, Blob Storage helpers, and Notification Hubs. The backend is a set of Python Azure Functions; the frontend is a static HTML/JS client that calls the APIs.

## Architecture Overview
- **Azure Functions (Python)** – HTTP triggers for meals and orders; queue trigger for delayed notifications.
- **Azure Storage Account**
  - **Table Storage**: `Restaurants`, `Meals`, `Orders` tables hold all business data.
  - **Queue Storage**: `invalid-orders` captures bad requests; `order-notifications` drives delayed user notifications.
  - **Blob Storage** (scripts): used by helper scripts to host meal images.
- **Azure Notification Hubs** – Broadcast push/templated notifications to clients seconds after an order is placed.
- **Static Frontend** – `/frontend` HTML/CSS/JS calling the Functions endpoints (`/api/...`).

## Backend Functions

### registerMeal (HTTP trigger) – `POST /api/registerMeal`
- Validates required fields (`name`, `description`, `price`, `preparationTime`, `deliveryAreas`, `restaurantName`).
- Writes a meal entity to the `Meals` table (PartitionKey = restaurantId, RowKey = mealId).
- Generates a restaurantId if not provided; normalizes delivery areas and stores a primary area for querying.

### getMeals (HTTP trigger) – `GET /api/meals?area=Central`
- Requires `area` query param.
- Queries `Meals` by `DeliveryArea` and `IsAvailable=true`.
- Returns meal metadata, pricing, prep time, and optional blob path/image URL.

### submitOrder (HTTP trigger) – `POST /api/submitOrder`
- Validates required fields (`customerName`, `deliveryAddress`, `area`, `meals`); empties are treated as missing.
- If invalid, sends the payload + reason to the `invalid-orders` queue and returns 400.
- Looks up each requested meal in `Meals`, aggregates totals, and creates an `Orders` entity:
  - PartitionKey = area; RowKey = orderId; stores customer info, meals JSON, totals, prep estimate, and restaurants.
- Enqueues an `order-notifications` message with a 15s visibility delay so a separate function can notify the user that the order is “Preparing”.

### notifyorder (Queue trigger) – `order-notifications`
- Triggered by messages from `order-notifications` queue.
- Builds a SAS token from Notification Hub credentials and calls the Notification Hubs REST API.
- Sends a templated/broadcast notification: “Your order {orderNumber} is being prepared.”

## Data Model (Azure Table Storage)
- **Restaurants**: PartitionKey = delivery area; RowKey = restaurantId. Metadata: name, cuisine, address, phone, delivery fee, rating, etc.
- **Meals**: PartitionKey = restaurantId; RowKey = mealId. Fields: name, description, price, prep time, category, availability, calories, delivery area, restaurant metadata, image URL/blob path.
- **Orders**: PartitionKey = area; RowKey = orderId. Fields: customer info, meals (JSON array), totals, preparation/delivery estimates, status, order number, restaurant IDs.

## Queues and Message Shapes
- **invalid-orders** (from `submitOrder` on validation failure)  
  ```json
  {
    "id": "<uuid>",
    "reason": "Missing required fields: area, meals",
    "orderData": { ...original payload... },
    "timestamp": "2025-12-14T15:00:00Z"
  }
  ```
- **order-notifications** (from `submitOrder` on success; 15s delayed visibility)  
  ```json
  {
    "orderId": "...",
    "orderNumber": "ORD-20251214-ABC123",
    "customerName": "...",
    "area": "Central",
    "status": "Preparing",
    "message": "Your order ORD-20251214-ABC123 is being prepared.",
    "timestamp": "2025-12-14T15:00:00Z"
  }
  ```

## Notification Hubs Integration
- Uses REST API (no SDK) with a SAS token derived from the Notification Hub connection string and hub name.
- Environment variables:
  - `AZURE_NOTIFICATION_HUB_CONNECTION_STRING`
  - `AZURE_NOTIFICATION_HUB_NAME`
- `notifyorder` broadcasts a templated payload (`ServiceBusNotification-Format: template`) to all registered devices.

## Helper Scripts (backend/databases)
- **dgenerate.py** – Seeds Table Storage with realistic `Restaurants` and `Meals` (uses Faker). Creates tables if missing.
- **blobl.py** – Uploads food images to Blob Storage containers and annotates meals with image URLs/blob paths.
- **verify_data.py / verify_db1.py** – Quick verification scripts to inspect seeded data and image availability.

## Frontend (static)
- Located in `/frontend` with HTML, CSS, and JS:
  - `js/api.js` defines API helpers.
  - `js/customer.js` and `js/restaurant.js` drive customer and restaurant flows.
  - `restaurant.html` is a sample UI; it calls the Functions endpoints exposed at `/api/...`.
- The frontend assumes CORS is allowed (`Host` settings and Function handlers send `Access-Control-Allow-Origin: *`).

## Configuration
- See `backend/local.settings.json.example` for all required settings:
  - `AzureWebJobsStorage` / `AzureStorageConnectionString`: Storage account for Tables/Queues/Blobs.
  - `FUNCTIONS_WORKER_RUNTIME`: `python`.
  - `AZURE_NOTIFICATION_HUB_CONNECTION_STRING` and `AZURE_NOTIFICATION_HUB_NAME`: needed to send notifications.
- Queues are auto-created by the code (`invalid-orders`, `order-notifications`).

## API Summary
- `POST /api/registerMeal` – Add a meal for a restaurant.
- `GET /api/meals?area=<area>` – List meals available in an area.
- `POST /api/submitOrder` – Place an order; stores it in Table Storage and schedules a notification.

## Local Development
1. **Prerequisites**: Python 3.10+ and Azure Functions Core Tools if you want to run the host locally.
2. **Install deps**: `cd backend && pip install -r requirements.txt`.
3. **Configure**: Copy `backend/local.settings.json.example` to `backend/local.settings.json` and fill in your values (Storage + Notification Hub).
4. **Run**: From `backend`, `func start` to run all Functions locally.
5. **Test**:
   - Register a meal: `curl -X POST http://localhost:7071/api/registerMeal ...`
   - List meals: `curl "http://localhost:7071/api/meals?area=Central"`
   - Submit an order: `curl -X POST http://localhost:7071/api/submitOrder ...`
   - Inspect queues (`invalid-orders`, `order-notifications`) via Azure Storage Explorer or the Azure Portal.

## Cloud Deployment Notes
- Deploy the Function App with your Storage connection string in `AzureWebJobsStorage`.
- Ensure the Storage account has Table and Queue services enabled.
- Provision Notification Hubs and set `AZURE_NOTIFICATION_HUB_CONNECTION_STRING` and `AZURE_NOTIFICATION_HUB_NAME`.
- Frontend can be hosted as static files (Storage static website, Static Web Apps, or any web host) and pointed at the Function App URL.

## Operational Considerations
- **Validation**: Invalid orders are never lost—they’re written to `invalid-orders` for inspection.
- **Retries**: Queue-triggered `notifyorder` will retry on failure; poison queue can capture problematic messages.
- **CORS**: Handled in each HTTP function for `OPTIONS` and responses.
- **Images**: If using `blobl.py`, ensure Blob containers exist and are publicly readable for images (or adjust SAS/ACLs).

