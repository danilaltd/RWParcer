#!/usr/bin/env python3

from __future__ import annotations
import asyncio
from http.client import HTTPResponse
import random
import sys
from typing import cast
from urllib.error import URLError
from urllib.request import urlopen

from ProxyDatabase import ProxyDatabase
from ProxyTypes import ProxyType, ProxyUrlList
from ProxyValidator import ProxyValidator
from config import CHECK_TIMEOUT_SECONDS, MAX_CONCURRENCY, PROXY_DB_PATH, RUN_EVERY_HOURS, SOURCE_URLS, TEST_URL
from utilities import normalize_proxy

class ProxyCollectorApp:
    def __init__(self, source_urls: list[ProxyUrlList], db_path: str, run_every_hours: int, validator: ProxyValidator) -> None:
        self.source_urls = source_urls
        self.run_every_hours = run_every_hours
        self.db = ProxyDatabase(db_path)
        self.validator = validator

    def fetch_raw_proxies(self) -> list[str]:
        proxies: set[str] = set()
        proxies.update(self.db.get_active_proxies())
        for url_list in self.source_urls:
            payload: str = ""
            try:
                with urlopen(url_list.urlList, timeout=30) as res:
                    response = cast(HTTPResponse, res)
                    payload = response.read().decode("utf-8", errors="ignore")
            except URLError as exc:
                print(f"Failed to fetch proxy list from {url_list.urlList}: {exc}", file=sys.stderr)
                continue
            if payload:
                splited = payload.splitlines()
                print(f"Fetched {len(splited)} lines from {url_list.urlList}")
                for line in splited:
                    item = normalize_proxy(line, url_list.type)
                    if item:
                        proxies.add(item)
                    else:
                        print(f"Couldn't normalize proxy {line}", file=sys.stderr)
            else:
                print("Payload from {url_list.urlList} eq None for some reason")
        return list(proxies)

    def export_to_file(self, file_path) -> None:
        active_proxies = self.db.get_active_proxies()
        with open(file_path, "w", encoding="utf-8") as handle:
            for proxy in active_proxies:
                handle.write(f"{proxy}\n")

    async def run_once(self) -> None:
        proxies = self.fetch_raw_proxies()
        random.shuffle(proxies)

        print(f"Will check {len(proxies)} proxies")
        results = await self.validator.validate_all(proxies)
        self.db.save_results(results)
        cleared = self.db.clear_old(self.run_every_hours)

        print(f"Checked {len(proxies)} proxies, saved {len(results)} active, cleared old {cleared}")

    async def start(self) -> None:
        if self.run_every_hours <= 0:
            await self.run_once()
            return

        while True:
            try:
                await self.run_once()
            except Exception as exc:
                print(f"Proxy collection failed: {exc}", file=sys.stderr)
            print(f"Now sleep for {self.run_every_hours}h for next proxy check", file=sys.stderr)
            await asyncio.sleep(self.run_every_hours * 3600)

if __name__ == "__main__":
    validator = ProxyValidator(TEST_URL, CHECK_TIMEOUT_SECONDS, MAX_CONCURRENCY)
    
    app = ProxyCollectorApp(
        source_urls=[
                ProxyUrlList(url, ProxyType[type_str]) 
                for url, type_str in SOURCE_URLS
            ],
        db_path=PROXY_DB_PATH,
        run_every_hours=RUN_EVERY_HOURS,
        validator=validator
    )
    asyncio.run(app.start())