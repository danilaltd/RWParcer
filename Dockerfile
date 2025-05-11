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
RUN printf '#!/usr/bin/env bash\n\
set -e\n\
\n\
HTTP_PORTS=(8080 8081 8090 8091 8100 8101 8110 8111 8120 8121 8130 8131 8140 8141 8150 8151 8160 8161 8170 8171)\n\
SOCKS_PORTS=(1080 1081 1090 1091 1100 1101 1110 1111 1120 1121 1130 1131 1140 1141 1150 1151 1160 1161 1170 1171)\n\
\n\
for i in \"${!HTTP_PORTS[@]}\"; do\n\
  cat > psiphon-$i.conf <<CONFIG\n\
{\n\
  \"LocalHttpProxyPort\": ${HTTP_PORTS[$i]},\n\
  \"LocalSocksProxyPort\": ${SOCKS_PORTS[$i]},\n\
  \"PropagationChannelId\": \"FFFFFFFFFFFFFFFF\",\n\
  \"RemoteServerListDownloadFilename\": \"remote_server_list\",\n\
  \"RemoteServerListSignaturePublicKey\": \"MIICIDANBgkqhkiG9w0BAQEFAAOCAg0AMIICCAKCAgEAt7Ls+/39r+T6zNW7GiVpJfzq/xvL9SBH5rIFnk0RXYEYavax3WS6HOD35eTAqn8AniOwiH+DOkvgSKF2caqk/y1dfq47Pdymtwzp9ikpB1C5OfAysXzBiwVJlCdajBKvBZDerV1cMvRzCKvKwRmvDmHgphQQ7WfXIGbRbmmk6opMBh3roE42KcotLFtqp0RRwLtcBRNtCdsrVsjiI1Lqz/lH+T61sGjSjQ3CHMuZYSQJZo/KrvzgQXpkaCTdbObxHqb6/+i1qaVOfEsvjoiyzTxJADvSytVtcTjijhPEV6XskJVHE1Zgl+7rATr/pDQkw6DPCNBS1+Y6fy7GstZALQXwEDN/qhQI9kWkHijT8ns+i1vGg00Mk/6J75arLhqcodWsdeG/M/moWgqQAnlZAGVtJI1OgeF5fsPpXu4kctOfuZlGjVZXQNW34aOzm8r8S0eVZitPlbhcPiR4gT/aSMz/wd8lZlzZYsje/Jr8u/YtlwjjreZrGRmG8KMOzukV3lLmMppXFMvl4bxv6YFEmIuTsOhbLTwFgh7KYNjodLj/LsqRVfwz31PgWQFTEPICV7GCvgVlPRxnofqKSjgTWI4mxDhBpVcATvaoBl1L/6WLbFvBsoAUBItWwctO2xalKxF5szhGm8lccoc5MZr8kfE0uxMgsxz4er68iCID+rsCAQM=\",\n\
  \"RemoteServerListUrl\": \"https://s3.amazonaws.com//psiphon/web/mjr4-p23r-puwl/server_list_compressed\",\n\
  \"SponsorId\": \"FFFFFFFFFFFFFFFF\",\n\
  \"UseIndistinguishableTLS\": true\n\
}\n\
CONFIG\n\
  ./psiphon --config psiphon-$i.conf &\n\
done\n\
\n\
exec dotnet RWParcer.dll\n' > start.sh && chmod +x start.sh

RUN chmod +x start.sh

ENTRYPOINT ["./start.sh"]
