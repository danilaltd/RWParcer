"""Client for the rw.by endpoints — port of ``RWParcer.cs``.

Endpoints (exact):
  stations: https://pass.rw.by/ru/ajax/autocomplete/search/?term=<prefix>  (no proxy)
  trains:   https://apicast.rw.by/v1/rasp/ru/index/route                 (no proxy)
  seats:    https://apicast.rw.by/v1/rasp/ru/index/car_places            (via proxy)

Retry semantics are preserved: up to 5 attempts per request, 10 ms pause
between attempts, log lines byte-identical to the C# ``LogDebug`` messages.
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

from app.domain import times
from app.domain.value_objects import Car, CarType, Route, Station, SubscriptionDetails, Train

if TYPE_CHECKING:
    import httpx

    from app.domain.protocols import Logger
    from app.infrastructure.http_client_factory import AsyncHttpClientFactory

USER_KEY = "c2a3d81674b7f4c9e4af16bdba110d53"
GET_STATIONS_URL = "https://pass.rw.by/ru/ajax/autocomplete/search/?term="
GET_TRAINS_URL = "https://apicast.rw.by/v1/rasp/ru/index/route"
GET_SEATS_URL = "https://apicast.rw.by/v1/rasp/ru/index/car_places"
MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 0.01  # C# ``Task.Delay(10ms)``


class RwClient:
    """Implements the ``RwRepository`` protocol against ``rw.by``."""

    def __init__(self, http: AsyncHttpClientFactory, logger: Logger) -> None:
        self._http = http
        self.logger = logger

    async def get_stations(self, prefix: str) -> list[Station]:
        """``GetStationsAsync`` — no proxy, tolerates exhaustion with ``[]``."""
        full_url = GET_STATIONS_URL + prefix
        response = await self._fetch_with_retries(full_url, direct=True)
        if response is None:
            self.logger.debug("Все попытки исчерпаны, возвращаем пустой массив.")
            return []
        stations: list[Station] = []
        for item in self._parse_stations_list(response.text):
            stations.append(Station(label=item.get("label") or "", exp=item.get("exp") or ""))
        return stations

    async def get_trains(self, route: Route) -> list[Train]:
        """``GetTrainsAsync`` — reads ``routes``, tolerates missing/dirty items."""
        url = self._build_trains_url(route)
        response = await self._fetch_with_retries(url, direct=True)
        if response is None:
            self.logger.debug("Все попытки исчерпаны, возвращаем пустой массив.")
            return []
        try:
            root = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.debug("Ошибка: JSON не содержит маршрутов.")
            return []
        if not isinstance(root, dict) or "routes" not in root:
            self.logger.debug("Ошибка: JSON не содержит маршрутов.")
            return []
        routes = root["routes"]
        trains: list[Train] = []
        for index, item in enumerate(routes):
            if not isinstance(item, dict):
                continue
            try:
                trains.append(self._dto_to_train(item))
            except (TypeError, ValueError, OverflowError) as exc:
                # Newtonsoft ``Error`` handler: log and keep going (Handled = true).
                self.logger.debug(f"Ошибка при десериализации routes[{index}]: {exc}")
        return trains

    async def get_seats(self, details: SubscriptionDetails) -> list[Car]:
        result: list[Car] = []
        for car_type in range(1, 7):
            url = self._build_seats_url(details, car_type)
            response = await self._fetch_with_retries(url, direct=False)
            if response is None:
                self.logger.debug("Все попытки исчерпаны, throw new exception.")
                raise TimeoutError("max_retries")
            try:
                root = json.loads(response.text)
            except json.JSONDecodeError as exc:
                self.logger.debug(f"Ошибка десериализации JSON: {exc}")
                raise
            if not isinstance(root, dict):
                raise TimeoutError("max_retries")
            tariffs = root.get("tariffs")
            if not isinstance(tariffs, list):
                continue
            for tariff in tariffs:
                if not isinstance(tariff, dict):
                    continue
                cars = tariff.get("cars")
                if not isinstance(cars, list):
                    continue
                for car in cars:
                    if not isinstance(car, dict):
                        continue
                    car_form = self._parse_car(car, car_type)
                    if car_form is not None:
                        result.append(car_form)
        return result

    # -- internals -----------------------------------------------------------

    @staticmethod
    def _parse_stations_list(text: str) -> list[dict]:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return []
        if not isinstance(payload, list):
            return []
        return [item for item in payload if isinstance(item, dict)]

    def _build_trains_url(self, route: Route) -> str:
        from urllib.parse import urlencode

        params = {
            "format": "json",
            "from_exp": route.from_station.exp,
            "to_exp": route.to_station.exp,
            "date": "everyday",
            "user_key": USER_KEY,
        }
        return GET_TRAINS_URL + "?" + urlencode(params)

    def _build_seats_url(self, details: SubscriptionDetails, car_type: int) -> str:
        from urllib.parse import urlencode

        params = {
            "format": "json",
            "from": details.train.station_from.exp,
            "to": details.train.station_to.exp,
            "date": details.date.strftime("%Y-%m-%d"),
            "train_number": details.train.train_number,
            "car_type": str(car_type),
            "user_key": USER_KEY,
        }
        return GET_SEATS_URL + "?" + urlencode(params)

    async def _fetch_with_retries(self, url: str, direct: bool) -> httpx.Response | None:
        """C# retry loop; returns the first successful response or ``None``."""
        attempt = 0
        response = None
        while attempt < MAX_RETRIES:
            attempt += 1
            try:
                response = (
                    await self._http.get_no_proxy(url)
                    if direct
                    else await self._http.get_with_proxy(url)
                )
                if response.is_success:
                    break
                self.logger.debug(f"Попытка {attempt}: Ошибка {response.status_code}")
            except Exception as exc:
                self.logger.debug(f"Попытка {attempt}: Ошибка {exc}")
            await asyncio.sleep(RETRY_DELAY_SECONDS)
        if response is None or not response.is_success:
            return None
        return response

    @staticmethod
    def _dto_to_train(item: dict) -> Train:
        return Train(
            train_type=item.get("train_type") or "",
            train_number=item.get("train_number") or "",
            title_station_from=item.get("title_station_from") or "",
            title_station_to=item.get("title_station_to") or "",
            station_from=Station(
                item.get("from_station_db") or "",
                item.get("from_station_exp") or "",
            ),
            station_to=Station(
                item.get("to_station_db") or "",
                item.get("to_station_exp") or "",
            ),
            from_time=times.unix_seconds_to_local_time(int(item.get("from_time") or 0)),
            to_time=times.unix_seconds_to_local_time(int(item.get("to_time") or 0)),
            train_days=item.get("train_days") or "",
            train_days_except=item.get("train_days_except") or "",
            duration_minutes=int(item.get("duration_minutes") or 0),
        )

    def _parse_car(self, car: dict, car_type: int) -> Car | None:
        """One ``cars[]`` item; null checks and log lines match ``RWParcer.cs``.

        ``uint.Parse`` failures propagate (the C# had no try/catch there), so an
        invalid ``number``/seat string escapes up to the retry loop in the
        notifier — matching the original exception-flow.
        """
        number = car.get("number")
        places = car.get("emptyPlaces")
        if number is None or places is None:
            if number is None:
                self.logger.debug("carNumberStr null")
            return None
        car_number = int(str(number))
        seats: list[int] = []
        for seat in places:
            if seat is None:
                self.logger.debug("seatStr null")
                continue
            seats.append(int(str(seat)))
        return Car(car_type=CarType(car_type), number=car_number, free_seats=tuple(seats))
