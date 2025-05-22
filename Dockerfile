#FROM debian:bookworm-slim
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

COPY RWParcerCore/RWParcerCore.csproj RWParcerCore/
COPY RWParcer/RWParcer.csproj RWParcer/

RUN dotnet restore RWParcerCore/RWParcerCore.csproj \
    && dotnet restore RWParcer/RWParcer.csproj

COPY RWParcerCore/ RWParcerCore/
COPY RWParcer/ RWParcer/

RUN dotnet publish RWParcerCore/RWParcerCore.csproj -c Release -o /app/out
RUN dotnet publish RWParcer/RWParcer.csproj -c Release -o /app/out

FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y wget curl bash jq libjson-xs-perl net-tools procps \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y wget bash && rm -rf /var/lib/apt/lists/* \
    && wget -O psiphon https://github.com/Psiphon-Labs/psiphon-tunnel-core-binaries/raw/master/linux/psiphon-tunnel-core-x86_64 \
    && chmod +x psiphon


COPY --from=build /app/out ./

ENV ASPNETCORE_URLS=http://*:${PORT}
EXPOSE ${PORT}

COPY start.sh /app/start.sh

RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]