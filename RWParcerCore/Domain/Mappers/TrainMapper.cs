using RWParcerCore.Domain.DTOs;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.Mappers
{
    internal static class TrainMapper
    {
        public static TrainVO FromDTO(RepoTrain dto) => new(
            trainType: dto.TrainType ?? "",
            trainNumber: dto.TrainNumber ?? "",
            titleStationFrom: dto.TitleStationFrom ?? "",
            titleStationTo: dto.TitleStationTo ?? "",
            fromStationDb: dto.FromStationDb ?? "",
            toStationDb: dto.ToStationDb ?? "",
            fromTime: dto.FromTime ?? 0,
            toTime: dto.ToTime ?? 0,
            trainDays: dto.TrainDays ?? "",
            trainDaysExcept: dto.TrainDaysExcept ?? "",
            fromStationExp: dto.FromStationExp ?? "",
            toStationExp: dto.ToStationExp ?? "",
            durationMinutes: dto.DurationMinutes ?? 0
        );
    }
}
