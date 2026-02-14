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
    procps curl \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /app/out ./

ENTRYPOINT ["dotnet", "RWParcer.dll"]