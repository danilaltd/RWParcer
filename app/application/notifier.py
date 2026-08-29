"""Background notifier mirroring ``NotificationBackgroundService``.

Semantics preserved from the C# service:

* The loop re-fetches all subscriptions continuously (10 ms pause only when
  the table is empty) — there is **no** periodic sleep between iterations.
* Expired subscriptions (``date < today UTC``) are removed; a removal aborts
  the current pass.
* Each subscription is processed under a global semaphore
  (``max_concurrency``) with up to ``max_retries`` attempts.
* A subscription is skipped while ``now - LastUpdate < user.MinUpdateInterval``.
* The page life-cycle of ``CarVO`` state introduces the exact diff strings.
"""

from __future__ import annotations

import asyncio
import datetime
import uuid

from app.application.errors import HttpRequestError
from app.domain.entities import Notification, Subscription
from app.domain.protocols import (
    Logger,
    NotificationRepository,
    RwRepository,
    SubscriptionRepository,
    UserRepository,
)
from app.domain.value_objects import Car, SubscriptionDetails, Train, car_type_label

UTC = datetime.UTC


class Notifier:
    def __init__(
        self,
        subscriptions: SubscriptionRepository,
        notifications: NotificationRepository,
        users: UserRepository,
        rw: RwRepository,
        logger: Logger,
        max_retries: int = 5,
        max_concurrency: int = 15,
    ) -> None:
        self._subscriptions = subscriptions
        self._notifications = notifications
        self._users = users
        self._rw = rw
        self.logger = logger
        self._max_retries = max_retries
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def run(self, stop: asyncio.Event) -> None:
        """Main notifier loop (``StartAsync``)."""
        self.logger.debug("Waiting...")
        while not stop.is_set():
            try:
                subscriptions = await self._subscriptions.get_all_subscriptions()
                if not subscriptions:
                    await asyncio.sleep(10)  # C# ``Task.Delay(10)``
                if await self._unsubscribe_expired(subscriptions):
                    continue
                await asyncio.gather(
                    *(self._process_subscription(s) for s in subscriptions)
                )
            except Exception as exc:
                self.logger.debug(f"Неизвестная ошибка: {exc}")

    async def _unsubscribe_expired(self, subscriptions: list[Subscription]) -> bool:
        today = datetime.datetime.now(UTC).date()  # DateOnly.FromDateTime(UtcNow)
        expired = [s for s in subscriptions if s.details.date < today]
        for subscription in expired:
            await self._subscriptions.remove_subscription(subscription)
        return len(expired) > 0

    async def _process_subscription(self, subscription: Subscription) -> None:
        async with self._semaphore:
            for attempt in range(1, self._max_retries + 1):
                try:
                    now = datetime.datetime.now(UTC)
                    min_interval = datetime.timedelta(
                        seconds=await self._users.get_user_min_interval(
                            subscription.user_id
                        )
                    )
                    if (
                        subscription.last_update is not None
                        and now - subscription.last_update < min_interval
                    ):
                        break
                    self.logger.debug(f"Попытка {attempt}: Запрос {subscription.id}")
                    response = await self._rw.get_seats(subscription.details)
                    actual = await self._subscriptions.get_by_id(subscription.id)
                    if actual is None:
                        break
                    if not self._states_equal(response, actual.last_state):
                        self.logger.debug(f"Изменение данных для {subscription.id}\n")
                        changes = self._find_seat_changes(
                            actual.last_state, response
                        )
                        if changes:
                            await self._notifications.add_notification(
                                Notification(
                                    id=uuid.uuid4(),
                                    user_id=subscription.user_id,
                                    content=self._build_change_message(
                                        subscription.details,
                                        actual.last_state,
                                        changes,
                                    ),
                                )
                            )
                        elif response:
                            raise RuntimeError(
                                f"unsupported changes {actual.id}"
                            )
                        actual.last_state = response
                        await self._subscriptions.update_subscription(actual)
                    actual.last_update = now
                    await self._subscriptions.update_subscription(actual)
                    break
                except TimeoutError:
                    self.logger.debug(
                        f"Тайм-аут запроса для {subscription.id} (Попытка {attempt})"
                    )
                except HttpRequestError as exc:
                    self.logger.debug(
                        f"Ошибка HTTP ({subscription.id}, Попытка {attempt}): {exc}"
                    )
                except Exception as exc:
                    self.logger.debug(
                        f"Неизвестная ошибка ({subscription.id}, Попытка {attempt}): {exc}"
                    )

    @staticmethod
    def _build_change_message(
        details: SubscriptionDetails,
        old_state: list[Car] | None,
        changes: list[str],
    ) -> str:
        header = f"{details.date:%d.%m.%Y}\n{convert_train(details.train)}\n"
        # C# ``LastState is not null ? "Изменены места" : "Свободные места"``;
        # ``Subscription.LastState`` is initialized to ``[]`` so it is effectively
        # always "Изменены места".
        label = "Изменены места" if old_state is not None else "Свободные места"
        return f"{header}{label}: \n{chr(10).join(changes)}"

    @staticmethod
    def _states_equal(l1: list[Car] | None, l2: list[Car] | None) -> bool:
        if l1 is None or l2 is None:
            return False
        if len(l1) != len(l2):
            return False
        return all(
            a == b
            for a, b in zip(
                sorted(l1, key=lambda c: c.number),
                sorted(l2, key=lambda c: c.number),
                strict=False,
            )
        )

    @staticmethod
    def _find_seat_changes(
        old_state: list[Car] | None, new_state: list[Car] | None
    ) -> list[str]:
        changes: list[str] = []
        old_safe = old_state or []
        new_safe = new_state or []

        for old_car in sorted(old_safe, key=lambda c: c.number):
            new_car = next((c for c in new_safe if c.number == old_car.number), None)
            if new_car is not None:
                removed = [s for s in old_car.free_seats if s not in new_car.free_seats]
                added = [s for s in new_car.free_seats if s not in old_car.free_seats]
                if removed:
                    changes.append(
                        f"{car_type_label(old_car.car_type)} №{old_car.number}: "
                        f"Заняты места {', '.join(map(str, removed))}"
                    )
                if added:
                    changes.append(
                        f"{car_type_label(old_car.car_type)} №{old_car.number}: "
                        f"Освобождены места {', '.join(map(str, added))}"
                    )
            else:
                changes.append(
                    f"{car_type_label(old_car.car_type)} №{old_car.number}: "
                    f"Все места удалены"
                )

        for new_car in sorted(new_safe, key=lambda c: c.number):
            if not any(c.number == new_car.number for c in old_safe):
                changes.append(
                    f"{car_type_label(new_car.car_type)} №{new_car.number}: "
                    f"Новый вагон, места {', '.join(map(str, new_car.free_seats))}"
                )
        return changes


def convert_train(train: Train) -> str:
    route = f"{train.station_from.label} - {train.station_to.label}"
    times = f"{train.from_time:%H:%M}→{train.to_time:%H:%M}"
    return "\n".join((route, times))
