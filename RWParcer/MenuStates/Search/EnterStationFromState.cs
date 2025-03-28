namespace RWParcer.MenuStates.Search
{
    public class EnterStationFromState : InputMenuState
    {
        protected override string BadInputMsg => "Станция не найдена";
        protected override string Header => "Введите станцию отправления";
        public MenuView GetMenu(List<string> but) => new($"Найдено {but.Count} станций\n\n" + Header, but);
        protected override MenuView HandleInput_main(string input, MenuContext context)
        {
            List<Station> req = Parcer.GetStation(input);
            if (req.Count == 1 && string.Equals(input, req[0].label, StringComparison.OrdinalIgnoreCase))
            {
                context.SetState(new EnterStationToState(req[0]));
                return context.GetMenu();
            } 
            else if (req.Count == 0)
            {
                return ErrorMessageGetButtons();
            }
            return GetMenu([.. req.Select(s => s.label)]);
        }
    }
}
