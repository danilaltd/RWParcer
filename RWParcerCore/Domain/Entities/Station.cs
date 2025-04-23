namespace RWParcerCore.Domain.Entities
{
    internal struct Station
    {
        public string prefix;
        public string label;
        public string label_tail;
        public string value;
        public string exp;
        public string ecp;

        public Station(string pref, string labe, string labe_t, string val, string exp_, string ecp_)
        {
            prefix = pref;
            label = labe;
            label_tail = labe_t;
            value = val;
            exp = exp_;
            ecp = ecp_;

        }
    }
}
