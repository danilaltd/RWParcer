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
        string toStationExp
        ) : ValueObject
    {
        public StationVO StationFrom = new(fromStationDb, fromStationDb, fromStationExp);
        public StationVO StationTo = new(toStationDb, toStationDb, toStationExp);
        public string TrainType { get; private set; } = trainType;
        public string TrainNumber { get; private set; } = trainNumber;
        public string TitleStationFrom { get; private set; } = titleStationFrom;
        public string TitleStationTo { get; private set; } = titleStationTo;
        public TimeOnly FromTime { get; private set; } = UnixTimeToDateOnly(fromTime);
        public TimeOnly ToTime { get; private set; } = UnixTimeToDateOnly(toTime);
        public string TrainDays { get; private set; } = trainDays;
        public string TrainDaysExcept { get; private set; } = trainDaysExcept;

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
        }

        private static TimeOnly UnixTimeToDateOnly(long unix) => TimeOnly.FromDateTime(
            DateTimeOffset.FromUnixTimeSeconds(unix)
                .ToOffset(TimeSpan.FromHours(3))
                .DateTime
        );
    }
}
                            
