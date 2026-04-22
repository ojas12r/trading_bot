"""
Order placement orchestration layer.

Sits between the CLI and the raw BinanceFuturesClient.
Handles:
  - Parameter preparation (Decimal → string with correct precision)
  - Pre-flight validation
  - Friendly result formatting
  - Structured logging of the full order lifecycle
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from .client import BinanceFuturesClient, BinanceAPIError, BinanceNetworkError
from .validators import validate_all
from .logging_config import get_logger

logger = get_logger("orders")


def _fmt(value: Decimal | None) -> str | None:
    """Convert Decimal to string, stripping trailing zeros."""
    if value is None:
        return None
    return format(value.normalize(), "f")


def _print_separator(char: str = "─", width: int = 60) -> None:
    print(char * width)


def _print_order_summary(params: dict) -> None:
    """Print a human-readable summary of what will be sent to the exchange."""
    _print_separator()
    print("  ORDER REQUEST SUMMARY")
    _print_separator()
    print(f"  Symbol     : {params['symbol']}")
    print(f"  Side       : {params['side']}")
    print(f"  Type       : {params['order_type']}")
    print(f"  Quantity   : {_fmt(params['quantity'])}")
    if params.get("price"):
        print(f"  Price      : {_fmt(params['price'])}")
    if params.get("stop_price"):
        print(f"  Stop Price : {_fmt(params['stop_price'])}")
    _print_separator()


def _print_order_response(response: dict) -> None:
    """Pretty-print the exchange response."""
    _print_separator()
    print("  ORDER RESPONSE")
    _print_separator()
    fields = [
        ("Order ID", "orderId"),
        ("Client Order ID", "clientOrderId"),
        ("Symbol", "symbol"),
        ("Side", "side"),
        ("Type", "type"),
        ("Status", "status"),
        ("Quantity", "origQty"),
        ("Executed Qty", "executedQty"),
        ("Avg Price", "avgPrice"),
        ("Price", "price"),
        ("Stop Price", "stopPrice"),
        ("Time in Force", "timeInForce"),
        ("Reduce Only", "reduceOnly"),
        ("Created At", "updateTime"),
    ]
    for label, key in fields:
        value = response.get(key)
        if value is not None and value != "" and value != "0" and value != 0:
            if key == "updateTime" and isinstance(value, int):
                import datetime
                value = datetime.datetime.fromtimestamp(value / 1000).strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"  {label:<18}: {value}")
    _print_separator()


def place_order(
    client: BinanceFuturesClient,
    *,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: str | float | None = None,
    stop_price: str | float | None = None,
    time_in_force: str = "GTC",
    reduce_only: bool = False,
) -> dict[str, Any]:
    """
    Validate inputs, place the order, and return the exchange response.

    Raises:
        ValueError       – invalid input parameters
        BinanceAPIError  – API-level error from the exchange
        BinanceNetworkError – network failure
    """
    # 1. Validate
    logger.debug(
        "Validating params: symbol=%s side=%s type=%s qty=%s price=%s stop=%s",
        symbol, side, order_type, quantity, price, stop_price,
    )
    params = validate_all(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )

    # 2. Print pre-flight summary
    _print_order_summary(params)

    # 3. Send to exchange
    try:
        response = client.place_order(
            symbol=params["symbol"],
            side=params["side"],
            order_type=params["order_type"],
            quantity=_fmt(params["quantity"]),
            price=_fmt(params.get("price")),
            stop_price=_fmt(params.get("stop_price")),
            time_in_force=time_in_force,
            reduce_only=reduce_only,
        )
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        raise
    except BinanceAPIError as exc:
        logger.error("API error placing order: %s", exc)
        raise
    except BinanceNetworkError as exc:
        logger.error("Network error placing order: %s", exc)
        raise

    # 4. Print response
    _print_order_response(response)

    status = response.get("status", "UNKNOWN")
    order_id = response.get("orderId", "N/A")

    if status in ("NEW", "PARTIALLY_FILLED", "FILLED"):
        print(f"\n  ✅  SUCCESS — Order #{order_id} accepted by exchange (status: {status})\n")
        logger.info("Order #%s placed successfully (status=%s)", order_id, status)
    else:
        print(f"\n  ⚠️   Order #{order_id} returned status: {status}\n")
        logger.warning("Order #%s returned unexpected status: %s", order_id, status)

    return response
