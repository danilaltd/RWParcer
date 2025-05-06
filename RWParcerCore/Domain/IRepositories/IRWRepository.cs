using RWParcerCore.Domain.DTOs;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface IRWRepository
    {
        Task<List<RepoStation>> GetStationsAsync(string pref);
        Task<List<RepoTrain>> GetTrainsAsync(RouteVO route);
        Task<List<CarVO>> GetSeatsAsync(SubscriptionVO subscription);
    } 
}
