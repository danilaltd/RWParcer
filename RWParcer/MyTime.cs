using System;
using System.Globalization;

namespace RWParcer
{
    public class MyTime
    {
        public static string NormalizeTime(string time)
        {
            return System.Text.RegularExpressions.Regex.Replace(time, "[^0-9]", ":");
        }
        public static bool IsSameTime(string time1, string time2)
        {
            var formats = new[] { "H:m", "HH:mm", "H:mm", "HH:m" };

            foreach (var format in formats)
            {
                if (DateTime.TryParseExact(NormalizeTime(time1), format, CultureInfo.InvariantCulture, DateTimeStyles.None, out var dt1) &&
                    DateTime.TryParseExact(NormalizeTime(time2), format, CultureInfo.InvariantCulture, DateTimeStyles.None, out var dt2))
                {
                    if (dt1 == dt2)
                        return true;
                }
            }
            return false;
        }
    }
}
