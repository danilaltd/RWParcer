"""FastAPI web interface sharing the application Facade."""

from __future__ import annotations

import datetime
from contextlib import asynccontextmanager

from app.application.facade import Facade
from app.config import load_settings
from app.domain.value_objects import Station, Train
from app.infrastructure.db.pool import ConnectionPool
from app.infrastructure.db.repositories import (
    AvailabilitySnapshotPostgresRepository,
    FavoritePostgresRepository,
    MessagePostgresRepository,
    NotificationPostgresRepository,
    RolePostgresRepository,
    ServiceRoutePostgresRepository,
    SubscriptionPostgresRepository,
    UserPostgresRepository,
    UserRolePostgresRepository,
)
from app.infrastructure.http_client_factory import AsyncHttpClientFactory
from app.infrastructure.logging import PythonLogger
from app.infrastructure.rw_client import RwClient
from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/web/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    settings = load_settings()
    logger = PythonLogger("rwparcer-web")
    connection_pool = await ConnectionPool.create(settings.database)

    role = RolePostgresRepository(connection_pool)
    user_role = UserRolePostgresRepository(connection_pool, role)
    users = UserPostgresRepository(connection_pool, user_role)
    service_route = ServiceRoutePostgresRepository(connection_pool)
    snapshot = AvailabilitySnapshotPostgresRepository(connection_pool)
    subscriptions = SubscriptionPostgresRepository(connection_pool, service_route, snapshot)
    favorites = FavoritePostgresRepository(connection_pool, service_route)
    notifications = NotificationPostgresRepository(connection_pool)
    messages = MessagePostgresRepository(connection_pool)

    http = AsyncHttpClientFactory(
        proxy_manager_url=settings.proxy.proxy_manager_url,
        logger=logger,
    )
    rw = RwClient(http, logger)

    facade = Facade(
        users=users,
        transport=service_route,
        subscriptions=subscriptions,
        favorites=favorites,
        notifications=notifications,
        messages=messages,
        rw=rw,
    )

    app.state.facade = facade
    app.state.connection_pool = connection_pool

    await facade.register_user(1, 1, "testuser", "Test User")
    yield
    await connection_pool.close()


app = FastAPI(title="RWParcer Web", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_id: int = 1, chat_id: int = 1) -> HTMLResponse:
    fac: Facade = request.app.state.facade
    uid = await fac.authenticate_user(user_id, chat_id)
    favorites = await fac.get_favorites(uid)
    messages = await fac.get_messages(uid)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "favorites": favorites,
            "messages": messages,
        },
    )


@app.post("/favorites/add", response_class=RedirectResponse)
async def add_favorite(
    request: Request,
    user_id: int = Form(...),
    chat_id: int = Form(...),
    train_type: str = Form("p"),
    train_number: str = Form(...),
    station_from: str = Form(...),
    station_to: str = Form(...),
    dep_time: str = Form("08:00"),
    arr_time: str = Form("10:00"),
) -> RedirectResponse:
    fac: Facade = request.app.state.facade
    uid = await fac.authenticate_user(user_id, chat_id)
    from_time = datetime.time.fromisoformat(dep_time)
    to_time = datetime.time.fromisoformat(arr_time)
    train = Train(
        train_type=train_type,
        train_number=train_number,
        main_station_from=Station(station_from, station_from),
        main_station_to=Station(station_to, station_to),
        station_from=Station(station_from, station_from),
        station_to=Station(station_to, station_to),
        from_time=from_time,
        to_time=to_time,
        train_days="",
        train_days_except="",
        duration_minutes=120,
    )
    await fac.add_to_favorites(uid, train)
    return RedirectResponse(url=f"/?user_id={user_id}", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/feedback/send", response_class=RedirectResponse)
async def send_feedback(
    request: Request,
    user_id: int = Form(...),
    chat_id: int = Form(...),
    content: str = Form(...),
) -> RedirectResponse:
    fac: Facade = request.app.state.facade
    uid = await fac.authenticate_user(user_id, chat_id)

    await fac.send_feedback(uid, content)
    return RedirectResponse(url=f"/?user_id={user_id}", status_code=status.HTTP_303_SEE_OTHER)
