Binance Futures Testnet Trading Bot
A modular, command-line trading bot built for the Binance USDT-M Futures Testnet. This project demonstrates clean architecture, robust error handling, structured logging, and validated order execution using raw REST APIs without relying on third-party SDKs.

 Table of Contents
Overview

Features

Architecture

Project Structure

Getting Started

Usage Examples

System Design Highlights

Roadmap

License

Overview
This trading bot provides a comprehensive CLI to interact with the Binance Futures Testnet. It supports multiple order types, strictly validates all inputs before execution to prevent invalid requests, and logs every operation for complete traceability. The system is designed using a layered architecture, closely mimicking production-grade backend services.

Features
Multiple Order Types: Support for Market, Limit, and Stop-Market orders.

Pre-flight Validation: Strict input validation before any API calls are made.

Comprehensive Logging: Structured logging with both console output and rotating file logs.

Resilience: Built-in retry logic for network failures.

Clean CLI: Extensible and user-friendly command-line interface.

No Third-Party SDKs: Direct API integration with custom authentication and request signing.

Architecture

The bot relies on a clear separation of concerns, moving linearly from user input to the external exchange:

CLI -->Validation Layer--> Orders Layer-->API Client-->Binance API

CLI: Handles user interaction and argument parsing.

Validators: Ensures the correctness of inputs (e.g., positive quantities, required prices).

Orders Layer: Manages business logic and payload formatting.

API Client: Handles network communication, request signing, retries, and error parsing.

 Project Structure
trading_bot/
├── bot/
│   ├── client.py           # Binance API client (signing, retries, error handling)
│   ├── orders.py           # Order orchestration and formatting
│   ├── validators.py       # Input validation logic
│   └── logging_config.py   # Logging setup
├── cli.py                  # CLI entry point
├── logs/                   # Auto-created log files
├── requirements.txt
└── README.md

Getting Started
Prerequisites
Python: 3.8 or higher.

Binance Account: A valid Binance Futures Testnet account.

API Credentials: Your Testnet API Key and Secret.

1. Install Dependencies
Clone the repository and install the required packages:

pip install -r requirements.txt

(Note: Dependencies include requests and urllib3.)

2. Configure API Credentials
Option 1: Environment Variables (Recommended)

export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"

Option 2: Pass via CLI Arguments

python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET order ...

Usage Examples
Placing Orders
Market Order

python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

Limit Order

python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500

Stop-Market Order

python cli.py order --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 65000

Account & Positions
View Account Information

python cli.py account

View Open Orders

python cli.py open-orders

View Active Positions

python cli.py positions

System Design Highlights
Validation
All inputs are thoroughly validated before reaching the API client. This prevents invalid requests and improves reliability.

Quantity must be a positive number.

price is strictly required for LIMIT orders.

stop-price is strictly required for STOP_MARKET orders.

side is restricted to BUY or SELL.

Logging
Console: INFO level for clear user feedback.

File: DEBUG level for deep troubleshooting (logs/trading_bot.log).

Features: Rotating log files (max 5 MB, up to 3 backups), full request/response tracking, and detailed error tracing.

Error Handling
The CLI gracefully manages user interruptions, validation errors, API errors, and network failures using custom exceptions:

BinanceAPIError: Captures and formats API-level failures.

BinanceNetworkError: Captures underlying network/connection issues.

Assumptions & Constraints
Operates only on the Binance Futures Testnet.

Supports USDT-M perpetual contracts.

Assumes a one-way position mode (positionSide=BOTH).

Quantity precision is validated directly by the exchange API.

Future Improvements
[ ] Add STOP_LIMIT order support.

[ ] Implement automated trading strategies.

[ ] Add WebSocket support for real-time market data.

[ ] Introduce a historical backtesting module.

[ ] Expand unit and integration test coverage.

[ ] Dockerize the application for easier deployment.

License
This project is open-sourced software licensed under the MIT License.
