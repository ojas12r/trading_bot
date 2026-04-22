# Binance Futures Testnet Trading Bot

A modular command-line trading bot for Binance USDT-M Futures Testnet.  
This project demonstrates clean architecture, robust error handling, structured logging, and validated order execution using raw REST APIs.

---

## Overview

This trading bot provides a CLI to interact with Binance Futures Testnet. It supports multiple order types, validates all inputs before execution, and logs every operation for traceability.

The system is designed using a layered architecture similar to production backend services.

---

## Features

- Market, Limit, and Stop-Market order support
- Input validation before API calls
- Structured logging (console + rotating file logs)
- Retry logic for network failures
- Clean and extensible CLI interface
- Modular codebase with clear separation of concerns

---

## Project Structure


trading_bot/
├── bot/
│ ├── client.py # Binance API client (signing, retries, error handling)
│ ├── orders.py # Order orchestration and formatting
│ ├── validators.py # Input validation logic
│ └── logging_config.py # Logging setup
├── cli.py # CLI entry point
├── logs/ # Log files (auto-created)
├── README.md
└── requirements.txt


---

## Architecture


CLI → Validation Layer → Orders Layer → API Client → Binance API


- CLI handles user interaction  
- Validators ensure correctness of inputs  
- Orders layer manages business logic  
- Client handles API communication  

---

## Setup

### Prerequisites

- Python 3.8+
- Binance Futures Testnet account: https://testnet.binancefuture.com
- API Key and Secret from Testnet

---

### Install dependencies


pip install -r requirements.txt


---

### Configure API credentials

**Option 1: Environment variables (recommended)**


export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"


**Option 2: Pass via CLI**


python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET order ...


---

## Usage

### Market Order


python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001


---

### Limit Order


python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500


---

### Stop-Market Order


python cli.py order --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 65000


---

### Account Information


python cli.py account


---

### Open Orders


python cli.py open-orders


---

### Positions


python cli.py positions


---

## Validation

All inputs are validated before API calls.

Examples:

- Quantity must be positive  
- Price is required for LIMIT orders  
- Stop price is required for STOP_MARKET orders  
- Side must be BUY or SELL  

This prevents invalid requests and improves reliability.

---

## Logging

- Console logging: INFO level  
- File logging: DEBUG level  

Logs are stored in:


logs/trading_bot.log


Features:

- Rotating log files (5 MB, 3 backups)
- Full request/response tracking
- Error tracing

---

## Error Handling

Custom exceptions:

- BinanceAPIError – API-level failures  
- BinanceNetworkError – network issues  

The CLI gracefully handles:

- Validation errors  
- API errors  
- Network failures  
- User interruptions  

---

## Assumptions

- Uses Binance Futures Testnet only  
- Supports USDT-M perpetual contracts  
- Uses one-way position mode (positionSide=BOTH)  
- Quantity precision is validated by exchange  

---

## Dependencies

- requests  
- urllib3  

No third-party Binance SDK is used.

---

## Why This Project

This project demonstrates:

- Clean software design with layered architecture  
- Real-world API integration with authentication and signing  
- Robust validation and error handling  
- Production-style logging practices  
- CLI-based system design  

---

## Future Improvements

- Add Stop-Limit order support  
- Implement automated trading strategies  
- Add WebSocket support for real-time data  
- Introduce backtesting module  
- Add unit tests  
- Dockerize the application  

---

## License

This project is available under the MIT License.
