//namespace RWParcerCore.Domain.ValueObjects
//{
//    internal class TicketFilterVO : ValueObject
//    {
//        public HashSet<int> IncludeCarriages { get; private set; } = new();

//        public HashSet<int> ExcludeCarriages { get; private set; } = new();

//        public SeatOptions AllowedSeats { get; private set; } = SeatOptions.All;

//        public HashSet<int> IncludeSeats { get; private set; } = new();

//        public HashSet<int> ExcludeSeats { get; private set; } = new();

//        public bool IsMatch(int carriageNo, int seatNo, SeatOptions Seat)
//        {
//            // 1) по вагонам
//            if (ExcludeCarriages.Contains(carriageNo)) return false;
//            if (IncludeCarriages.Count > 0 && !IncludeCarriages.Contains(carriageNo))
//                return false;

//            // 2) по номерам мест
//            if (ExcludeSeats.Contains(seatNo)) return false;
//            if (IncludeSeats.Count > 0 && !IncludeSeats.Contains(seatNo))
//                return false;

//            // 3) по типу места
//            if (!AllowedSeats.HasFlag(Seat)) return false;

//            return true;
//        }


//        protected override IEnumerable<object> GetEqualityComponents()
//        {
//            yield return IncludeCarriages;
//            yield return ExcludeCarriages;
//            yield return AllowedSeats;
//            yield return IncludeSeats;
//            yield return ExcludeSeats;
//        }
//    }



//    [Flags]
//    public enum SeatOptions
//    {
//        None = 0,
//        Lower = 1 << 0,   // нижняя полка
//        Upper = 1 << 1,   // верхняя полка
//        SideLower = 1 << 2,   // боковая нижняя
//        SideUpper = 1 << 3,   // боковая верхняя

//        All = Lower | Upper | SideLower | SideUpper
//    }

//}
