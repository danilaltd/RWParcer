import os

PROXY_MANAGER_PORT = int(os.environ.get("PROXY_MANAGER_PORT", "8080"))
PROXY_MANAGER_HEALTH_CHECK_INTERVAL = int(os.environ.get("PROXY_MANAGER_HEALTH_CHECK_INTERVAL", "30"))
COLLECTOR_RUN_HOUR = int(os.environ.get("COLLECTOR_RUN_HOUR", "1"))

MIN_HEALTHY_SCORE = 40
FAILED_COOLDOWN_SECONDS = 30
TCP_CHECK_TIMEOUT_SECONDS = 5.0
FORWARD_TIMEOUT_SECONDS = 15.0

PROXY_DB_PATH = os.environ.get("PROXY_DB_PATH", "proxies.db")
TEST_URL = os.environ.get("TEST_URL", "http://ifconfig.me")
CHECKS_ON_TEST_URL = int(os.environ.get("CHECKS_ON_TEST_URL", "2"))
CHECKS_ON_TEST_URL_SUCCESSED_NEED = int(os.environ.get("CHECKS_ON_TEST_URL_SUCCESSED_NEED", "1"))
CHECKS_ON_RW = int(os.environ.get("CHECKS_ON_RW", "3"))
CHECKS_ON_RW_SUCCESSED_NEED = int(os.environ.get("CHECKS_ON_RW_SUCCESSED_NEED", "1"))
CHECK_TIMEOUT_SECONDS = float(os.environ.get("CHECK_TIMEOUT_SECONDS", "10"))
MAX_CONCURRENCY = int(os.environ.get("MAX_CONCURRENCY", "1500"))
RUN_EVERY_HOURS = int(os.environ.get("RUN_EVERY_HOURS", "-1"))
SOURCE_URLS = [
    ("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"                 , "UNKNOWN"),
    ("https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"       , "UNKNOWN"),
    ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt"                , "HTTP"   ),
    ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt"               , "HTTP"   ),
    ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks4.txt"              , "SOCKS4" ),
    ("https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt"              , "SOCKS5" ),
    ("https://raw.githubusercontent.com/zloi-user/hideip.me/master/http.txt"                      , "HTTP"   ),
    ("https://raw.githubusercontent.com/zloi-user/hideip.me/master/https.txt"                     , "HTTP"   ),
    ("https://raw.githubusercontent.com/zloi-user/hideip.me/master/socks4.txt"                    , "SOCKS4" ),
    ("https://raw.githubusercontent.com/zloi-user/hideip.me/master/socks5.txt"                    , "SOCKS5" ),
    ("https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/http.txt"             , "HTTP"   ),
    ("https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks4.txt"           , "SOCKS4" ),
    ("https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt"           , "SOCKS5" ),
    ("https://raw.githubusercontent.com/dpangestuw/Free-Proxy/master/http_proxies.txt"            , "HTTP"   ),
    ("https://raw.githubusercontent.com/dpangestuw/Free-Proxy/master/socks4_proxies.txt"          , "SOCKS4" ),
    ("https://raw.githubusercontent.com/dpangestuw/Free-Proxy/master/socks5_proxies.txt"          , "SOCKS5" ),
    ("https://raw.githubusercontent.com/iplocate/free-proxy-list/master/all-proxies.txt"          , "UNKNOWN"),
    ("https://raw.githubusercontent.com/elliottophellia/proxylist/master/results/pmix_checked.txt", "UNKNOWN"),
]