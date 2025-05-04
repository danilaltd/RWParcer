namespace RWParcerCore.Infrastructure
{
    internal interface IAppDbContextFactory
    {
        AppDbContext CreateDbContext();
    }
}
