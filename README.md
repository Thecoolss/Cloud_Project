# Cloud_Project

## Backend notes
- Storage queues used: `invalid-orders` (captures invalid order payloads) and `order-notifications` (drives delayed notifications). Queues are auto-created when requests arrive.
- Configure storage via `AzureWebJobsStorage` or `AzureStorageConnectionString`. See `backend/local.settings.json.example` for a full list of required app settings.
- To enable user notifications 15 seconds after an order is placed, supply `AZURE_NOTIFICATION_HUB_CONNECTION_STRING` and `AZURE_NOTIFICATION_HUB_NAME` for your Notification Hub.
