using System.Net;

namespace RWParcerCore.Infrastructure
{
    internal class HttpClientFactoryWithProxyRotation(string? proxyManagerUrl = null)
    {
        private readonly string? _proxyManagerUrl = proxyManagerUrl;
        private readonly HttpClient _httpClient = new()
        {
            Timeout = TimeSpan.FromSeconds(10)
        };

        public async Task<HttpResponseMessage> GetAsyncNoProxy(string url)
        {
            return await _httpClient.GetAsync(url);
        }

        public async Task<HttpResponseMessage> GetAsyncWithProxy(string url)
        {
            if (!string.IsNullOrWhiteSpace(_proxyManagerUrl))
            {
                url = $"{_proxyManagerUrl.TrimEnd('/')}/proxy?url={Uri.EscapeDataString(url)}";
            }
            return await _httpClient.GetAsync(url);
        }
    }

}
