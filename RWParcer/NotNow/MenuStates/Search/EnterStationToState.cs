namespace RWParcer.NotNow.MenuStates.Search
{
    //public class EnterStationToState : InputMenuState<Route, RouteWithTime>
    //{
    //    private Station StationFrom;
    //    public EnterStationToState(Station s)
    //    {
    //        StationFrom = s;
    //    } 
    //    protected override string BadInputMsg => "Станция не найдена";
    //    protected override string Header => "Введите станцию прибытия";
    //    public MenuView GetMenu(List<string> but) => new($"Найдено {but.Count} станций\n\n" + Header, but);
    //    protected override MenuView HandleInput_main(string input, MenuContext context)
    //    {
    //        throw new InvalidOperationException("Seems that path is not use");
            
    //    }

    //    protected override MenuView HandleInput_main(string input, MenuContextRequest<RouteWithTime> context)
    //    {
    //        List<Station> req = Parcer.GetStation(input);
    //        if (req.Count == 1 && string.Equals(input, req[0].label, StringComparison.OrdinalIgnoreCase))
    //        {
    //            Route route = new() { StationFrom = StationFrom, StationTo = req[0] };
    //            List<string> times = Parcer.GetTimes(route);
    //            if (times.Count == 0)
    //            {
    //                context.SetState(new MainMenuState());
    //                return context.GetMenu("Нет прямого сообщения между станциями. Возврат в главное меню");
    //            }
    //            context.SetState(new EnterTimeState(route, times));
    //            return context.GetMenu();
    //        }
    //        else if (req.Count == 0)
    //        {
    //            return ErrorMessageGetButtons();
    //        }
    //        return GetMenu([.. req.Select(s => s.label)]);
    //    }
    //}
}
