"""FastAPI web server entrypoint for running the web interface alongside the bot."""

from __future__ import annotations

import logging
import os

import uvicorn


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    uvicorn.run("app.web.app:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
