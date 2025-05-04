namespace RWParcerCore.Infrastructure.Repositories
{
    internal abstract class RepositoryBase
    {
        private readonly IAppDbContextFactory _factory;

        protected RepositoryBase(IAppDbContextFactory factory)
        {
            _factory = factory;
        }

        protected async Task<TResult> QueryAsync<TResult>(Func<AppDbContext, Task<TResult>> action)
        {
            await using var ctx = _factory.CreateDbContext();
            return await action(ctx);
        }

        protected async Task ExecuteAsync(Func<AppDbContext, Task> action)
        {
            await using var ctx = _factory.CreateDbContext();
            await action(ctx);
        }
    }
}
