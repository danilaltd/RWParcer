using RWParcer.MenuStates;

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
            TempOutput(menu.HandleInput(""));
            while (true)
            {
                string input = Console.ReadLine() ?? "";
                TempOutput(menu.HandleInput(input));
            }
        }

        private void TempOutput(MenuView a)
        {
            Console.WriteLine(a.header);
            foreach (var item in a.buttons)
            {
                Console.WriteLine($"\t{item}");
            }
        }
    }
}