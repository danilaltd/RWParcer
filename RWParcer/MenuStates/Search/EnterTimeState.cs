namespace RWParcer.MenuStates.Search
{
    public class EnterTimeState : InputMenuState
    {
        private readonly Route Route;
        private readonly List<string> req;
        public EnterTimeState(Route r, List<string> req)
        {
            Route = r;
            this.req = req;
        }
        public override MenuView GetMenu() => new(Header, req);
        protected override string BadInputMsg => "Введите корректное время";
        protected override string Header => "Выберите время отправления и время прибытия";
        protected virtual MenuView ErrorMessageGetButtons(List<string> but) => new(BadInputMsg + "\n\n" + Header, but);
        protected override MenuView HandleInput_main(string input, MenuContext context)
        {  
            if (req.Any(item => item.Equals(input, StringComparison.CurrentCultureIgnoreCase)))
            {
                //context.SetState(new EnterTimeState(new Route() { StationFrom = StationFrom, StationTo = req[0] });
                return context.GetMenu();
            } 
            return ErrorMessageGetButtons([.. req.Select(s => s)]);
        }
    }
}
