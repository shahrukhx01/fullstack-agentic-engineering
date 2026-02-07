import logging
from uuid import uuid4

from langchain.tools import tool

logger = logging.getLogger("react-agents")
logging.basicConfig(level=logging.INFO)


@tool
def get_order_id(customer_email: str) -> dict[str, str]:
    """Get the order ID for a customer's most recent order."""
    # In a real implementation, this would query a database or API.
    logger.info(f"Retrieving order ID for customer email: {customer_email}")
    return {"order_id": uuid4().hex}


@tool
def get_tracking_id(order_id: str) -> dict[str, str]:
    """Get the tracking ID for an order."""
    # In a real implementation, this would query a database or API.
    logger.info(f"Retrieving tracking ID for order ID: {order_id}")
    return {"tracking_id": uuid4().hex}


@tool
def get_shipping_details(tracking_id: str) -> dict[str, str]:
    """Get the shipping details for a tracking ID."""
    # In a real implementation, this would query a database or API.
    logger.info(f"Retrieving shipping details for tracking ID: {tracking_id}")
    return {
        "shipping_status": "In Transit",
        "estimated_delivery": "2024-06-30",
        "tracking_id": tracking_id,
        "shipping_provider": "DHL",
    }
