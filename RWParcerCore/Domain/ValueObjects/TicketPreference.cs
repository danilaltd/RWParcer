namespace RWParcerCore.Domain.ValueObjects
{
    internal class TicketPreference
    {
        public decimal? Price { get; private set; }
        public TimeSpan? Time { get; private set; }
        public string Upper { get; private set; }    // Например, класс или разряд
        public string Lower { get; private set; }
        public string Side { get; private set; }
        public TimeSpan? UpdatePeriod { get; private set; }  // Период обновления
        public int? RemainingSeatsThreshold { get; private set; }  // Порог для уведомления при малом количестве мест

        public TicketPreference(decimal? price = null, TimeSpan? time = null, string upper = null,
                                 string lower = null, string side = null, TimeSpan? updatePeriod = null,
                                 int? remainingSeatsThreshold = null)
        {
            Price = price;
            Time = time;
            Upper = upper;
            Lower = lower;
            Side = side;
            UpdatePeriod = updatePeriod;
            RemainingSeatsThreshold = remainingSeatsThreshold;
        }

        // Метод для проверки корректности параметров
        public bool Validate()
        {
            // Реализовать проверку значений при необходимости
            return true;
        }
    }

}
