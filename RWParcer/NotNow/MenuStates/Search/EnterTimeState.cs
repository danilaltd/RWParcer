namespace RWParcer.NotNow.MenuStates.Search
{
    //public class EnterTimeState : InputMenuState<RouteWithTime, RouteWithTime>
    //{
    //    private readonly Route Route;
    //    private readonly List<string> req;
    //    public EnterTimeState(Route r, List<string> req)
    //    {
    //        Route = r;
    //        this.req = req;
    //    }
    //    public override MenuView GetMenu() => new(Header, req);
    //    protected override string BadInputMsg => "Введите корректное время";
    //    protected override string Header => "Выберите время отправления и время прибытия";
    //    protected virtual MenuView ErrorMessageGetButtons(List<string> but) => new(BadInputMsg + "\n\n" + Header, but);
    //    protected override MenuView HandleInput_main(string input, MenuContext context)
    //    {
    //        throw new InvalidOperationException("Seems that path is not use");
    //    }

    //    protected override MenuView HandleInput_main(string input, MenuContextRequest<RouteWithTime> context)
    //    {
    //        if (req.Any(item => item.Equals(input, StringComparison.CurrentCultureIgnoreCase)))
    //        {
    //            context.done = true;
    //            context.error = false;
    //            Param = new RouteWithTime() { StationFrom = Route.StationFrom, StationTo = Route.StationTo, Time = input};
    //            return context.GetMenu();
    //        }
    //        return ErrorMessageGetButtons([.. req.Select(s => s)]);
    //    }

    //}
}
