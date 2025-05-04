using RWParcerCore.Application.Interfaces.IRWService;
using RWParcerCore.Domain.DTOs;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.Mappers;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.RWService
{
    internal class GetStationsUseCase(IRWRepository rwRepository, IUserRepository userRepository) : IGetStations
    {
        private readonly IUserRepository _userRepository = userRepository;

        private readonly IRWRepository _rwRepository = rwRepository;
        public async Task<List<StationVO>> GetStationsAsync(string userId, string prefix)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            List<RepoStation> ans = await _rwRepository.GetStationsAsync(prefix);
            return [.. ans.Select(item => StationMapper.FromDTO(item))];
        }
    }
}
