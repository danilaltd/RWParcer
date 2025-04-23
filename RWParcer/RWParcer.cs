using RWParcer.NotNow;

namespace RWParcer
{
    public class RWParcer
    {
        //private readonly MenuContext menu;
        public RWParcer()
        {
            //menu = new(new MainMenuState());
        }
        public void Start() {
            //TempOutput(menu.HandleInput(""));
            //TempOutput(menu.HandleInput("поиск"));
            //TempOutput(menu.HandleInput("ст. Марьина Горка, г. Марьина Горка, Минская обл., Беларусь"));
            //TempOutput(menu.HandleInput("ст. Марьина Горка, г. Марьина Горка, Минская обл., Беларусь"));
            while (true)
            {
                string input = Console.ReadLine() ?? "";
                //TempOutput(menu.HandleInput(input));
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