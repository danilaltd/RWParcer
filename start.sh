#!/usr/bin/env bash
set -e

# Массивы портов для экземпляров Psiphon
HTTP_PORTS=(8080 8081 8090 8091 8100 8101 8110 8111 8120 8121 8130 8131 8140 8141 8150 8151 8160 8161 8170 8171)
SOCKS_PORTS=(1080 1081 1090 1091 1100 1101 1110 1111 1120 1121 1130 1131 1140 1141 1150 1151 1160 1161 1170 1171)

# Запуск нескольких экземпляров Psiphon
for (( i=0; i<20; i++ )); do
  cat > psiphon-$i.conf <<CONFIG
{
  "LocalHttpProxyPort": ${HTTP_PORTS[$i]},
  "LocalSocksProxyPort": ${SOCKS_PORTS[$i]},
  "PropagationChannelId": "FFFFFFFFFFFFFFFF",
  "RemoteServerListDownloadFilename": "remote_server_list",
  "RemoteServerListSignaturePublicKey": "mykey",
  "RemoteServerListUrl": "https://s3.amazonaws.com//psiphon/web/mjr4-p23r-puwl/server_list_compressed",
  "SponsorId": "FFFFFFFFFFFFFFFF",
  "UseIndistinguishableTLS": true
}
CONFIG

  ./psiphon --config psiphon-$i.conf &
done

# Пауза для запуска Psiphon (опционально, можно настроить)
sleep 10

# Запуск .NET приложения
exec dotnet RWParcer.dll