using RWParcerCore.Domain.ValueObjects;

namespace RWParcer.Converters
{
    public static class TrainVOToStringConverter
    {
        public static string Convert(TrainVO train)
        {
            string route = train.StationFrom.Label + " - " + train.StationTo.Label;
            string times = $"{train.FromTime:HH:mm}→{train.ToTime:HH:mm}";
            string formattedDuration = $"{train.Duration.Hours:D2}:{train.Duration.Minutes:D2}";

            string number =  "№" + train.TrainNumber;
            string name = train.TitleStationFrom + " - " + train.TitleStationTo;
            string type = train.TrainType;

            string trainDays = "Дни курсирования: " + train.TrainDays;
            if (train.TrainDaysExcept.Length != 0)
            {
                trainDays += ", кроме " + train.TrainDaysExcept;
            }

            return string.Join("\n", route, times, formattedDuration, number, name, type, trainDays);
        }
    }
}
