namespace RWParcerCore.Domain.Entities
{
    internal struct Route
    {
        public Station StationFrom;
        public Station StationTo;
        public string Time;
        public Route(Station from, Station to, string time)
        {
            StationFrom = from;
            StationTo = to;
            Time = time;
        }

        public object DepartureStation { get; set; }
    }
}
