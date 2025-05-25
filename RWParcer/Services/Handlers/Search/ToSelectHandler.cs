using RWParcer.Interfaces;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Services.Handlers.Search
{
    public class ToSelectHandler(IFacade facade, ICommandRouter router) : StationSelectHandler(facade,
               router,
               CommandNames.TrainSelect,
               "Введите префикс станции назначения:",
               "Станция назначения выбрана: {0}")
    {
    }
}