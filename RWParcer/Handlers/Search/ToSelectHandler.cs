using RWParcer.Interfaces;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.Search
{
    public class ToSelectHandler : StationSelectHandler
    {
        public ToSelectHandler(IFacade facade, ICommandRouter router)
            : base(facade,
                   router,
                   CommandNames.TrainSelect,
                   "Введите префикс станции назначения:",
                   "Станция назначения выбрана: {0}")
        { }
    }
}