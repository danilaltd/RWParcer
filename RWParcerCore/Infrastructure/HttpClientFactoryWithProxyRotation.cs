using System.Net;

namespace RWParcerCore.Infrastructure
{
    internal class HttpClientFactoryWithProxyRotation(IEnumerable<string> proxyList)
    {
        private readonly List<string> _proxyList = [.. proxyList];
        private int _currentIndex = 0;
        private readonly Lock _lock = new();

        private HttpClient CreateClientWithProxy()
        {
            if (_proxyList.Count == 0) return CreateClientNoProxy();
            string proxyAddress;
            lock (_lock)
            {
                proxyAddress = _proxyList[_currentIndex];
                _currentIndex = (_currentIndex + 1) % _proxyList.Count;
            }

            var proxy = new WebProxy(proxyAddress);
            var handler = new HttpClientHandler
            {
                Proxy = proxy,
                UseProxy = true
            };

            HttpClient httpClient = new(handler, disposeHandler: true)
            {
                Timeout = TimeSpan.FromSeconds(10)
            };
            return httpClient;
        }

        private static HttpClient CreateClientNoProxy()
        {
            HttpClient httpClient = new()
            {
                Timeout = TimeSpan.FromSeconds(10)
            };
            return httpClient;
        }

        public async Task<HttpResponseMessage> GetAsyncNoProxy(string url)
        {
            var client = CreateClientNoProxy();
            return await client.GetAsync(url);
        }

        public async Task<HttpResponseMessage> GetAsyncWithProxy(string url)
        {
            var client = CreateClientWithProxy();
            return await client.GetAsync(url);
        }
    }

}
