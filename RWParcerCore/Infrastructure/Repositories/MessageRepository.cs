using Microsoft.EntityFrameworkCore;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class MessageRepository(IAppDbContextFactory factory) : RepositoryBase(factory), IMessageRepository
    {
        public Task AddAsync(Message message)
        {
            ArgumentNullException.ThrowIfNull(message);
            return ExecuteAsync(async ctx =>
            {
                await ctx.Messages.AddAsync(message);
                await ctx.SaveChangesAsync();
            });
        }

        public Task<IEnumerable<Message>> GetAllMessagesAsync()
            => QueryAsync(async ctx =>
                (IEnumerable<Message>)await ctx.Messages.ToListAsync()
            );

        public Task<IEnumerable<Message>> GetUserMessagesAsync(string userId)
            => QueryAsync(async ctx =>
                (IEnumerable<Message>)await ctx.Messages
                    .Where(m => m.ReceiverId == userId)
                    .ToListAsync()
            );
    }
}
