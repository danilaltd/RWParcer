using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RWParcer
{
    public struct RouteWithTime
    {
        public Station StationFrom;
        public Station StationTo;
        public string Time;
        public RouteWithTime(Route route, string time)
        {
            StationFrom = route.StationFrom;
            StationTo = route.StationTo;
            Time = time;
        }
    }
}
