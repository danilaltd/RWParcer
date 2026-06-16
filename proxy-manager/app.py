from __future__ import annotations
import asyncio
from functools import partial
import json
import logging
import os
import random
import threading
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse
import requests
from requests import Response
import urllib3

from ProxyCollectorApp import ProxyCollectorApp
from ProxyDatabase import ProxyDatabase
from ProxyTypes import Proxy, ProxyRegistry, ProxyType, ProxyUrlList
from ProxyValidator import ProxyValidator
from config import CHECK_TIMEOUT_SECONDS, COLLECTOR_RUN_HOUR, FAILED_COOLDOWN_SECONDS, FORWARD_TIMEOUT_SECONDS, MAX_CONCURRENCY, MIN_HEALTHY_SCORE, PROXY_DB_PATH, PROXY_MANAGER_HEALTH_CHECK_INTERVAL, PROXY_MANAGER_PORT, SOURCE_URLS, TCP_CHECK_TIMEOUT_SECONDS, TEST_URL
from utilities import normalize_proxy


def setup_logging():
    if os.path.exists('/.dockerenv'):
        log_format = "%(levelname)s: %(message)s"
    else:
        log_format = "%(asctime)s %(levelname)s %(message)s"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
    )
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
setup_logging()
logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self, validator: ProxyValidator, proxy_db_path: str = PROXY_DB_PATH) -> None:
        self.proxies = ProxyRegistry(validator)
        self.proxies_lock = threading.RLock()
        self.db = ProxyDatabase(proxy_db_path)
        self.update_proxies_from_db()
        self._health_thread = threading.Thread(
            target=self._health_loop,
            name="proxy-health-check",
            daemon=True,
        )
        self._health_thread.start()
                    
    def _health_loop(self) -> None:
        while True:
            try:
                asyncio.run(self._run_health_checks())
            except Exception:
                logger.exception("Health-check loop failed")
            time.sleep(PROXY_MANAGER_HEALTH_CHECK_INTERVAL)

    async  def _run_health_checks(self) -> None:
        with self.proxies_lock:
            proxies = self.proxies.get_all()

        tasks = []
        for proxy in proxies:
            tasks.append(proxy.check_health()) 
        
        await asyncio.gather(*tasks)

    def update_proxies_from_db(self) -> None:
        with self.proxies_lock:
            self.proxies.clear()
            for proxy in self.db.get_active_proxies():
                normalized = normalize_proxy(proxy, ProxyType.UNKNOWN)
                if normalized is None:
                    continue

                self.proxies.get_or_create(normalized)

            proxies_len = len(self.proxies)
            
        logger.info(f"Fetched {proxies_len} from db")

    def get_next_proxy(self) -> str | None:
        with self.proxies_lock:
            now = time.time()
            healthy: list[Proxy] = [
                proxy
                for proxy in self.proxies.get_all()
                if proxy.is_available(now)
            ]

            if not healthy:
                return None

            weights = [max(1, proxy.score) for proxy in healthy]
            chosen = random.choices(healthy, weights=weights, k=1)[0]
            return chosen.url

    def report(self, proxy_url: str, ok: bool) -> None:
        with self.proxies_lock:
            proxy = self.proxies.get(proxy_url)
            if proxy is None:
                return

            if ok:
                proxy.score = min(100, proxy.score + 5)
            else:
                proxy.score = max(0, proxy.score - 20)
                proxy.cooldown_until = time.time() + FAILED_COOLDOWN_SECONDS

    def snapshot(self) -> dict[str, Any]:
        with self.proxies_lock:
            proxies: list[dict[str, Any]] = [
                {
                    "proxy": proxy.url,
                    "score": proxy.score,
                    "cooldown_until": proxy.cooldown_until,
                    "last_latency_ms": proxy.last_latency_ms,
                }
                for proxy in sorted(self.proxies.get_all(), key = lambda p: p.url)
            ]
            healthy_count = sum(
                1
                for proxy in self.proxies.get_all()
                if proxy.score >= MIN_HEALTHY_SCORE and time.time() >= proxy.cooldown_until
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
            verify=False,
        )
        logger.info(f"proxied {target_url} with {proxy}")
        return response


async def run_daily_collector(validator: ProxyValidator, callback: Callable[[], None]) -> None:
    collector = ProxyCollectorApp(
        source_urls=[
                ProxyUrlList(url, ProxyType[type_str]) 
                for url, type_str in SOURCE_URLS
            ],
        db_path=PROXY_DB_PATH,
        run_every_hours=24,
        validator=validator
    )

    while True:
        try:
            now = datetime.now()
            next_run = now.replace(hour=COLLECTOR_RUN_HOUR, minute=0, second=0, microsecond=0)
            if now >= next_run:
                next_run += timedelta(days=1)

            delay = (next_run - now).total_seconds()
            logger.info("Next proxy refresh scheduled for %s (in %s seconds)", next_run.isoformat(timespec="seconds"), int(delay))
            await asyncio.sleep(delay)

            logger.info("Running scheduled proxy refresh")
            await collector.run_once()
            callback()
        except Exception:
            logger.exception("Scheduled collector run failed")


class Handler(BaseHTTPRequestHandler):
    server_version = "ProxyManager/1.0"

    def __init__(self, manager: ProxyManager, *args, **kwargs) -> None:
        self.manager = manager
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._send_json(200, self.manager.snapshot())
            return

        if parsed.path == "/next":
            proxy = self.manager.get_next_proxy()
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
                response = self.manager.forward(target_url)
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
            except BrokenPipeError:
                logger.error(f"while proxing {target_url}: Broken Pipe - client closed connection")
            except Exception as exc:
                logger.error(f"while proxing {target_url}: {repr(exc)}")
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

        self.manager.report(proxy, bool(ok))
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
        try:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except BrokenPipeError:
                logger.error(f"BrokenPipeError while sending json")

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    validator = ProxyValidator(TEST_URL, CHECK_TIMEOUT_SECONDS, MAX_CONCURRENCY)
    manager = ProxyManager(validator)
    handler_with_args = partial(Handler, manager)
    
    server = ThreadingHTTPServer(("0.0.0.0", PROXY_MANAGER_PORT), handler_with_args)
    logger.info("proxy-manager listening on 0.0.0.0:%s", PROXY_MANAGER_PORT)

    scheduler_thread = threading.Thread(
        target=lambda: asyncio.run(run_daily_collector(validator, manager.update_proxies_from_db)),
        name="proxy-collector-scheduler",
        daemon=True,
    )
    scheduler_thread.start()

    server.serve_forever()


if __name__ == "__main__":
    main()
