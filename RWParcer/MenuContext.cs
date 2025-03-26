using RWParcer.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

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

        public void DisplayOptions()
        {
            _currentState.DisplayOptions();
        }

        public void HandleInput(string input)
        {
            _currentState.HandleInput(input, this);
        }
    }
}
