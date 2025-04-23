using RWParcerCore.Domain.DTOs;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.Mappers
{
    internal static class StationMapper
    {
        public static StationVO FromDTO(RepoStation dto) => new (
            label: dto.Label ?? "",
            value: dto.Value ?? "",
            exp: dto.Exp ?? ""
        );
    }
}
