from __future__ import annotations

from typing import TYPE_CHECKING
from ProxyTypes import ProxyDTO

if TYPE_CHECKING:
    from ProxyValidator import ProxyValidator

class BaseCheckStrategy:
    async def check(self, proxy: str) -> ProxyDTO:
        raise NotImplementedError

class TestUrlStrategy(BaseCheckStrategy):
    def __init__(self, validator_instance: ProxyValidator) -> None:
        self.validator = validator_instance

    async def check(self, proxy: str) -> ProxyDTO:
        return await self.validator.validate_single(proxy)

class RwUrlStrategy(BaseCheckStrategy):
    def __init__(self, validator_instance: ProxyValidator) -> None:
        self.validator = validator_instance

    async def check(self, proxy: str) -> ProxyDTO:
        return await self.validator.validate_single_on_rw(proxy)