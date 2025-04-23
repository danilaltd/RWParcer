using RWParcer.NotNow;
using RWParcer.NotNow.Interfaces;
using RWParcer.NotNow.MenuStates.Abstract;
using System.Reflection;

namespace RWParcer
{
    public class MenuContext
    {
        protected IMenuState _currentState;
        public MenuContext(IMenuState initialState)
        {
            _currentState = initialState;
        }

        public bool AddMenuContext<T, V>() where V : IMenuState, new()
        {
            if (_currentState is ChooseMenuRequestState<T> chooseMenuRequestState)
            {
                chooseMenuRequestState.MenuRequest = new MenuContextRequest<T>(new V());
                return true;
            }

            return false;
        }



        public void SetState(IMenuState newState)
        {
            _currentState = newState;
        }

        public MenuView GetMenu()
        {
            var property = _currentState.GetType().GetProperty("MenuRequest");

            if (property != null)
            {
                var menuRequest = property.GetValue(_currentState);

                if (menuRequest != null)
                {
                    var getMenuMethod = menuRequest.GetType().GetMethod(
                    "GetMenu",
                    BindingFlags.Public | BindingFlags.Instance,
                    null,
                    Type.EmptyTypes,
                    null
                );


                    if (getMenuMethod != null && getMenuMethod.Invoke(menuRequest, null) is MenuView ret)
                    {
                        return ret;
                    }

                }
            }

            return _currentState.GetMenu();

        }

        public MenuView GetMenu(string s)
        {
            var menuRequest = _currentState.GetType().GetProperty("MenuRequest")?.GetValue(_currentState);
            if (menuRequest?.GetType().GetMethod("GetMenu", BindingFlags.Public | BindingFlags.Instance, null, Type.EmptyTypes, null)
                    ?.Invoke(menuRequest, null) is MenuView ret)
            {
                throw new Exception("кажется это можно удалить");
                //return ret;
            }
            if (_currentState is ChooseMenuRequestState<object> menuRequestState && menuRequestState.MenuRequest != null)
            {
                return menuRequestState.MenuRequest.GetMenu();
            }


            return _currentState.GetMenu(s);
        }

        public MenuView HandleInput(string input)
        {
            return _currentState.HandleInput(input, this);
        }
    }

    public class MenuContextRequest<T> : MenuContext
    {
        public bool error = false;
        public bool done = false;
        public MenuContextRequest(IMenuState initialState)
            : base(initialState)
        {
        }

        public T? GetAnswer()
        {
            if (!error && done && _currentState is IMenuStateWithParam<T, T> stateWithParam) return stateWithParam.Param;
            return default;
        }
    }

}
