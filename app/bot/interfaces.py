"""Bot-side protocols, mirroring ``RWParcer/Interfaces/*``.

``ICommandHandler`` / ``ICommandRouter`` / ``IMenuProvider`` are the C#
interfaces the router, handlers and menu providers implement. Keeping them on
the ``context``/``router`` boundary avoids the circular imports the original
design produces with a service locator.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.bot.command_names import CommandNames
    from app.bot.context import CommandContext


class IMenuProvider(Protocol):
    """C# ``IMenuProvider.GetOptionsAsync`` — label -> next command."""

    async def get_options(self, ctx: CommandContext) -> dict[str, CommandNames]: ...


class ICommandHandler(Protocol):
    """C# ``ICommandHandler.HandleAsync``."""

    async def handle(self, ctx: CommandContext) -> None: ...


class ICommandRouter(Protocol):
    """C# ``ICommandRouter.RouteAsync``."""

    async def route(self, cmd: CommandNames | None, ctx: CommandContext) -> None: ...
