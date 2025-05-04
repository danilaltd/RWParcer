using RWParcer.Interfaces;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.Search
{
    public class FromSelectHandler : StationSelectHandler
    {
        public FromSelectHandler(IFacade facade, ICommandRouter router)
            : base(facade,
                   router,
                   CommandNames.ToSelect,
                   "Введите префикс станции отправления:",
                   "Станция отправления выбрана: {0}")
        { }
    }
}