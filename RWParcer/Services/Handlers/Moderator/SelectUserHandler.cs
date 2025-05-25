using RWParcer.Converters;
using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.Moderator
{
    public class SelectUserHandler(ICommandRouter router, IFacade facade) : ICommandHandler
    {
        private readonly IFacade _facade = facade;
        private readonly ICommandRouter _router = router;

        public async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.InitState)
            {
                await InitUsers(ctx);
                return;
            }

            await HandleTrainSelection(ctx);
        }

        private async Task InitUsers(CommandContext ctx)
        {
            var ts = ctx.Session.Data.OfType<TimeSpan>().FirstOrDefault();

            if (ts == default)
            {
                await ctx.ResetSessionAsync("Ошибка. Начните заново", _router);
                return;
            }

            var users = await _facade.GetUsersAsync(ctx.ChatId, ts);
            if (users.Count == 0)
            {
                await ctx.ResetSessionAsync("Нет пользователей за данный промежуток", _router);
                return;
            }

            ctx.Session.Data.Clear();
            ctx.Session.Data.Add(users);
            await ctx.SendKeyboard(
                users.Select(t => UserVOToStringConverter.Convert(t)),
                "Выберите пользователя:",
                true);
        }

        private async Task HandleTrainSelection(CommandContext ctx)
        {
            var usersList = ctx.Session.Data.OfType<List<UserVO>>().FirstOrDefault();
            if (usersList == null)
            {
                await ctx.ResetSessionAsync("Сессия устарела, начните заново", _router);
                return;
            }

            if (string.IsNullOrWhiteSpace(ctx.Input))
            {
                await ctx.SendMessage("Выберите пользователя из списка клавиатуры");
                return;
            }

            if (!(int.TryParse(ctx.Input, out int index) && index >= 1 && index <= usersList.Count))
            {
                await ctx.SendMessage("Введите корректный индекс пользователя");
                return;
            }

            var selected = usersList[index - 1];
            ctx.Session.Data.Clear();
            ctx.Session.Data.Add(selected);
            await ctx.SendMessage($"Вы выбрали пользователя: {UserVOToStringConverter.Convert(selected)}");
            ctx.Session.SetCommand(CommandNames.ManageUserMenuSelect);
            await _router.RouteAsync(CommandNames.ManageUserMenuSelect, ctx);
        }
    }

}