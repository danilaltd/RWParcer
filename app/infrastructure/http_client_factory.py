from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from app.domain.protocols import Logger

DEFAULT_TIMEOUT = 10.0


class AsyncHttpClientFactory:
    """C# ``HttpClientFactoryWithProxyRotation``."""

    def __init__(
        self,
        proxy_manager_url: str | None = None,
        logger: Logger | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._proxy_url = (proxy_manager_url or "").rstrip("/")
        self.logger = logger
        # C# ``HttpClient`` follows redirects (default) and times out at 10 s.
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )

    @property
    def proxy_status(self) -> bool:
        """Whether a proxy-manager URL is configured (``IsNullOrWhiteSpace``)."""
        return bool(self._proxy_url)

    async def get_no_proxy(self, url: str) -> httpx.Response:
        """Direct GET — mirrors ``HttpFactory.GetAsyncNoProxy(url)``."""
        return await self._request(url)

    async def get_with_proxy(self, url: str) -> httpx.Response:
        """GET routed through proxy-manager — mirror of ``GetAsyncWithProxy``.

        Routes via ``{proxy_manager_url}/proxy?url={Uri.EscapeDataString(url)}``;
        when no URL is configured the request goes direct (C# fallback).
        """
        if not self._proxy_url:
            if self.logger is not None:
                self.logger.warning("proxy-manager URL is not configured, requesting directly")
            return await self.get_no_proxy(url)
        from urllib.parse import quote

        proxied = f"{self._proxy_url}/proxy?url=" + quote(url, safe="")
        return await self._request(proxied)

    async def _request(self, url: str) -> httpx.Response:
        try:
            return await self._client.get(url)
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            raise httpx.HTTPError(str(exc)) from exc

    async def aclose(self) -> None:
        await self._client.aclose()
