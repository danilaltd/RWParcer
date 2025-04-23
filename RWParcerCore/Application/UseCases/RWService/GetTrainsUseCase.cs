using RWParcerCore.Application.Interfaces.IRWService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.Mappers;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.RWService
{
    internal class GetTrainsUseCase : IGetTrains
    {
        private readonly IRWRepository _rwRepository;
        public GetTrainsUseCase(IRWRepository rwRepository)
        {
            _rwRepository = rwRepository;
        }

        public async Task<List<TrainVO>> GetTrainsForRouteAsync(RouteVO route)
        {
            var ans = await _rwRepository.GetTrainsAsync(route);
            return ans.Select(item => TrainMapper.FromDTO(item)).ToList();
        }
    }
}
