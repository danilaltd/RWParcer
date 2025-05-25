namespace RWParcer.Models
{
    public class UserSession
    {
        public UserSession(CommandNames? currentCommand, bool initState, List<object>? data)
        {
            CurrentCommand = currentCommand;
            InitState = initState;
            Data = data ?? [];
        }
        public UserSession() { }
        public CommandNames? CurrentCommand { get; private set; }
        private bool _initState = true;
        public bool InitState
        {
            get
            {
                bool value = _initState;
                _initState = false;
                return value;
            }
            private set => _initState = value;
        }
        public List<object> Data { get; } = [];
        public DateOnly Date { get; set; } = DateOnly.FromDateTime(DateTime.Today);
        public void Reset()
        {
            CurrentCommand = null;
            Data.Clear();
        }
        public void SetCommand(CommandNames cmd)
        {
            CurrentCommand = cmd;
            InitState = true;
        }
    }
}