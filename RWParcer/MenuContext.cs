using RWParcer.Interfaces;

namespace RWParcer
{
    public class MenuContext
    {
        private IMenuState _currentState;

        public MenuContext(IMenuState initialState)
        {
            _currentState = initialState;
        }

        public void SetState(IMenuState newState)
        {
            _currentState = newState;
        }

        public MenuView GetMenu()
        {
            return _currentState.GetMenu();
        }

        public MenuView GetMenu(string s)
        {
            return _currentState.GetMenu(s);
        }

        public MenuView HandleInput(string input)
        {
            return _currentState.HandleInput(input, this);
        }
    }
}
