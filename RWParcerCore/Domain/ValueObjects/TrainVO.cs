namespace RWParcerCore.Domain.ValueObjects
{
    public class TrainVO : ValueObject
    {
        public StationVO StationFrom { get; private set; }
        public StationVO StationTo { get; private set; }
        public TrainVO(
            string trainType,
            string trainNumber,
            string titleStationFrom,
            string titleStationTo,
            string fromStationDb,
            string toStationDb,
            long fromTime,
            long toTime,
            string trainDays,
            string trainDaysExcept,
            string fromStationExp,
            string toStationExp,
            uint durationMinutes
        )
        {
            StationFrom = new(fromStationDb, fromStationExp);
            StationTo = new(toStationDb, toStationExp);
            TrainType = trainType;
            TrainNumber = trainNumber;
            TitleStationFrom = titleStationFrom;
            TitleStationTo = titleStationTo;
            FromTime = UnixTimeToTimeOnly(fromTime);
            ToTime = UnixTimeToTimeOnly(toTime);
            TrainDays = trainDays;
            TrainDaysExcept = trainDaysExcept;
            Duration = TimeSpan.FromMinutes(durationMinutes);
        }
        
        public string TrainType { get; private set; }
        public string TrainNumber { get; private set; }
        public string TitleStationFrom { get; private set; }
        public string TitleStationTo { get; private set; }
        public TimeOnly FromTime { get; private set; }
        public TimeOnly ToTime { get; private set; }
        public string TrainDays { get; private set; }
        public string TrainDaysExcept { get; private set; }
        public TimeSpan Duration { get; private set; }

        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return StationFrom;
            yield return StationTo;
            yield return TrainType;
            yield return TrainNumber;
            yield return TitleStationFrom;
            yield return TitleStationTo;
            yield return FromTime;
            yield return ToTime;
            yield return TrainDays;
            yield return TrainDaysExcept;
            yield return Duration;
        }

        private static TimeOnly UnixTimeToTimeOnly(long unix) => TimeOnly.FromDateTime(
            DateTimeOffset.FromUnixTimeSeconds(unix)
                .ToOffset(TimeSpan.FromHours(3))
                .DateTime
        );
    }
}
                            
