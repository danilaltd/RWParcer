namespace RWParcerCore.Domain.ValueObjects
{
    public class TrainVO(
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
        ) : ValueObject
    {
        public StationVO StationFrom { get; private set; } = new(fromStationDb, fromStationExp);
        public StationVO StationTo { get; private set; } = new(toStationDb, toStationExp);

        public string TrainType { get; private set; } = trainType;
        public string TrainNumber { get; private set; } = trainNumber;
        public string TitleStationFrom { get; private set; } = titleStationFrom;
        public string TitleStationTo { get; private set; } = titleStationTo;
        public TimeOnly FromTime { get; private set; } = UnixTimeToTimeOnly(fromTime);
        public TimeOnly ToTime { get; private set; } = UnixTimeToTimeOnly(toTime);
        public string TrainDays { get; private set; } = trainDays;
        public string TrainDaysExcept { get; private set; } = trainDaysExcept;
        public TimeSpan Duration { get; private set; } = TimeSpan.FromMinutes(durationMinutes);

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

        private static TimeOnly UnixTimeToTimeOnly(long unix)
        {
            var utcDateTime = DateTimeOffset.FromUnixTimeSeconds(unix).UtcDateTime;
            var minskTime = utcDateTime.AddHours(3);
            return TimeOnly.FromDateTime(minskTime);
        }

    }
}

