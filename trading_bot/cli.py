#!/usr/bin/env python3
"""
cli.py – Command-line interface for the Binance Futures Testnet trading bot.

Usage examples:
  # Market BUY
  python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Limit SELL
  python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500

  # Stop-Market BUY
  python cli.py order --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 65000

  # Account info
  python cli.py account

  # Open orders
  python cli.py open-orders --symbol BTCUSDT
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from bot.client import BinanceFuturesClient, BinanceAPIError, BinanceNetworkError
from bot.logging_config import setup_logging, get_logger
from bot.orders import place_order

# Initialise logging before anything else
setup_logging()
logger = get_logger("cli")


# ──────────────────────────────────────────────────────────────────────────────
# Argument parser
# ──────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet Trading Bot (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--api-key",
        default=os.environ.get("BINANCE_API_KEY"),
        help="Binance API key (or set BINANCE_API_KEY env var)",
    )
    parser.add_argument(
        "--api-secret",
        default=os.environ.get("BINANCE_API_SECRET"),
        help="Binance API secret (or set BINANCE_API_SECRET env var)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    # ── order ──────────────────────────────────────────────────────────────
    order_p = subparsers.add_parser("order", help="Place a new futures order")
    order_p.add_argument("--symbol",     required=True, help="Trading pair, e.g. BTCUSDT")
    order_p.add_argument("--side",       required=True, choices=["BUY", "SELL"], help="Order side")
    order_p.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type",
    )
    order_p.add_argument("--quantity",   required=True, help="Quantity to trade")
    order_p.add_argument("--price",      default=None,  help="Limit price (required for LIMIT orders)")
    order_p.add_argument("--stop-price", default=None,  dest="stop_price",
                         help="Stop trigger price (required for STOP_MARKET)")
    order_p.add_argument(
        "--tif", default="GTC", choices=["GTC", "IOC", "FOK"],
        help="Time-in-force (LIMIT orders, default: GTC)",
    )
    order_p.add_argument("--reduce-only", action="store_true", help="Reduce position only")

    # ── account ────────────────────────────────────────────────────────────
    subparsers.add_parser("account", help="Show account balances and info")

    # ── open-orders ────────────────────────────────────────────────────────
    oo_p = subparsers.add_parser("open-orders", help="List open orders")
    oo_p.add_argument("--symbol", default=None, help="Filter by symbol (optional)")

    # ── positions ──────────────────────────────────────────────────────────
    pos_p = subparsers.add_parser("positions", help="Show current positions")
    pos_p.add_argument("--symbol", default=None, help="Filter by symbol (optional)")

    return parser


# ──────────────────────────────────────────────────────────────────────────────
# Command handlers
# ──────────────────────────────────────────────────────────────────────────────

def cmd_order(args: argparse.Namespace, client: BinanceFuturesClient) -> None:
    logger.info(
        "CLI: place order | symbol=%s side=%s type=%s qty=%s price=%s stop=%s",
        args.symbol, args.side, args.order_type, args.quantity,
        args.price, args.stop_price,
    )
    place_order(
        client,
        symbol=args.symbol,
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        price=args.price,
        stop_price=args.stop_price,
        time_in_force=args.tif,
        reduce_only=args.reduce_only,
    )


def cmd_account(args: argparse.Namespace, client: BinanceFuturesClient) -> None:
    logger.info("CLI: fetching account info")
    data = client.get_account()
    # Show only meaningful balances
    balances = [
        a for a in data.get("assets", [])
        if float(a.get("walletBalance", 0)) > 0
    ]
    print("\n  ACCOUNT BALANCES")
    print("─" * 60)
    for b in balances:
        print(
            f"  {b['asset']:<8}  Wallet={b['walletBalance']}  "
            f"Available={b['availableBalance']}  "
            f"UnrealizedPnL={b['unrealizedProfit']}"
        )
    if not balances:
        print("  (No non-zero balances found)")
    print("─" * 60)
    print(f"\n  Total Margin Balance : {data.get('totalMarginBalance')}")
    print(f"  Total Wallet Balance : {data.get('totalWalletBalance')}")
    print(f"  Available Balance    : {data.get('availableBalance')}\n")


def cmd_open_orders(args: argparse.Namespace, client: BinanceFuturesClient) -> None:
    symbol = getattr(args, "symbol", None)
    logger.info("CLI: fetching open orders (symbol=%s)", symbol or "all")
    orders = client.get_open_orders(symbol=symbol)
    if not orders:
        print("\n  No open orders found.\n")
        return
    print(f"\n  OPEN ORDERS ({len(orders)} found)")
    print("─" * 60)
    for o in orders:
        print(
            f"  [{o['orderId']}] {o['symbol']} {o['side']} {o['type']} "
            f"qty={o['origQty']} price={o['price']} status={o['status']}"
        )
    print("─" * 60 + "\n")


def cmd_positions(args: argparse.Namespace, client: BinanceFuturesClient) -> None:
    symbol = getattr(args, "symbol", None)
    logger.info("CLI: fetching positions (symbol=%s)", symbol or "all")
    positions = client.get_position_risk(symbol=symbol)
    active = [p for p in positions if float(p.get("positionAmt", 0)) != 0]
    if not active:
        print("\n  No active positions.\n")
        return
    print(f"\n  ACTIVE POSITIONS ({len(active)} found)")
    print("─" * 60)
    for p in active:
        print(
            f"  {p['symbol']:<12} amt={p['positionAmt']}  "
            f"entryPrice={p['entryPrice']}  "
            f"unrealizedProfit={p['unRealizedProfit']}  "
            f"leverage={p['leverage']}x"
        )
    print("─" * 60 + "\n")


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Validate credentials before doing anything
    api_key = args.api_key or os.environ.get("BINANCE_API_KEY")
    api_secret = args.api_secret or os.environ.get("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        print(
            "\n  ❌  Error: API credentials not found.\n"
            "  Set BINANCE_API_KEY and BINANCE_API_SECRET environment variables,\n"
            "  or pass --api-key / --api-secret on the command line.\n"
        )
        logger.error("Missing API credentials. Aborting.")
        sys.exit(1)

    try:
        client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)
    except ValueError as exc:
        print(f"\n  ❌  Configuration error: {exc}\n")
        logger.error("Client init failed: %s", exc)
        sys.exit(1)

    try:
        if args.command == "order":
            cmd_order(args, client)
        elif args.command == "account":
            cmd_account(args, client)
        elif args.command == "open-orders":
            cmd_open_orders(args, client)
        elif args.command == "positions":
            cmd_positions(args, client)

    except ValueError as exc:
        print(f"\n  ❌  Validation error: {exc}\n")
        logger.error("Validation error: %s", exc)
        sys.exit(2)

    except BinanceAPIError as exc:
        print(f"\n  ❌  Exchange API error (code {exc.code}): {exc.message}\n")
        logger.error("API error: code=%s msg=%s", exc.code, exc.message)
        sys.exit(3)

    except BinanceNetworkError as exc:
        print(f"\n  ❌  Network error: {exc}\n")
        logger.error("Network error: %s", exc)
        sys.exit(4)

    except KeyboardInterrupt:
        print("\n  Interrupted by user.\n")
        logger.info("Interrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
