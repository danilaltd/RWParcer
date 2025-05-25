using RWParcerCore.Domain.ValueObjects;

namespace RWParcer.Converters
{
    public static class MessageVOToStringConverter
    {
        public static string Convert(MessageVO messageVO)
        {
            string time = messageVO.SentDate.AddHours(3).ToString();
            string from = $"from: {messageVO.SenderId}";
            string to = $"to: {messageVO.ReceiverId}";
            string content = messageVO.Content;
            return string.Join("\n", new[] { time, from, to, content }.Where(s => !string.IsNullOrEmpty(s)));
        }
    }
}
