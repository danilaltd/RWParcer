#!/usr/bin/env bash
set -eu

# Define arrays for HTTP and SOCKS ports
HTTP_PORTS=(8090 8091 8092 8093 8094 8095 8096 8097 8098 8099 8100 8101 8102 8103 8104 8105 8106 8107 8108 8109)
SOCKS_PORTS=(1080 1081 1082 1083 1084 1085 1086 1087 1088 1089 1090 1091 1092 1093 1094 1095 1096 1097 1098 1099)
PSIPHON_BIN="./psiphon"

# Check if the Psiphon binary exists and is executable
if [[ ! -x "$PSIPHON_BIN" ]]; then
  echo "Не найден исполняемый файл $PSIPHON_BIN"
  exit 1
fi

echo "Шаг 1: Загрузка списка серверов..."
curl -L -o server_list_compressed "https://s3.amazonaws.com//psiphon/web/mjr4-p23r-puwl/server_list_compressed"
ls -lh server_list_compressed

echo "Шаг 4: Извлечение токенов..."
printf "\x1f\x8b\x08\x00\x00\x00\x00\x00" | cat - server_list_compressed | gzip -dc 2>/dev/null | json_xs | grep '"data"' | awk -F\" '{print $4}' | sed "s@\\\n@\n\n\n\n@g" > server_tokens.txt
sed -i '/^$/d' server_tokens.txt


echo "Шаг 5: Проверяем токены..."
ls -lh server_tokens.txt
#cat server_tokens.txt
echo "Всего токенов: $(wc -l < server_tokens.txt)"

echo "✅ Все шаги выполнены!"
mapfile -t tokens < server_tokens.txt
printf "%s\n" "${tokens[@]}"



# Check if there are enough unique tokens (at least 20)
if [ ${#tokens[@]} -lt 10 ]; then
  echo "Недостаточно серверных токенов: доступно только ${#tokens[@]}"
  exit 1
fi

# Step 4: Launch 20 Psiphon instances with unique servers
for (( i=0; i<10; i++ )); do
  inst_dir="instance-$i"
  mkdir -p "$inst_dir"
  token=${tokens[$i]}

  # Create configuration file for this instance
  cat > "$inst_dir/psiphon-$i.conf" <<CONFIG
{
  "LocalHttpProxyPort": ${HTTP_PORTS[$i]},
  "LocalSocksProxyPort": ${SOCKS_PORTS[$i]},
  "PropagationChannelId": "FFFFFFFFFFFFFFFF",
  "RemoteServerListDownloadFilename": "remote_server_list",
  "RemoteServerListSignaturePublicKey": "MIICIDANBgkqhkiG9w0BAQEFAAOCAg0AMIICCAKCAgEAt7Ls+/39r+T6zNW7GiVpJfzq/xvL9SBH5rIFnk0RXYEYavax3WS6HOD35eTAqn8AniOwiH+DOkvgSKF2caqk/y1dfq47Pdymtwzp9ikpB1C5OfAysXzBiwVJlCdajBKvBZDerV1cMvRzCKvKwRmvDmHgphQQ7WfXIGbRbmmk6opMBh3roE42KcotLFtqp0RRwLtcBRNtCdsrVsjiI1Lqz/lH+T61sGjSjQ3CHMuZYSQJZo/KrvzgQXpkaCTdbObxHqb6/+i1qaVOfEsvjoiyzTxJADvSytVtcTjijhPEV6XskJVHE1Zgl+7rATr/pDQkw6DPCNBS1+Y6fy7GstZALQXwEDN/qhQI9kWkHijT8ns+i1vGg00Mk/6J75arLhqcodWsdeG/M/moWgqQAnlZAGVtJI1OgeF5fsPpXu4kctOfuZlGjVZXQNW34aOzm8r8S0eVZitPlbhcPiR4gT/aSMz/wd8lZlzZYsje/Jr8u/YtlwjjreZrGRmG8KMOzukV3lLmMppXFMvl4bxv6YFEmIuTsOhbLTwFgh7KYNjodLj/LsqRVfwz31PgWQFTEPICV7GCvgVlPRxnofqKSjgTWI4mxDhBpVcATvaoBl1L/6WLbFvBsoAUBItWwctO2xalKxF5szhGm8lccoc5MZr8kfE0uxMgsxz4er68iCID+rsCAQM=",
  "RemoteServerListUrl": "https://s3.amazonaws.com//psiphon/web/mjr4-p23r-puwl/server_list_compressed",
  "SponsorId": "FFFFFFFFFFFFFFFF",
  "UseIndistinguishableTLS": true,
  "TargetServerEntry": "$token"
}
CONFIG

  # Launch Psiphon instance in the background
  (
    cd "$inst_dir"
    nohup "../$PSIPHON_BIN" --config "psiphon-$i.conf" &
  )
  echo "Запущен Psiphon instance-$i: HTTP ${HTTP_PORTS[$i]}, SOCKS ${SOCKS_PORTS[$i]}, Server: $token"
done

# Wait for instances to initialize
sleep 5

# Run the dotnet application
#exec dotnet RWParcer.dll