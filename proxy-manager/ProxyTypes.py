from __future__ import annotations
import asyncio
from dataclasses import dataclass
from enum import Enum, StrEnum, auto
import time
from typing import TYPE_CHECKING

from config import FAILED_COOLDOWN_SECONDS, MIN_HEALTHY_SCORE
if TYPE_CHECKING:
    from ProxyValidator import ProxyValidator

DEFAULT_SCORE = 70

class Proxy:
    def __init__(self,
                 url: str,
                 validator: ProxyValidator,
                 score: int = DEFAULT_SCORE,
                 cooldown_until: float = 0.0,
                 last_latency_ms: int | None = None,
    ) -> None:
        self.url = url
        self.score = score
        self.cooldown_until = cooldown_until
        self.last_latency_ms = last_latency_ms
        self._validator = validator
    
    def is_available(self, now: float) -> bool:
        return self.score >= MIN_HEALTHY_SCORE and now >= self.cooldown_until
    
    async def check_health(self):
        started = time.perf_counter()
        proxy_dto = await self._validator.validate_single(self.url)

        self.last_latency_ms = proxy_dto.latency
        if proxy_dto.status == ProxyStatus.ACTIVE:
            self.score = min(100, self.score + 1)
        else:
            self.score = max(0, self.score - 10)
            self.cooldown_until = started + FAILED_COOLDOWN_SECONDS
            

class ProxyRegistry:
    def __init__(self, validator) -> None:
        self._proxies: dict[str, Proxy] = {}
        self._validator = validator

    def __len__(self) -> int:
        return len(self._proxies)

    def add(self, proxy: Proxy) -> None:
        self._proxies[proxy.url] = proxy

    def get(self, url: str) -> Proxy | None:
        return self._proxies.get(url)

    def get_all(self) -> list[Proxy]:
        return list(self._proxies.values())

    def clear(self) -> None:
        self._proxies.clear()

    def get_or_create(self, url: str) -> Proxy:
        if url not in self._proxies:
            self._proxies[url] = Proxy(url=url, validator=self._validator)
        return self._proxies[url]



class ProxyStatus(StrEnum):
    ACTIVE = "active"
    DEAD = "dead"


@dataclass
class ProxyDTO:
    url: str
    status: ProxyStatus
    latency: int

    def __or__(self, other: ProxyDTO) -> ProxyDTO:
        if not isinstance(other, ProxyDTO):
            return NotImplemented
        
        if self.url != other.url:
            raise ValueError("OR on ProxyDTO should be with same url!")

        new_status = ProxyStatus.DEAD if (self.status == ProxyStatus.DEAD or other.status == ProxyStatus.DEAD) else ProxyStatus.ACTIVE
        avg_latency = (self.latency + other.latency) // 2

        return ProxyDTO(
            url=self.url,
            status=new_status,
            latency=avg_latency
        )
    
    def __bool__(self):
        return self.status == ProxyStatus.ACTIVE


class ProxyType(Enum):
    HTTP = auto()
    SOCKS4 = auto()
    SOCKS5 = auto()
    UNKNOWN = auto()


@dataclass
class ProxyUrlList:
    urlList: str
    type: ProxyType