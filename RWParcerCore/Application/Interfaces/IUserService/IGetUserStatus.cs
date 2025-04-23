namespace RWParcerCore.Application.Interfaces.IUserService
{
    internal interface IGetUserStatus
    {
        Task<string> GetUserStatusAsync(string UserId);
    }
}
