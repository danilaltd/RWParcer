FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

COPY ["RWParcerCore/RWParcerCore.csproj", "RWParcerCore/"]
COPY ["RWParcer/RWParcer.csproj", "RWParcer/"]
RUN dotnet restore "RWParcer/RWParcer.csproj"

COPY RWParcerCore/ RWParcerCore/
COPY RWParcer/ RWParcer/

RUN dotnet publish "RWParcer/RWParcer.csproj" -c Release -o /app/out

FROM mcr.microsoft.com/dotnet/runtime:9.0 AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    jq \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && wget -O psiphon https://github.com/Psiphon-Labs/psiphon-tunnel-core-binaries/raw/master/linux/psiphon-tunnel-core-x86_64 \
    && chmod +x psiphon \
    && if ! ./psiphon --version > /dev/null 2>&1; then \
        echo "Error with psiphon: coruupted or not start" && exit 1; \
    fi

COPY --from=build /app/out ./

COPY start.sh ./
RUN chmod +x start.sh

ENTRYPOINT ["./start.sh"]