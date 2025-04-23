namespace RWParcer.NotNow.MenuStates.Search
{
    //public class EnterStationFromState : InputMenuState<Station, RouteWithTime>
    //{
    //    protected override string BadInputMsg => "Станция не найдена";
    //    protected override string Header => "Введите станцию отправления";
    //    public MenuView GetMenu(List<string> but) => new($"Найдено {but.Count} станций\n\n" + Header, but);
    //    protected override MenuView HandleInput_main(string input, MenuContext context)
    //    {
    //        throw new InvalidOperationException("Seems that path is not use");
    //    }

    //    protected override MenuView HandleInput_main(string input, MenuContextRequest<RouteWithTime> context)
    //    {
    //        List<Station> req = Parcer.GetStation(input);
    //        if (req.Count == 0)
    //            return ErrorMessageGetButtons();
    //        if (req.Count == 1 && string.Equals(input, req[0].label, StringComparison.OrdinalIgnoreCase))
    //        {
    //            context.SetState(new EnterStationToState(req[0]));
    //            return context.GetMenu();
    //        }
    //        return GetMenu([.. req.Select(s => s.label)]);
    //    }
    //}
}
