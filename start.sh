#!/usr/bin/env bash
set -eu

NUM_INSTANCES=10
HTTP_PORTS=(8090 8091 8092 8093 8094 8095 8096 8097 8098 8099)
SOCKS_PORTS=(1080 1081 1082 1083 1084 1085 1086 1087 1088 1089)
PSIPHON_BIN="./psiphon"
STATE_FILE="/app/data/index.state"

load_index() {
  if [[ -f "$STATE_FILE" ]]; then
    BASE_INDEX=$(cat "$STATE_FILE")
    
    if [[ -z "$BASE_INDEX" || ! "$BASE_INDEX" =~ ^[0-9]+$ ]]; then
      echo "ERROR: State file $STATE_FILE is corrupt or empty (value: '$BASE_INDEX')" >&2
      exit 1
    fi
    
    echo "Restored BASE_INDEX from file: $BASE_INDEX"
  else
    echo "ERROR: State file $STATE_FILE not found!" >&2
    echo "Check your docker-compose volumes or create the file manually." >&2
    exit 1
  fi
}

save_index() {
  echo "$BASE_INDEX" > "$STATE_FILE"
}

load_tokens() {
  echo "1. Psiphon servers loading..."
  if ! curl -sL -o server_list_compressed \
    "https://s3.amazonaws.com//psiphon/web/mjr4-p23r-puwl/server_list_compressed"; then
    echo "Error when load server_list_compressed"
    exit 1
  fi
  
  echo "2. Extract tokens..."
  printf "\x1f\x8b\x08\x00\x00\x00\x00\x00" | \
  cat - server_list_compressed | gzip -dc 2>/dev/null | \
  jq -r '.data' | sed 's/\\n/\n/g' > server_tokens.txt
  
  TOKENS=( $(< server_tokens.txt) )
  TOTAL_TOKENS=${#TOKENS[@]}
  echo "Tokens found: $TOTAL_TOKENS"
  if (( TOTAL_TOKENS < NUM_INSTANCES )); then
    echo "Error: not enoght tokens: ($TOTAL_TOKENS)<($NUM_INSTANCES)"
    exit 1
  fi
}

stop_instance() {
  local i=$1
  pkill -f "psiphon-${i}\.conf" || true
  echo "instance-$i stopped (ports: HTTP ${HTTP_PORTS[i]}, SOCKS ${SOCKS_PORTS[i]})"
}

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
  echo "instance-$i started - token #$token_index (HTTP ${HTTP_PORTS[i]}, SOCKS ${SOCKS_PORTS[i]})"
}

psiphon_loop() {
  load_index

  trap 'echo "got SIGTERM, psiphon_loop stops."; exit 0' TERM

  while true; do
    echo "Iterating on instances, BASE_INDEX=$BASE_INDEX"
    for (( i=0; i<NUM_INSTANCES; i++ )); do
      stop_instance "$i"
      start_instance "$i"
      sleep 2
    done

    BASE_INDEX=$(( (BASE_INDEX + NUM_INSTANCES) % TOTAL_TOKENS ))
    save_index

    for (( m=30; m>0; m-- )); do
      echo "Wait $m minutes untill psiphon restart..."
      sleep 60
    done
  done
}

main() {
  if [[ ! -x "$PSIPHON_BIN" ]]; then
    echo "Not found $PSIPHON_BIN"
    exit 1
  fi

  load_tokens
  psiphon_loop &
  
  echo "Wait untill the lastest port (${HTTP_PORTS[NUM_INSTANCES-1]}...)"
  while ! timeout 1 bash -c "cat < /dev/null > /dev/tcp/127.0.0.1/${HTTP_PORTS[NUM_INSTANCES-1]}" 2>/dev/null; do
    sleep 2
  done
  sleep 3

  echo "All proxies up. Good to start .NET"
  exec dotnet RWParcer.dll
}

main
