using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IRWService
{
    internal interface IGetStations
    {
        public Task<List<StationVO>> GetStationsAsync(string userId, string prefix);
    }
}
