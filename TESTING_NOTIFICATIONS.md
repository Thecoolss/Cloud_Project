# Testing Azure Notifications

## Overview

Your notification system sends push notifications via Azure Notification Hub 15 seconds after an order is placed.

## How It Works

1. Customer submits order
2. Order saved to Azure Table Storage
3. Message sent to `order-notifications` queue (15 second delay)
4. `notifyorder` function picks up message from queue
5. Push notification sent via Azure Notification Hub

## Testing Methods

### Method 1: Check Azure Queue (Easiest Way)

1. Submit a test order through your website
2. Go to Azure Portal → Storage Account "1sttry" → Queues
3. Look for `order-notifications` queue
4. You should see messages (visible after 15 seconds)

### Method 2: Check Azure Function Logs

Azure Portal → Function App → Functions → notifyorder → Monitor
Look for execution logs showing "Notification sent for order..."

### Method 3: Manual Test Message

Add this JSON to the `order-notifications` queue manually:

```json
{
  "orderId": "test-123",
  "orderNumber": "ORD-TEST",
  "customerName": "Test User",
  "area": "Central",
  "status": "Preparing",
  "message": "Test notification"
}
```

## What to Configure

### In Azure Function App Settings:

```
AZURE_NOTIFICATION_HUB_CONNECTION_STRING=[your-connection-string]
AZURE_NOTIFICATION_HUB_NAME=[your-hub-name]
```

## Expected Behavior

### Success:
- Messages appear in `order-notifications` queue
- notifyorder function executes successfully
- Logs show "Notification sent for order..."
- No errors in Application Insights

### If Not Working:
- Check if environment variables are set
- Verify Notification Hub exists
- Check function logs for errors
- Ensure Azure Function is deployed with latest code

## Quick Check Command

```bash
# Deploy the updated function
cd backend
func azure functionapp publish [your-function-app-name]

# Watch logs
func azure functionapp logstream [your-function-app-name]
```

## Notes

- Notifications appear 15 seconds after order placement
- If Notification Hub isn't configured, orders still work (notifications just skip)
- Check Application Insights for detailed execution traces

