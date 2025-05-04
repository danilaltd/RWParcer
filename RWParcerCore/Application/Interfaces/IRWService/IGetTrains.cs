using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IRWService
{
    internal interface IGetTrains
    {
        public Task<List<TrainVO>> GetTrainsForRouteAsync(string userId, RouteVO route);
    }
}
