Binance Futures Testnet Trading Bot

A modular, production-style command-line trading bot for Binance USDT-M Futures Testnet.
This project demonstrates clean architecture, robust error handling, structured logging, and validated order execution using raw REST APIs.

Overview

This trading bot provides a command-line interface (CLI) to interact with the Binance Futures Testnet. It supports multiple order types, validates inputs before execution, and logs all activity for traceability and debugging.

The project is designed with a layered architecture similar to real-world backend systems.

Features
Place orders using:
Market orders
Limit orders
Stop-Market orders
Input validation before API calls
Structured logging (console + rotating log files)
Retry logic for network failures
Clear CLI interface for interaction
Modular and extensible codebase
Project Structure
trading_bot/
├── bot/
│   ├── client.py          # Binance API client (signing, retries, error handling)
│   ├── orders.py          # Order orchestration and formatting
│   ├── validators.py      # Input validation logic
│   └── logging_config.py  # Logging setup (console + file)
├── cli.py                 # Command-line interface
├── logs/                  # Log files (auto-created)
├── README.md
└── requirements.txt
Architecture
CLI → Validation Layer → Orders Layer → API Client → Binance API
CLI handles user input
Validators ensure correctness before execution
Orders layer manages business logic
Client layer handles API communication
Setup
1. Prerequisites
Python 3.8+
Binance Futures Testnet account
https://testnet.binancefuture.com
API Key and Secret from Testnet
2. Install dependencies
pip install -r requirements.txt
3. Configure API credentials

Option 1: Environment variables

export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"

Option 2: Pass via CLI

python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET order ...
Usage
Place a Market Order
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
Place a Limit Order
python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500
Place a Stop-Market Order
python cli.py order --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 65000
View Account Information
python cli.py account
View Open Orders
python cli.py open-orders
View Positions
python cli.py positions
Validation

All inputs are validated before sending requests to the exchange.

Examples:

Invalid quantity:

Quantity must be positive

Missing price for limit order:

Price is required for LIMIT orders

Invalid order side:

Must be BUY or SELL

This prevents unnecessary API calls and improves reliability.

Logging

The bot uses structured logging:

Console: INFO level
File: DEBUG level

Logs are stored in:

logs/trading_bot.log

Features:

Rotating logs (5 MB per file, 3 backups)
Full request/response tracking
Error tracing
Error Handling

Custom exceptions are implemented:

BinanceAPIError – API-level errors
BinanceNetworkError – network failures

The CLI handles:

Validation errors
API errors
Network issues
User interruptions

Each error produces a clear and meaningful message.

Assumptions
Uses Binance Futures Testnet only
Supports USDT-M perpetual contracts
Uses one-way position mode (positionSide=BOTH)
Quantity precision is not enforced locally (handled by exchange)
Dependencies
requests
urllib3

No third-party Binance SDK is used. All API calls are implemented using raw REST with HMAC-SHA256 signing.

Why This Project

This project demonstrates:

Clean software design using layered architecture
Real-world API integration with authentication and signing
Robust validation and error handling
Production-style logging and debugging practices
CLI-based system design similar to developer tools
Future Improvements
Add Stop-Limit order support
Implement trading strategies (automation layer)
Add WebSocket support for real-time data
Introduce backtesting module
Add unit tests
Dockerize the application
