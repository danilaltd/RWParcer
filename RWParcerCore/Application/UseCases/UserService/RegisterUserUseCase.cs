using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.UserService
{
    internal class RegisterUserUseCase(IUserRepository userRepository) : IRegisterUser
    {
        private readonly IUserRepository _userRepository = userRepository;

        public async Task RegisterUserAsync(string userId)
        {
            if (await _userRepository.IsUserRegistredAsync(userId)) return;// throw new KeyNotFoundException($"User with ID {userId} already exists");

            var newUser = new User(userId);
            //if (userId.Contains("moderator")) newUser.Promote();
            await _userRepository.AddAsync(newUser);
        }
    }
}
