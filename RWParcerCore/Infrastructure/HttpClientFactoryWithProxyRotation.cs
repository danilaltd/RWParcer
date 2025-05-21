using System.Net;

namespace RWParcerCore.Infrastructure
{
    internal class HttpClientFactoryWithProxyRotation
    {
        private readonly List<string> _proxyList;
        private int _currentIndex = 0;
        private readonly Lock _lock = new();

        public HttpClientFactoryWithProxyRotation(IEnumerable<string> proxyList)
        {
            _proxyList = [.. proxyList];
        }

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

            HttpClient httpClient = new(handler, disposeHandler: true);
            //httpClient.DefaultRequestHeaders.Add("Cookie", "hg-client-security=2wYWCwYjyj7EbcjAw98T7DTE4GQ; hg-security=jSvnyAzRO13rHxzxDQofaNhudTzZhdMLWREbC5iPNPrQbWMqaYq3EQPi1vGNz_rCZZ5FJBk9B9T1V401kT7hxaNLwppBih0=");
            return httpClient;
        }

        private HttpClient CreateClientNoProxy()
        {
            HttpClient httpClient = new();
            //httpClient.DefaultRequestHeaders.Add("Cookie", "hg-client-security=2wYWCwYjyj7EbcjAw98T7DTE4GQ; hg-security=jSvnyAzRO13rHxzxDQofaNhudTzZhdMLWREbC5iPNPrQbWMqaYq3EQPi1vGNz_rCZZ5FJBk9B9T1V401kT7hxaNLwppBih0=");
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
