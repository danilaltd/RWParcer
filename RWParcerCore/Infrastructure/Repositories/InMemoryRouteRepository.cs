using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class InMemoryRouteRepository : IRouteRepository
    {
        private readonly List<Route> _routes = new List<Route>();

        public void Add(Route route)
        {
            _routes.Add(route);
        }

        public void Update(Route route)
        {
            //var index = _routes.FindIndex(r => r.Id == route.Id);
            //if (index >= 0)
            //{
            //    _routes[index] = route;
            //}
            //else
            //{
            //    throw new KeyNotFoundException("Маршрут не найден");
            //}
        }

        public void Delete(Guid routeId)
        {
            //var route = _routes.FirstOrDefault(r => r.Id == routeId);
            //if (route != null)
            //{
            //    _routes.Remove(route);
            //}
            //else
            //{
            //    throw new KeyNotFoundException("Маршрут не найден");
            //}
        }

        //public Route GetById(Guid routeId)
        //{
            //return _routes.FirstOrDefault(r => r.Id == routeId);
        //}

        public IList<Route> GetByDate(DateTime date)
        {
            // Если для маршрута предусмотрено несколько дат, здесь следует
            // реализовать фильтрацию по датам. Пример ниже возвращает все маршруты.
            return _routes.Where(r => DateTime.TryParse(r.Time, out DateTime routeTime) &&
                                        routeTime.Date == date.Date).ToList();
        }

        public IList<Route> GetAll()
        {
            return _routes.ToList();
        }
    }


}
