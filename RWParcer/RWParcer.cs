using RWParcer.MenuStates;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace RWParcer
{
    public class RWParcer
    {
        private readonly MenuContext menu;
        public RWParcer()
        {
            menu = new(new MainMenuState());
        }
        public void Start() {
            while (true)
            {
                menu.DisplayOptions();
                string input = Console.ReadLine() ?? "";
                menu.HandleInput(input);
            }
        }
    }
}