#!/usr/bin/env bash
set -eu

if [[ -n "${NODE_ID_FROM_HOSTNAME:-}" ]]; then
  ID="${HOSTNAME##*_}"
else
  ID="${ID:-0}"
fi
HTTP_PORT="${HTTP_PORT:-8090}"
SOCKS_PORT="${SOCKS_PORT:-1080}"
FORWARD_PORT="${FORWARD_PORT:-8080}"
LOCALHOST="127.0.0.1"
PSIPHON_BIN="${PSIPHON_BIN:-./psiphon}"
STATE_FILE="${STATE_FILE:-/app/data/index.state}"
STATE_LOCK="${STATE_FILE}.lock"
LOG_DIR="${LOG_DIR:-/app/data/logs}"
SERVER_LIST_URL="${SERVER_LIST_URL:-https://s3.amazonaws.com//psiphon/web/mjr4-p23r-puwl/server_list_compressed}"
ROTATE_MINUTES="${ROTATE_MINUTES:-30}"

mkdir -p "$LOG_DIR"

TOKENS=()
TOTAL_TOKENS=0
SELECTED_INDEX=

load_index_with_inc() {
  if [[ ! -f "$STATE_FILE" ]]; then
    echo "ERROR: State file $STATE_FILE not found!" >&2
    echo "Create it with a number (e.g. '0') or mount correct volume." >&2
    exit 1
  fi

  exec 9>"$STATE_LOCK"
  flock -x 9

  local raw
  raw=$(cat "$STATE_FILE" 2>/dev/null || echo "")
  if [[ -z "$raw" || ! "$raw" =~ ^[0-9]+$ ]]; then
    echo "ERROR: State file $STATE_FILE is corrupt or empty (value: '$raw')" >&2
    flock -u 9
    exec 9>&-
    exit 1
  fi

  SELECTED_INDEX=$raw
  local next=$(( (SELECTED_INDEX + 1) % TOTAL_TOKENS ))
  echo "$next" > "$STATE_FILE"

  flock -u 9
  exec 9>&-
  echo "Selected index=$SELECTED_INDEX, next saved=$next"
}

