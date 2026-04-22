# Binance Futures Testnet Trading Bot

A clean, structured Python trading bot for Binance USDT-M Futures Testnet. Supports Market, Limit, and Stop-Market orders via a well-organised CLI with robust validation, structured logging, and full error handling.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper (signing, retries, error handling)
│   ├── orders.py          # Order placement orchestration + pretty output
│   ├── validators.py      # Input validation (all raises ValueError with clear messages)
│   └── logging_config.py  # Rotating file + console logging setup
├── cli.py                 # CLI entry point (argparse, 4 commands)
├── logs/
│   └── trading_bot.log    # Auto-created on first run
├── README.md
└── requirements.txt
```

---

## Setup

### 1. Prerequisites

- Python 3.8+
- A [Binance Futures Testnet](https://testnet.binancefuture.com) account
- Testnet API credentials (generate at https://testnet.binancefuture.com → API Management)

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set API credentials

**Option A — Environment variables (recommended):**
```bash
export BINANCE_API_KEY="your_testnet_api_key"
export BINANCE_API_SECRET="your_testnet_api_secret"
```

**Option B — Pass on the command line:**
```bash
python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET order ...
```

---

## How to Run

### Place a Market BUY order
```bash
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Console output:**
```
────────────────────────────────────────────────────────────
  ORDER REQUEST SUMMARY
────────────────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
────────────────────────────────────────────────────────────
  ORDER RESPONSE
────────────────────────────────────────────────────────────
  Order ID           : 4710427847
  Client Order ID    : web_IlyAbdRUfkDwHUWQVV7g
  Symbol             : BTCUSDT
  Side               : BUY
  Type               : MARKET
  Status             : FILLED
  Quantity           : 0.001
  Executed Qty       : 0.001
  Avg Price          : 93427.10
  Created At         : 2026-04-22 15:09:28 UTC
────────────────────────────────────────────────────────────

    SUCCESS — Order #4710427847 accepted by exchange (status: FILLED)
```

---

### Place a Limit SELL order
```bash
python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500
```

### Place a Market SELL order
```bash
python cli.py order --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### Place a Limit BUY order with custom Time-in-Force
```bash
python cli.py order --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.002 --price 60000 --tif IOC
```

### Place a Stop-Market order (Bonus feature)
```bash
python cli.py order --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 65000
```

### View account balances
```bash
python cli.py account
```

### List open orders
```bash
python cli.py open-orders
python cli.py open-orders --symbol BTCUSDT
```

### View positions
```bash
python cli.py positions
python cli.py positions --symbol BTCUSDT
```

---

## Validation Examples

The bot validates all inputs before hitting the API:

```bash
# Missing price for LIMIT order → error before API call
python cli.py order --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001
#   Validation error: Price is required for LIMIT orders.

# Zero quantity
python cli.py order --symbol BTCUSDT --side SELL --type MARKET --quantity 0
#   Validation error: Quantity must be positive, got 0.

# Invalid side
python cli.py order --symbol BTCUSDT --side LONG --type MARKET --quantity 0.001
#   Validation error: Invalid side 'LONG'. Must be one of: BUY, SELL.
```

---

## Logging

Logs are written to `logs/trading_bot.log` (rotating, max 5 MB × 3 backups).

- **File**: DEBUG level — every request params, full response body, errors
- **Console**: INFO level — key milestones and errors only

Log format:
```
2026-04-22 15:09:29 | INFO     | trading_bot.client | Order placed ✓ | orderId=4710427847 status=FILLED executedQty=0.001 avgPrice=93427.10
```

---

## Assumptions

1. **Testnet only** — the base URL is hardcoded to `https://testnet.binancefuture.com`. To switch to mainnet, pass `--base-url https://fapi.binance.com` (requires extending the client init).
2. **USDT-M perpetuals** — uses `/fapi/v1/` endpoints (USDT-Margined). Coin-M (`/dapi/`) is not supported.
3. **Hedge mode not assumed** — orders are placed with `positionSide=BOTH` (default one-way mode). Enable hedge mode in your testnet account settings if needed.
4. **Quantity precision** — the bot sends whatever quantity you specify. If the exchange rejects it (e.g., wrong step size), the API error is displayed clearly.
5. **Python 3.8+** required for `from __future__ import annotations`.

---

## Dependencies

| Package    | Purpose                              |
|------------|--------------------------------------|
| `requests` | HTTP client for REST API calls       |
| `urllib3`  | Retry logic via `HTTPAdapter`        |

No third-party Binance SDK is used — all API calls are raw REST with HMAC-SHA256 signing.
