#!/usr/bin/env bash
set -euo pipefail

# Массивы портов для экземпляров Psiphon
HTTP_PORTS=(8090 8081)
SOCKS_PORTS=(1080 1081)

# Путь к бинарю psiphon (или psiphon-tunnel-core)
PSIPHON_BIN="./psiphon"

# Убедимся, что бинарь существует
if [[ ! -x "$PSIPHON_BIN" ]]; then
  echo "Не найден исполняемый файл $PSIPHON_BIN"
  exit 1
fi

# Запуск нескольких экземпляров Psiphon
for (( i=0; i<2; i++ )); do
  inst_dir="instance-$i"
  mkdir -p "$inst_dir"
  
  # Генерируем конфиг прямо в папке экземпляра
  cat > "$inst_dir/psiphon-$i.conf" <<CONFIG
{
  "LocalHttpProxyPort": ${HTTP_PORTS[$i]},
  "LocalSocksProxyPort": ${SOCKS_PORTS[$i]},
  "PropagationChannelId": "FFFFFFFFFFFFFFFF",
  "RemoteServerListDownloadFilename": "remote_server_list",
  "RemoteServerListSignaturePublicKey": "MIICIDANBgkqhkiG9w0BAQEFAAOCAg0AMIICCAKCAgEAt7Ls+/39r+T6zNW7GiVpJfzq/xvL9SBH5rIFnk0RXYEYavax3WS6HOD35eTAqn8AniOwiH+DOkvgSKF2caqk/y1dfq47Pdymtwzp9ikpB1C5OfAysXzBiwVJlCdajBKvBZDerV1cMvRzCKvKwRmvDmHgphQQ7WfXIGbRbmmk6opMBh3roE42KcotLFtqp0RRwLtcBRNtCdsrVsjiI1Lqz/lH+T61sGjSjQ3CHMuZYSQJZo/KrvzgQXpkaCTdbObxHqb6/+i1qaVOfEsvjoiyzTxJADvSytVtcTjijhPEV6XskJVHE1Zgl+7rATr/pDQkw6DPCNBS1+Y6fy7GstZALQXwEDN/qhQI9kWkHijT8ns+i1vGg00Mk/6J75arLhqcodWsdeG/M/moWgqQAnlZAGVtJI1OgeF5fsPpXu4kctOfuZlGjVZXQNW34aOzm8r8S0eVZitPlbhcPiR4gT/aSMz/wd8lZlzZYsje/Jr8u/YtlwjjreZrGRmG8KMOzukV3lLmMppXFMvl4bxv6YFEmIuTsOhbLTwFgh7KYNjodLj/LsqRVfwz31PgWQFTEPICV7GCvgVlPRxnofqKSjgTWI4mxDhBpVcATvaoBl1L/6WLbFvBsoAUBItWwctO2xalKxF5szhGm8lccoc5MZr8kfE0uxMgsxz4er68iCID+rsCAQM=",
  "RemoteServerListUrl": "https://s3.amazonaws.com//psiphon/web/mjr4-p23r-puwl/server_list_compressed",
  "SponsorId": "FFFFFFFFFFFFFFFF",
  "UseIndistinguishableTLS": true
}
CONFIG

  # Запуск из своей директории с перенаправлением логов
  (
    cd "$inst_dir"
    nohup "$PSIPHON_BIN" --config "psiphon-$i.conf" \
      &> "psiphon-$i.log" &
  )
  echo "Запущен Psiphon instance-$i: HTTP ${HTTP_PORTS[$i]}, SOCKS ${SOCKS_PORTS[$i]}"
done

# Дать Psiphon-ам пару секунд на инициализацию
sleep 5

# Запуск .NET приложения
exec dotnet RWParcer.dll
