import base64
import hashlib
import hmac
import json
import logging
import os
import time
from urllib.parse import quote_plus

import azure.functions as func
import requests


def _parse_notification_hub_connection(conn_str: str):
    """
    Parse the Notification Hubs connection string.
    """
    parts = dict(item.split('=', 1) for item in conn_str.split(';') if item)
    endpoint = parts.get('Endpoint')
    key_name = parts.get('SharedAccessKeyName')
    key_value = parts.get('SharedAccessKey')

    if not endpoint or not key_name or not key_value:
        raise ValueError("Notification Hub connection string is missing required parts.")

    endpoint = endpoint.replace('sb://', 'https://')
    if not endpoint.endswith('/'):
        endpoint += '/'

    return endpoint, key_name, key_value


def _build_sas_token(endpoint: str, hub_name: str, key_name: str, key_value: str, ttl_seconds: int = 3600):
    """
    Create a SAS token for Notification Hubs REST API.
    """
    target_uri = f"{endpoint}{hub_name}/messages"
    encoded_uri = quote_plus(target_uri)
    expiry = int(time.time()) + ttl_seconds
    signature = quote_plus(base64.b64encode(
        hmac.new(key_value.encode('utf-8'), f"{encoded_uri}\n{expiry}".encode('utf-8'), hashlib.sha256).digest()
    ))
    token = f"SharedAccessSignature sr={encoded_uri}&sig={signature}&se={expiry}&skn={key_name}"
    return target_uri, token


def _send_notification(order_payload: dict) -> None:
    """
    Send a broadcast notification via Azure Notification Hubs announcing preparation.
    """
    connection = os.getenv("AZURE_NOTIFICATION_HUB_CONNECTION_STRING")
    hub_name = os.getenv("AZURE_NOTIFICATION_HUB_NAME")

    if not connection or not hub_name:
        logging.warning("Notification Hub settings missing; skipping notification send.")
        return

    endpoint, key_name, key_value = _parse_notification_hub_connection(connection)
    target_uri, sas_token = _build_sas_token(endpoint, hub_name, key_name, key_value)
    url = f"{target_uri}/?api-version=2015-01"

    payload = json.dumps({
        "data": {
            "message": order_payload.get("message") or f"Your order {order_payload.get('orderNumber')} is being prepared.",
            "orderId": order_payload.get("orderId"),
            "orderNumber": order_payload.get("orderNumber"),
            "status": order_payload.get("status", "Preparing"),
            "area": order_payload.get("area"),
            "customerName": order_payload.get("customerName")
        }
    })

    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "Authorization": sas_token,
        "ServiceBusNotification-Format": "template"
    }

    response = requests.post(url, headers=headers, data=payload, timeout=10)
    response.raise_for_status()
    logging.info("Notification sent for order %s", order_payload.get("orderNumber"))


def main(msg: func.QueueMessage) -> None:
    """
    Queue-triggered Azure Function that sends a notification 15 seconds after order placement.
    """
    try:
        order_payload = json.loads(msg.get_body().decode('utf-8'))
    except Exception as parse_error:
        logging.error("Failed to parse queue message: %s", parse_error)
        return

    try:
        _send_notification(order_payload)
    except Exception as notify_error:
        logging.error("Failed to send notification: %s", notify_error)
        # Raising ensures the message is retried or moved to the poison queue.
        raise notify_error
