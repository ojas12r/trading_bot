"""
Input validation for CLI arguments before any API call is made.
All validators raise ValueError with a human-readable message on failure.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def validate_symbol(symbol: str) -> str:
    """Return upper-cased symbol or raise ValueError."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if not symbol.isalnum():
        raise ValueError(
            f"Symbol '{symbol}' contains invalid characters. "
            "Use alphanumeric only (e.g. BTCUSDT)."
        )
    return symbol


def validate_side(side: str) -> str:
    """Return normalised side (BUY/SELL) or raise ValueError."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    """Return normalised order type or raise ValueError."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: str | float) -> Decimal:
    """Return validated Decimal quantity or raise ValueError."""
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation:
        raise ValueError(f"Quantity '{quantity}' is not a valid number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be positive, got {qty}.")
    return qty


def validate_price(price: str | float | None, order_type: str) -> Decimal | None:
    """
    Validate price based on order type.
    - LIMIT / STOP_MARKET orders: price is required and must be > 0.
    - MARKET orders: price must be None / omitted.
    """
    if order_type == "MARKET":
        if price is not None and str(price).strip() not in ("", "0", "None"):
            raise ValueError("Price must not be supplied for MARKET orders.")
        return None

    if price is None or str(price).strip() in ("", "None"):
        raise ValueError(f"Price is required for {order_type} orders.")

    try:
        p = Decimal(str(price))
    except InvalidOperation:
        raise ValueError(f"Price '{price}' is not a valid number.")
    if p <= 0:
        raise ValueError(f"Price must be positive, got {p}.")
    return p


def validate_stop_price(stop_price: str | float | None, order_type: str) -> Decimal | None:
    """Validate stop price for STOP_MARKET orders."""
    if order_type != "STOP_MARKET":
        return None
    if stop_price is None or str(stop_price).strip() in ("", "None"):
        raise ValueError("stopPrice is required for STOP_MARKET orders.")
    try:
        sp = Decimal(str(stop_price))
    except InvalidOperation:
        raise ValueError(f"Stop price '{stop_price}' is not a valid number.")
    if sp <= 0:
        raise ValueError(f"Stop price must be positive, got {sp}.")
    return sp


def validate_all(
    *,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: str | float | None = None,
    stop_price: str | float | None = None,
) -> dict:
    """
    Run all validators and return a clean, normalised dict of parameters.
    Raises ValueError on the first validation failure.
    """
    sym = validate_symbol(symbol)
    sd = validate_side(side)
    ot = validate_order_type(order_type)
    qty = validate_quantity(quantity)
    prc = validate_price(price, ot)
    sp = validate_stop_price(stop_price, ot)

    return {
        "symbol": sym,
        "side": sd,
        "order_type": ot,
        "quantity": qty,
        "price": prc,
        "stop_price": sp,
    }
