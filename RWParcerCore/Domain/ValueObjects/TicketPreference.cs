namespace RWParcerCore.Domain.ValueObjects
{
    internal class TicketPreference(decimal? price = null, TimeSpan? time = null, string upper = "",
                             string lower = "", string side = "", TimeSpan? updatePeriod = null,
                             int? remainingSeatsThreshold = null)
    {
        public decimal? Price { get; private set; } = price;
        public TimeSpan? Time { get; private set; } = time;
        public string Upper { get; private set; } = upper;
        public string Lower { get; private set; } = lower;
        public string Side { get; private set; } = side;
        public TimeSpan? UpdatePeriod { get; private set; } = updatePeriod;
        public int? RemainingSeatsThreshold { get; private set; } = remainingSeatsThreshold;

        // Метод для проверки корректности параметров
        public static bool Validate()
        {
            // Реализовать проверку значений при необходимости
            return true;
        }
    }

}
