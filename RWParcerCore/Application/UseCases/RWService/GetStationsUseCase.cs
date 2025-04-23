using RWParcerCore.Application.Interfaces.IRWService;
using RWParcerCore.Domain.DTOs;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.Mappers;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.RWService
{
    internal class GetStationsUseCase(IRWRepository rwRepository) : IGetStations
    {
        private readonly IRWRepository _rwRepository = rwRepository;
        public async Task<List<StationVO>> GetStationsAsync(string prefix)
        {
            List<RepoStation> ans = await _rwRepository.GetStationsAsync(prefix);
            return [.. ans.Select(item => StationMapper.FromDTO(item))];
        }
    }
}
