using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.UserService
{
    internal class RegisterUserUseCase : IRegisterUser
    {
        private readonly IUserRepository _userRepository;
        public RegisterUserUseCase(IUserRepository userRepository)
        {
            _userRepository = userRepository;
        }
        public async Task RegisterUser(string id)
        {
            User? existingUser = await _userRepository.GetUserByIdAsync(id);
            if (existingUser != null) return;

            var newUser = new User(id);
            await _userRepository.AddUserAsync(newUser);
        }
    }
}
