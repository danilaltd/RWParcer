#!/usr/bin/env bash
set -euo pipefail

# Define arrays for HTTP and SOCKS ports
HTTP_PORTS=(8090 8091 8092 8093 8094 8095 8096 8097 8098 8099 8100 8101 8102 8103 8104 8105 8106 8107 8108 8109)
SOCKS_PORTS=(1080 1081 1082 1083 1084 1085 1086 1087 1088 1089 1090 1091 1092 1093 1094 1095 1096 1097 1098 1099)
PSIPHON_BIN="./psiphon"

# Check if the Psiphon binary exists and is executable
if [[ ! -x "$PSIPHON_BIN" ]]; then
  echo "Не найден исполняемый файл $PSIPHON_BIN"
  exit 1
fi

# Step 1: Download the server list
curl -L -o server_list_compressed "https://s3.amazonaws.com//psiphon/web/mjr4-p23r-puwl/server_list_compressed"

# Step 2: Extract server tokens
gunzip -c server_list_compressed | jq -r '.servers[].data' > server_tokens.txt

# Step 3: Read tokens into an array
mapfile -t tokens < server_tokens.txt

# Check if there are enough unique tokens (at least 20)
if [ ${#tokens[@]} -lt 20 ]; then
  echo "Недостаточно серверных токенов: доступно только ${#tokens[@]}"
  exit 1
fi

# Step 4: Launch 20 Psiphon instances with unique servers
for (( i=0; i<20; i++ )); do
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
  "RemoteServerListSignaturePublicKey": "mykey",
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