from dataclasses import replace

import asyncio
import time
from typing import Iterable
from aiohttp_socks import ProxyConnector
import aiohttp
import ssl

from ProxyTypes import ProxyStatus, ProxyDTO
from ValidationStrategy import BaseCheckStrategy, RwUrlStrategy, TestUrlStrategy
from config import CHECKS_ON_RW, CHECKS_ON_RW_SUCCESSED_NEED, CHECKS_ON_TEST_URL, CHECKS_ON_TEST_URL_SUCCESSED_NEED


class ProxyValidator:
    def __init__(self, test_url: str, timeout: float, concurrency: int) -> None:
        self._test_url = test_url
        self._timeout = timeout
        self._semaphore = asyncio.Semaphore(concurrency)
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE

    async def validate_single(self, proxy_url: str) -> ProxyDTO:
        start = time.perf_counter()
        connector = ProxyConnector.from_url(proxy_url, ssl=self._ssl_context)
        client_timeout = aiohttp.ClientTimeout(total=self._timeout)
        
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=client_timeout) as session:
                async with session.get(self._test_url, allow_redirects=True, ssl=self._ssl_context) as response:
                    await response.read()
                    latency_ms = int((time.perf_counter() - start) * 1000)
                    
                    if response.ok:
                        return ProxyDTO(proxy_url, ProxyStatus.ACTIVE, latency_ms)
                    return ProxyDTO(proxy_url, ProxyStatus.DEAD, latency_ms)
                    
        except Exception:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return ProxyDTO(proxy_url, ProxyStatus.DEAD, latency_ms)

    async def _run_checks(self, proxy: str, total_checks: int, needed_success: int, strategy: BaseCheckStrategy) -> ProxyDTO:
        success_count = 0
        res: ProxyDTO | None = None
        for _ in range(total_checks):
            current_test = await strategy.check(proxy)
            if res is None:
                res = current_test
            else:
                res |= current_test
                
            if current_test:
                success_count += 1
            if success_count >= needed_success:
                break

        if res is not None:
            if success_count >= needed_success:
                return replace(res, status=ProxyStatus.ACTIVE)
            else:
                return replace(res, status=ProxyStatus.DEAD)
        return ProxyDTO(url=proxy, status=ProxyStatus.DEAD, latency=5000)

    async def validate_all(self, proxies: Iterable[str]) -> list[ProxyDTO]:
        async def bounded_check(proxy: str) -> ProxyDTO:
            async with self._semaphore:
                first_test = await self._run_checks(proxy, CHECKS_ON_TEST_URL, CHECKS_ON_TEST_URL_SUCCESSED_NEED, strategy=TestUrlStrategy(self))
                if not first_test:
                    return first_test
                return await self._run_checks(proxy, CHECKS_ON_RW, CHECKS_ON_RW_SUCCESSED_NEED, strategy=RwUrlStrategy(self))

        tasks = [bounded_check(proxy) for proxy in proxies]
        res = await asyncio.gather(*tasks)

        return [p for p in res if p and p.status == ProxyStatus.ACTIVE]

    async def validate_single_on_rw(self, proxy_url: str) -> ProxyDTO:
        start = time.perf_counter()
        connector = ProxyConnector.from_url(proxy_url, ssl=self._ssl_context)
        client_timeout = aiohttp.ClientTimeout(total=self._timeout)
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=client_timeout) as session:
                async with session.get("https://apicast.rw.by/", allow_redirects=True, ssl=self._ssl_context) as response:
                    response_text = await response.text()
                    latency_ms = int((time.perf_counter() - start) * 1000)
                    
                    if (response.ok or response.status == 403) and "Authentication parameters missing" in response_text:
                        return ProxyDTO(proxy_url, ProxyStatus.ACTIVE, latency_ms)
                    return ProxyDTO(proxy_url, ProxyStatus.DEAD, latency_ms)
                    
        except Exception as e:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return ProxyDTO(proxy_url, ProxyStatus.DEAD, latency_ms)