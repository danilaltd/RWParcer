using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RWParcer.NotNow
{
    public class MenuView
    {
        public readonly string header;
        public readonly List<string> buttons;
        public MenuView(string h, List<string> b)
        {
            header = h;
            buttons = b;
        }
    }
}
