"""FastAPI web interface sharing the application Facade."""

from __future__ import annotations

import datetime
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from app.domain.value_objects import Station, Train
from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

if TYPE_CHECKING:
    from app.application.facade import Facade

templates = Jinja2Templates(directory="app/web/templates")


def create_web_app(facade: Facade) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):  # noqa: ANN202
        await facade.register_user(1, 1, "testuser", "Test User")
        yield

    app = FastAPI(title="RWParcer Web", lifespan=lifespan)
    app.state.facade = facade

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

    return app
