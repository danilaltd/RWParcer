FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Copy only the .csproj files for fast restore
COPY RWParcerCore/RWParcerCore.csproj RWParcerCore/
COPY RWParcer/RWParcer.csproj RWParcer/

# Restore dependencies
RUN dotnet restore RWParcerCore/RWParcerCore.csproj \
    && dotnet restore RWParcer/RWParcer.csproj

# Copy the rest of the source code and psiphon.config
COPY RWParcerCore/ RWParcerCore/
COPY RWParcer/ RWParcer/
#COPY psiphon.config ./

# Publish projects
RUN dotnet publish RWParcerCore/RWParcerCore.csproj -c Release -o /app/out
RUN dotnet publish RWParcer/RWParcer.csproj       -c Release -o /app/out

FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app

# Download Psiphon binary and make it executable
RUN apt-get update \
    && apt-get install -y wget \
    && wget -O psiphon https://github.com/Psiphon-Labs/psiphon-tunnel-core-binaries/raw/master/linux/psiphon-tunnel-core-x86_64 \
    && chmod +x psiphon

# Copy published output and configuration from build stage
COPY --from=build /app/out ./
#COPY --from=build /src/psiphon.config ./

# Expose default ASP.NET port
ENV ASPNETCORE_URLS=http://*:${PORT}
EXPOSE ${PORT}

# Create startup script that launches 20 Psiphon instances + .NET app\ nRUN << 'EOF' > start.sh
#!/usr/bin/env bash
set -e

# Define arrays of recommended ports
HTTP_PORTS=(8080 8081 8090 8091 8100 8101 8110 8111 8120 8121 8130 8131 8140 8141 8150 8151 8160 8161 8170 8171)
SOCKS_PORTS=(1080 1081 1090 1091 1100 1101 1110 1111 1120 1121 1130 1131 1140 1141 1150 1151 1160 1161 1170 1171)

# Loop to generate configs and start Psiphon
for i in "${!HTTP_PORTS[@]}"; do
  cat > psiphon-$i.conf <<CONFIG
{
  "LocalHttpProxyPort": ${HTTP_PORTS[$i]},
  "LocalSocksProxyPort": ${SOCKS_PORTS[$i]},
  "PropagationChannelId": "FFFFFFFFFFFFFFFF",
  "RemoteServerListDownloadFilename": "remote_server_list",
  "RemoteServerListSignaturePublicKey": "<your-public-key-here>",
  "RemoteServerListUrl": "https://s3.amazonaws.com//psiphon/web/mjr4-p23r-puwl/server_list_compressed",
  "SponsorId": "FFFFFFFFFFFFFFFF",
  "UseIndistinguishableTLS": true
}
CONFIG
  # Start instance in background
  ./psiphon --config psiphon-$i.conf &
done

# Finally, run the .NET application in foreground
exec dotnet RWParcer.dll
EOF

RUN chmod +x start.sh

ENTRYPOINT ["./start.sh"]
