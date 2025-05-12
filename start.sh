#!/usr/bin/env bash
set -eu

# Количество инстансов, портов и сдвиг при перезапуске
NUM_INSTANCES=10
HTTP_PORTS=(8090 8091 8092 8093 8094 8095 8096 8097 8098 8099)
SOCKS_PORTS=(1080 1081 1082 1083 1084 1085 1086 1087 1088 1089)
PSIPHON_BIN="./psiphon"

# С какого токена начинать (можно менять в коде или задавать через env)
START_INDEX=${START_INDEX:-10}

# Загрузка и разбор списка токенов
load_tokens() {
  echo "Шаг 1: Загрузка списка серверов..."
  curl -sL -o server_list_compressed \
    "https://s3.amazonaws.com//psiphon/web/mjr4-p23r-puwl/server_list_compressed"
  
  echo "Шаг 2: Извлечение токенов..."
  printf "\x1f\x8b\x08\x00\x00\x00\x00\x00" | \
    cat - server_list_compressed | gzip -dc 2>/dev/null | \
    json_xs | grep '"data"' | awk -F\" '{print $4}' | \
    sed "s@\\\n@\n\n\n\n@g" > server_tokens.txt
  sed -i '/^$/d' server_tokens.txt
  
  TOKENS=( $(< server_tokens.txt) )
  TOTAL_TOKENS=${#TOKENS[@]}
  echo "Найдено токенов: $TOTAL_TOKENS"
  if (( TOTAL_TOKENS < NUM_INSTANCES )); then
    echo "Ошибка: токенов меньше, чем инстансов ($NUM_INSTANCES)"
    exit 1
  fi
}

# Остановка одного инстанса по номеру
stop_instance() {
  local i=$1
  pkill -f "psiphon-${i}\.conf" || true
  echo "Остановлен instance-$i (порты HTTP ${HTTP_PORTS[i]}, SOCKS ${SOCKS_PORTS[i]})"
}

# Запуск одного инстанса по номеру, с учётом текущего базового смещения
start_instance() {
  local i=$1
  local token_index=$(( (BASE_INDEX + i) % TOTAL_TOKENS ))
  local token="${TOKENS[token_index]}"
  local inst_dir="instance-${i}"
  mkdir -p "$inst_dir"

  cat > "$inst_dir/psiphon-${i}.conf" <<CONFIG
{
  "LocalHttpProxyPort": ${HTTP_PORTS[i]},
  "LocalSocksProxyPort": ${SOCKS_PORTS[i]},
  "PropagationChannelId": "FFFFFFFFFFFFFFFF",
  "RemoteServerListDownloadFilename": "remote_server_list",
  "RemoteServerListSignaturePublicKey": "MIICIDANBgkqhkiG9w0BAQEFAAOCAg0AMIICCAKCAgEAt7Ls+/39r+T6zNW7GiVpJfzq/xvL9SBH5rIFnk0RXYEYavax3WS6HOD35eTAqn8AniOwiH+DOkvgSKF2caqk/y1dfq47Pdymtwzp9ikpB1C5OfAysXzBiwVJlCdajBKvBZDerV1cMvRzCKvKwRmvDmHgphQQ7WfXIGbRbmmk6opMBh3roE42KcotLFtqp0RRwLtcBRNtCdsrVsjiI1Lqz/lH+T61sGjSjQ3CHMuZYSQJZo/KrvzgQXpkaCTdbObxHqb6/+i1qaVOfEsvjoiyzTxJADvSytVtcTjijhPEV6XskJVHE1Zgl+7rATr/pDQkw6DPCNBS1+Y6fy7GstZALQXwEDN/qhQI9kWkHijT8ns+i1vGg00Mk/6J75arLhqcodWsdeG/M/moWgqQAnlZAGVtJI1OgeF5fsPpXu4kctOfuZlGjVZXQNW34aOzm8r8S0eVZitPlbhcPiR4gT/aSMz/wd8lZlzZYsje/Jr8u/YtlwjjreZrGRmG8KMOzukV3lLmMppXFMvl4bxv6YFEmIuTsOhbLTwFgh7KYNjodLj/LsqRVfwz31PgWQFTEPICV7GCvgVlPRxnofqKSjgTWI4mxDhBpVcATvaoBl1L/6WLbFvBsoAUBItWwctO2xalKxF5szhGm8lccoc5MZr8kfE0uxMgsxz4er68iCID+rsCAQM=",
  "RemoteServerListUrl": "https://s3.amazonaws.com//psiphon/web/mjr4-p23r-puwl/server_list_compressed",
  "SponsorId": "FFFFFFFFFFFFFFFF",
  "UseIndistinguishableTLS": true,
  "TargetServerEntry": "$token"
}
CONFIG

  (
    cd "$inst_dir"
    nohup "../$PSIPHON_BIN" --config "psiphon-${i}.conf" &>/dev/null &
  )
  echo "Запущен instance-$i → токен #$token_index (HTTP ${HTTP_PORTS[i]}, SOCKS ${SOCKS_PORTS[i]})"
}

# Основной цикл перезапуска
psiphon_loop() {
  # Начальное базовое смещение
  BASE_INDEX=$START_INDEX

  trap 'echo "Получен SIGTERM, завершаю."; exit 0' TERM

  while true; do
    echo "=== Обход инстансов, BASE_INDEX=$BASE_INDEX ==="
    for (( i=0; i<NUM_INSTANCES; i++ )); do
      stop_instance "$i"
      start_instance "$i"
      # Небольшая пауза между перезапусками, чтобы не давить одновременно
      sleep 2
    done

    # После того как все инстансы подняты — сдвигаем базовый индекс
    BASE_INDEX=$(( (BASE_INDEX + NUM_INSTANCES) % TOTAL_TOKENS ))

    # Ждём перед следующим циклом (например, 60 минут)
    for (( m=60; m>0; m-- )); do
      echo "Ждём $m минут до следующего обновления..."
      sleep 60
    done
  done
}

# Точка входа
main() {
  if [[ ! -x "$PSIPHON_BIN" ]]; then
    echo "Не найден исполняемый файл $PSIPHON_BIN"
    exit 1
  fi

  load_tokens
  psiphon_loop &
  
  echo "Ожидаем, пока откроется последний HTTP-порт ${HTTP_PORTS[NUM_INSTANCES-1]}…"
  while ! netstat -tulnp | grep -q "${HTTP_PORTS[NUM_INSTANCES-1]}"; do
    sleep 2
  done
  sleep 3

  echo "✅ Все прокси подняты, запускаем .NET..."
  exec dotnet RWParcer.dll
}

main
