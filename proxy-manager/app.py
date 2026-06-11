from __future__ import annotations
import json
import logging
import os
import random
import socket
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests
from requests import Response

PROXY_FILE = os.environ.get("PROXY_FILE", "proxies.txt")
PORT = int(os.environ.get("PROXY_MANAGER_PORT", "8080"))
HEALTH_CHECK_INTERVAL = int(os.environ.get("HEALTH_CHECK_INTERVAL", "30"))

DEFAULT_SCORE = 70
MIN_HEALTHY_SCORE = 40
FAILED_COOLDOWN_SECONDS = 30
TCP_CHECK_TIMEOUT_SECONDS = 5.0
FORWARD_TIMEOUT_SECONDS = 15.0

logger = logging.getLogger(__name__)


@dataclass
class ProxyState:
    value: str
    score: int = DEFAULT_SCORE
    cooldown_until: float = 0.0
    last_error: str | None = None
    last_latency_ms: int | None = None


class ProxyManager:
    def __init__(self, proxy_file: str = PROXY_FILE) -> None:
        self.proxy_file = proxy_file
        self.proxies: dict[str, ProxyState] = {}
        self.lock = threading.RLock()

        self._load_from_file()
        self._health_thread = threading.Thread(
            target=self._health_loop,
            name="proxy-health-check",
            daemon=True,
        )
        self._health_thread.start()

    def _normalize_proxy(self, raw: str) -> str | None:
        candidate = raw.strip()
        if not candidate:
            return None

        if "://" not in candidate:
            candidate = f"http://{candidate}"

        parsed = urlparse(candidate)
        if not parsed.scheme or not parsed.hostname:
            return None

        if parsed.scheme not in {"http", "https", "socks4", "socks5", "socks5h"}:
            return None

        return candidate

    def _load_from_file(self) -> None:
        try:
            with open(self.proxy_file, "r", encoding="utf-8") as f:
                for line in f:
                    proxy = self._normalize_proxy(line)
                    if proxy is None:
                        continue

                    with self.lock:
                        if proxy not in self.proxies:
                            self.proxies[proxy] = ProxyState(value=proxy)
        except FileNotFoundError:
            logger.warning("Proxy file not found: %s", self.proxy_file)

    def _health_loop(self) -> None:
        while True:
            try:
                self._run_health_checks()
            except Exception:
                logger.exception("Health-check loop failed")
            time.sleep(HEALTH_CHECK_INTERVAL)

    def _run_health_checks(self) -> None:
        with self.lock:
            items = list(self.proxies.items())

        for proxy, state in items:
            try:
                started = time.perf_counter()
                self._tcp_check(proxy)
                latency_ms = int((time.perf_counter() - started) * 1000)

                with self.lock:
                    state.last_latency_ms = latency_ms
                    state.score = min(100, state.score + 1)
                    state.last_error = None
            except Exception as exc:
                with self.lock:
                    state.score = max(0, state.score - 10)
                    state.cooldown_until = time.time() + FAILED_COOLDOWN_SECONDS
                    state.last_error = str(exc)

    def _tcp_check(self, proxy: str) -> None:
        parsed = urlparse(proxy)
        host = parsed.hostname
        port = parsed.port

        if host is None:
            raise ValueError(f"Invalid proxy URL: {proxy}")

        if port is None:
            port = 443 if parsed.scheme == "https" else 80

        with socket.create_connection((host, port), timeout=TCP_CHECK_TIMEOUT_SECONDS):
            return

    def _is_available(self, state: ProxyState, now: float) -> bool:
        return state.score >= MIN_HEALTHY_SCORE and now >= state.cooldown_until

    def get_next_proxy(self) -> str | None:
        with self.lock:
            now = time.time()
            healthy: list[tuple[str, ProxyState]] = [
                (proxy, state)
                for proxy, state in self.proxies.items()
                if self._is_available(state, now)
            ]

            if not healthy:
                return None

            weights = [max(1, state.score) for _, state in healthy]
            chosen = random.choices(healthy, weights=weights, k=1)[0]
            return chosen[0]

    def report(self, proxy: str, ok: bool) -> None:
        with self.lock:
            state = self.proxies.get(proxy)
            if state is None:
                return

            if ok:
                state.score = min(100, state.score + 5)
                state.last_error = None
                return

            state.score = max(0, state.score - 20)
            state.cooldown_until = time.time() + FAILED_COOLDOWN_SECONDS
            state.last_error = "reported failure"

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            proxies: list[dict[str, Any]] = [
                {
                    "proxy": proxy,
                    "score": state.score,
                    "cooldown_until": state.cooldown_until,
                    "last_latency_ms": state.last_latency_ms,
                    "last_error": state.last_error,
                }
                for proxy, state in sorted(self.proxies.items())
            ]
            healthy_count = sum(
                1
                for state in self.proxies.values()
                if state.score >= MIN_HEALTHY_SCORE and time.time() >= state.cooldown_until
            )

        return {
            "proxies": proxies,
            "healthy_count": healthy_count,
        }

    def forward(self, target_url: str) -> Response:
        proxy = self.get_next_proxy()
        if proxy is None:
            raise RuntimeError("No healthy proxy available")

        parsed_target = urlparse(target_url)
        if parsed_target.scheme not in {"http", "https"}:
            raise ValueError("Only http and https URLs are allowed")

        response = requests.get(
            target_url,
            proxies={"http": proxy, "https": proxy},
            timeout=(5, FORWARD_TIMEOUT_SECONDS),
            allow_redirects=True,
        )
        print(f"proxied {target_url} with {proxy}")
        return response


manager = ProxyManager()


class Handler(BaseHTTPRequestHandler):
    server_version = "ProxyManager/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._send_json(200, manager.snapshot())
            return

        if parsed.path == "/next":
            proxy = manager.get_next_proxy()
            if proxy is None:
                self._send_json(503, {"proxy": None, "error": "No healthy proxy available"})
                return
            self._send_json(200, {"proxy": proxy})
            return

        if parsed.path == "/proxy":
            params = parse_qs(parsed.query)
            target_url = params.get("url", [None])[0]

            if not target_url:
                self._send_json(400, {"error": "Missing url parameter"})
                return

            try:
                response = manager.forward(target_url)
                body = response.content
                self.send_response(response.status_code)

                for key, value in response.headers.items():
                    header = key.lower()
                    if header in {
                        "content-length",
                        "content-type",
                        "connection",
                        "server",
                        "transfer-encoding",
                    }:
                        continue
                    self.send_header(key, value)

                content_type = response.headers.get("Content-Type")
                if content_type is not None:
                    self.send_header("Content-Type", content_type)

                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except Exception as exc:
                self._send_json(502, {"error": str(exc)})
                return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/report":
            self._send_json(404, {"error": "Not found"})
            return

        payload = self._read_json_body()
        if not isinstance(payload, dict):
            self._send_json(400, {"error": "Invalid JSON payload"})
            return

        proxy =  payload.get("proxy")
        ok = payload.get("ok", False)

        if not isinstance(proxy, str):
            self._send_json(400, {"error": "Missing or invalid proxy"})
            return

        manager.report(proxy, bool(ok))
        self._send_json(200, {"ok": True})

    def _read_json_body(self) -> Any:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}

        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    logger.info("proxy-manager listening on 0.0.0.0:%s", PORT)
    server.serve_forever()


if __name__ == "__main__":
    main()
