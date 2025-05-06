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

            string number = "№" + train.TrainNumber;
            string name = train.TitleStationFrom + " - " + train.TitleStationTo;
            string type = ConvertType(train.TrainType);

            string trainDays = "Дни курсирования: " + train.TrainDays;
            if (train.TrainDaysExcept.Length != 0)
            {
                trainDays += ", кроме " + train.TrainDaysExcept;
            }

            return string.Join("\n", route, times, formattedDuration, number, name, type, trainDays);
        }

        private static string ConvertType(string type)
        {
            return type switch
            {
                "international" => "Международные линии",
                "interregional_economy" => "Межрегиональные линии экономкласса",
                "regional_economy" => "Региональные линии экономкласса",
                "regional_business" => "Региональные линии бизнес-класса",
                "interregional_business" => "Межрегиональные линии бизнес-класса",
                _ => type
            };
        }
    }
}
