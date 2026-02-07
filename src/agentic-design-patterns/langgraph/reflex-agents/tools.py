from uuid import uuid4

from langchain.tools import tool


def _ticket_response(topic: str) -> str:
    ticket_id = str(uuid4())
    message = (
        f"Your ticket has been created for {topic}. "
        f"Ticket #: {ticket_id}. A support agent will be in touch with you soon."
    )
    print(message)
    return message


@tool
def orders(query: str) -> str:
    """Create a support ticket for order-related requests."""

    return _ticket_response("orders")


@tool
def returns(query: str) -> str:
    """Create a support ticket for return-related requests."""

    return _ticket_response("returns")


@tool
def product_inquiry(query: str) -> str:
    """Create a support ticket for product inquiry requests."""

    return _ticket_response("product inquiries")


@tool
def shipping(query: str) -> str:
    """Create a support ticket for shipping-related requests."""

    return _ticket_response("shipping")
