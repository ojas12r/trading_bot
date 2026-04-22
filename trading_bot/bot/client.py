"""
Low-level Binance Futures Testnet REST client.

Handles:
  - HMAC-SHA256 request signing
  - Timestamping / recvWindow
  - HTTP retries with exponential back-off
  - Logging of every outbound request and inbound response
  - Structured exception raising on API / network errors
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
import urllib.parse
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .logging_config import get_logger

logger = get_logger("client")

TESTNET_BASE_URL = "https://testnet.binancefuture.com"
DEFAULT_RECV_WINDOW = 5000  # milliseconds


class BinanceAPIError(Exception):
    """Raised when the Binance API returns a non-200 status or error payload."""

    def __init__(self, code: int, message: str, http_status: int | None = None):
        self.code = code
        self.message = message
        self.http_status = http_status
        super().__init__(f"Binance API error {code}: {message}")


class BinanceNetworkError(Exception):
    """Raised on network-level failures (timeout, connection refused, etc.)."""


def _build_session(retries: int = 3) -> requests.Session:
    """Return a session with retry logic for transient failures."""
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST", "DELETE"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class BinanceFuturesClient:
    """
    Thin wrapper around the Binance USDT-M Futures REST API (Testnet).

    Usage:
        client = BinanceFuturesClient(api_key="...", api_secret="...")
        response = client.place_order(symbol="BTCUSDT", side="BUY",
                                       order_type="MARKET", quantity="0.001")
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str = TESTNET_BASE_URL,
        recv_window: int = DEFAULT_RECV_WINDOW,
    ):
        self.api_key = api_key or os.environ.get("BINANCE_API_KEY", "")
        self.api_secret = api_secret or os.environ.get("BINANCE_API_SECRET", "")
        self.base_url = base_url.rstrip("/")
        self.recv_window = recv_window
        self._session = _build_session()

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "API key and secret are required. "
                "Set BINANCE_API_KEY / BINANCE_API_SECRET env vars "
                "or pass them directly."
            )

        logger.info("BinanceFuturesClient initialised (base_url=%s)", self.base_url)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _sign(self, params: dict) -> str:
        """Create HMAC-SHA256 signature over URL-encoded params string."""
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _headers(self) -> dict:
        return {
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        signed: bool = True,
    ) -> Any:
        """
        Execute an HTTP request, handle signing, logging, and error parsing.
        Returns the JSON-decoded response body.
        """
        params = params or {}
        url = f"{self.base_url}{endpoint}"

        if signed:
            params["timestamp"] = self._timestamp()
            params["recvWindow"] = self.recv_window
            params["signature"] = self._sign(params)

        # Redact secret from logs
        safe_params = {k: v for k, v in params.items() if k != "signature"}
        logger.debug(
            "→ %s %s  params=%s", method.upper(), endpoint, safe_params
        )

        try:
            if method.upper() == "GET":
                response = self._session.get(url, params=params, headers=self._headers(), timeout=10)
            elif method.upper() == "POST":
                response = self._session.post(url, data=params, headers=self._headers(), timeout=10)
            elif method.upper() == "DELETE":
                response = self._session.delete(url, params=params, headers=self._headers(), timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        except requests.exceptions.ConnectionError as exc:
            logger.error("Network connection error: %s", exc)
            raise BinanceNetworkError(f"Connection failed: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out: %s", exc)
            raise BinanceNetworkError(f"Request timed out: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            logger.error("Unexpected request error: %s", exc)
            raise BinanceNetworkError(f"Request failed: {exc}") from exc

        logger.debug(
            "← HTTP %s  body=%s", response.status_code, response.text[:500]
        )

        # Parse response
        try:
            data = response.json()
        except ValueError:
            logger.error("Non-JSON response (HTTP %s): %s", response.status_code, response.text)
            raise BinanceAPIError(
                code=-1,
                message=f"Non-JSON response: {response.text[:200]}",
                http_status=response.status_code,
            )

        if response.status_code != 200 or (isinstance(data, dict) and "code" in data and data["code"] < 0):
            code = data.get("code", response.status_code) if isinstance(data, dict) else response.status_code
            msg = data.get("msg", str(data)) if isinstance(data, dict) else str(data)
            logger.error("API error – code=%s  msg=%s", code, msg)
            raise BinanceAPIError(code=code, message=msg, http_status=response.status_code)

        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_server_time(self) -> dict:
        """Fetch Binance server time (useful for clock-sync check)."""
        return self._request("GET", "/fapi/v1/time", signed=False)

    def get_exchange_info(self) -> dict:
        """Return exchange info including symbol filters."""
        return self._request("GET", "/fapi/v1/exchangeInfo", signed=False)

    def get_account(self) -> dict:
        """Return account details including balances."""
        return self._request("GET", "/fapi/v2/account")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str | None = None,
        stop_price: str | None = None,
        time_in_force: str = "GTC",
        reduce_only: bool = False,
    ) -> dict:
        """
        Place a futures order.

        Args:
            symbol:        e.g. "BTCUSDT"
            side:          "BUY" or "SELL"
            order_type:    "MARKET", "LIMIT", or "STOP_MARKET"
            quantity:      Order quantity as string
            price:         Required for LIMIT orders
            stop_price:    Required for STOP_MARKET orders
            time_in_force: GTC / IOC / FOK (LIMIT only)
            reduce_only:   Whether to reduce position only
        """
        params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if not price:
                raise ValueError("price is required for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = time_in_force

        if order_type == "STOP_MARKET":
            if not stop_price:
                raise ValueError("stopPrice is required for STOP_MARKET orders.")
            params["stopPrice"] = stop_price

        if reduce_only:
            params["reduceOnly"] = "true"

        logger.info(
            "Placing %s %s order | symbol=%s qty=%s price=%s stopPrice=%s",
            side, order_type, symbol, quantity, price or "N/A", stop_price or "N/A",
        )

        result = self._request("POST", "/fapi/v1/order", params=params)
        logger.info(
            "Order placed ✓ | orderId=%s status=%s executedQty=%s avgPrice=%s",
            result.get("orderId"),
            result.get("status"),
            result.get("executedQty"),
            result.get("avgPrice"),
        )
        return result

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel an open order by orderId."""
        params = {"symbol": symbol, "orderId": order_id}
        logger.info("Cancelling order | symbol=%s orderId=%s", symbol, order_id)
        result = self._request("DELETE", "/fapi/v1/order", params=params)
        logger.info("Order cancelled | orderId=%s status=%s", result.get("orderId"), result.get("status"))
        return result

    def get_order(self, symbol: str, order_id: int) -> dict:
        """Fetch status of a specific order."""
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("GET", "/fapi/v1/order", params=params)

    def get_open_orders(self, symbol: str | None = None) -> list:
        """Return all open orders, optionally filtered by symbol."""
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._request("GET", "/fapi/v1/openOrders", params=params)

    def get_position_risk(self, symbol: str | None = None) -> list:
        """Return current position information."""
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._request("GET", "/fapi/v2/positionRisk", params=params)
