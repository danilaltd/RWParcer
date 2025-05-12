# Этап сборки: компиляция .NET приложения
FROM debian:bookworm-slim
#FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Копирование .csproj файлов для восстановления зависимостей
#COPY RWParcerCore/RWParcerCore.csproj RWParcerCore/
#COPY RWParcer/RWParcer.csproj RWParcer/

# Восстановление зависимостей
#RUN dotnet restore RWParcerCore/RWParcerCore.csproj \
#    && dotnet restore RWParcer/RWParcer.csproj

# Копирование остального исходного кода
#COPY RWParcerCore/ RWParcerCore/
#COPY RWParcer/ RWParcer/
#COPY psiphon.config ./

# Публикация проектов
#RUN dotnet publish RWParcerCore/RWParcerCore.csproj -c Release -o /app/out
#RUN dotnet publish RWParcer/RWParcer.csproj -c Release -o /app/out

# Этап выполнения: настройка окружения с .NET и Psiphon
#FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y wget curl bash jq libjson-xs-perl \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y wget bash && rm -rf /var/lib/apt/lists/* \
    && wget -O psiphon https://github.com/Psiphon-Labs/psiphon-tunnel-core-binaries/raw/master/linux/psiphon-tunnel-core-x86_64 \
    && chmod +x psiphon


# Копирование опубликованного .NET приложения
#COPY --from=build /app/out ./
#COPY --from=build /src/psiphon.config ./

ENV ASPNETCORE_URLS=http://*:${PORT}
EXPOSE ${PORT}

# Копирование локального скрипта start.sh в образ
COPY start.sh /app/start.sh

# Установка прав на выполнение для скрипта
RUN chmod +x /app/start.sh

# Указание точки входа для запуска скрипта
ENTRYPOINT ["/app/start.sh"]