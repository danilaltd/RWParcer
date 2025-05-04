using RWParcerCore.Application.Interfaces.IRWService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.Mappers;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.RWService
{
    internal class GetTrainsUseCase(IRWRepository rwRepository, IUserRepository userRepository) : IGetTrains
    {
        private readonly IRWRepository _rwRepository = rwRepository;
        private readonly IUserRepository _userRepository = userRepository;
        public async Task<List<TrainVO>> GetTrainsForRouteAsync(string userId, RouteVO route)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            var ans = await _rwRepository.GetTrainsAsync(route);
            return [.. ans.Select(item => TrainMapper.FromDTO(item))];
        }
    }
}
