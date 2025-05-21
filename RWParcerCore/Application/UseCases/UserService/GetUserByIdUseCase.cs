using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.Mappers;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.UserService
{
    internal class GetUserByIdUseCase(IUserRepository userRepository) : IGetUserById
    {
        private readonly IUserRepository _userRepository = userRepository;

        public async Task<UserVO> GetUserByIdAsync(string userId, string targetId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            Exception? originalException = null;
            try
            {
                if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
                if (userId != targetId)
                {
                    if (!await _userRepository.IsUserModeratorAsync(userId)) throw new UnauthorizedAccessException($"{userId} tries get {targetId} status when not moder");
                    if (!await _userRepository.IsUserRegistredAsync(targetId)) throw new KeyNotFoundException($"User with ID {targetId} not found");
                }
                var u = UserMapper.FromEntity(await _userRepository.GetUserByIdAsync(targetId));
                return u;
            }
            catch (Exception ex)
            {
                originalException = ex;
                throw;
            }
            finally
            {
                try
                {
                    await _userRepository.UpdateActivityAsync(userId);
                }
                catch when (originalException != null) { }
            }
        }
    }
}