load_tokens() {
  echo "1 Downloading server list..."
  tmpfile="server_list_compressed"
  if ! curl -sL -o "$tmpfile" "$SERVER_LIST_URL"; then
    echo "ERROR: failed to download server list" >&2
    rm -f "$tmpfile"
    exit 1
  fi

  echo "2 Extracting tokens..."

  printf "\x1f\x8b\x08\x00\x00\x00\x00\x00" | cat - "$tmpfile" | gzip -dc 2>/dev/null | jq -r '.data' | sed 's/\\n/\n/g' > /tmp/psiphon_tokens.txt

  rm -f "$tmpfile"

  TOKENS=( $(< /tmp/psiphon_tokens.txt) )
  TOTAL_TOKENS=${#TOKENS[@]}
  echo "Tokens found: $TOTAL_TOKENS"
  if (( TOTAL_TOKENS < 1 )); then
    echo "ERROR: no tokens extracted" >&2
    exit 1
  fi
}


start_instance() {
  local inst_id="${1:-$ID}"
  local token_index="$SELECTED_INDEX"
  local token="${TOKENS[$token_index]}"
  local inst_dir="instance-${inst_id}"
  mkdir -p "$inst_dir"
  mkdir -p "$LOG_DIR"
  local TS
  TS=$(date +%Y%m%d-%H%M%S)
  LOGFILE="$LOG_DIR/${TS}-psiphon-${token_index}-${inst_id}.log"

  cat > "$inst_dir/psiphon-${inst_id}.conf" <<CONFIG
{
  "LocalHttpProxyPort": ${HTTP_PORT},
  "LocalSocksProxyPort": ${SOCKS_PORT},
  "PropagationChannelId": "FFFFFFFFFFFFFFFF",
  "RemoteServerListDownloadFilename": "remote_server_list",
  "RemoteServerListSignaturePublicKey": "MIICIDANBgkqhkiG9w0BAQEFAAOCAg0AMIICCAKCAgEAt7Ls+/39r+T6zNW7GiVpJfzq/xvL9SBH5rIFnk0RXYEYavax3WS6HOD35eTAqn8AniOwiH+DOkvgSKF2caqk/y1dfq47Pdymtwzp9ikpB1C5OfAysXzBiwVJlCdajBKvBZDerV1cMvRzCKvKwRmvDmHgphQQ7WfXIGbRbmmk6opMBh3roE42KcotLFtqp0RRwLtcBRNtCdsrVsjiI1Lqz/lH+T61sGjSjQ3CHMuZYSQJZo/KrvzgQXpkaCTdbObxHqb6/+i1qaVOfEsvjoiyzTxJADvSytVtcTjijhPEV6XskJVHE1Zgl+7rATr/pDQkw6DPCNBS1+Y6fy7GstZALQXwEDN/qhQI9kWkHijT8ns+i1vGg00Mk/6J75arLhqcodWsdeG/M/moWgqQAnlZAGVtJI1OgeF5fsPpXu4kctOfuZlGjVZXQNW34aOzm8r8S0eVZitPlbhcPiR4gT/aSMz/wd8lZlzZYsje/Jr8u/YtlwjjreZrGRmG8KMOzukV3lLmMppXFMvl4bxv6YFEmIuTsOhbLTwFgh7KYNjodLj/LsqRVfwz31PgWQFTEPICV7GCvgVlPRxnofqKSjgTWI4mxDhBpVcATvaoBl1L/6WLbFvBsoAUBItWwctO2xalKxF5szhGm8lccoc5MZr8kfE0uxMgsxz4er68iCID+rsCAQM=",
  "RemoteServerListUrl": "${SERVER_LIST_URL}",
  "SponsorId": "FFFFFFFFFFFFFFFF",
  "UseIndistinguishableTLS": true,
  "TargetServerEntry": "${token}"
}
CONFIG

  

  cd "$inst_dir"
  touch "$LOGFILE"
  nohup "../$PSIPHON_BIN" --config "psiphon-${inst_id}.conf" >> "$LOGFILE" 2>&1 &

  PSIPHON_PID=$!
  touch "psiphon.pid"
  echo "$PSIPHON_PID" > "psiphon.pid" || true
  cd ..

  echo "Starting instance ${inst_id} with token #${token_index} (HTTP ${HTTP_PORT}, SOCKS ${SOCKS_PORT})"
  socat TCP4-LISTEN:${FORWARD_PORT},fork,reuseaddr TCP4:${LOCALHOST}:${HTTP_PORT} >> "$LOGFILE" 2>&1 &

  SOCAT_PID=$!

  echo "psiphon pid=${PSIPHON_PID}, socat pid=${SOCAT_PID}, logfile=${LOGFILE}"
}

stop_instance() {
  echo "Stopping psiphon and socat (if running)..."
  if [[ -n "${PSIPHON_PID:-}" ]]; then
    kill "${PSIPHON_PID}" 2>/dev/null || true
    wait "${PSIPHON_PID}" 2>/dev/null || true
  fi
  if [[ -n "${SOCAT_PID:-}" ]]; then
    kill "${SOCAT_PID}" 2>/dev/null || true
    wait "${SOCAT_PID}" 2>/dev/null || true
  fi
}

trap stop_instance EXIT

main() {
  if [[ ! -x "$PSIPHON_BIN" ]]; then
    echo "ERROR: not found or not executable: $PSIPHON_BIN" >&2
    exit 1
  fi

  load_tokens
  while true; do
    load_index_with_inc
    start_instance "$ID"

    for (( m=ROTATE_MINUTES; m>0; m-- )); do
        passed=$((ROTATE_MINUTES - m))
        if (( passed > 2 )); then
            if ! curl -s --max-time 5 -x ${LOCALHOST}:${FORWARD_PORT} https://ifconfig.me >/dev/null; then
                echo "Proxy check failed — next instance"
                echo "Proxy check failed — next instance" >> $LOGFILE
                break
            fi
        fi

      echo "$ID: Wait $m minute(s) until psiphon restart..." >> $LOGFILE
      sleep 60
    done

    stop_instance
    sleep 2
  done
}



main
