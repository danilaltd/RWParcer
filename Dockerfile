# 1️⃣ Используем .NET SDK для сборки проекта
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /app

# 2️⃣ Копируем только .csproj файлы для быстрого restore
COPY RWParcerCore/RWParcerCore.csproj RWParcerCore/
COPY RWParcer/RWParcer.csproj RWParcer/

# 3️⃣ Восстанавливаем зависимости
RUN dotnet restore RWParcerCore/RWParcerCore.csproj && dotnet restore RWParcer/RWParcer.csproj

# 4️⃣ Копируем весь проект
COPY RWParcerCore/ RWParcerCore/
COPY RWParcer/ RWParcer/

# 5️⃣ Компилируем проекты
RUN dotnet publish RWParcerCore/RWParcerCore.csproj -c Release -o /app/out
RUN dotnet publish RWParcer/RWParcer.csproj -c Release -o /app/out

# 6️⃣ Используем легкий .NET runtime для запуска
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app

# 7️⃣ Устанавливаем Psiphon (пример для Linux)
RUN apt-get update && apt-get install -y wget && \
    wget https://psiphon3.com/psiphon3.tar.gz && \
    tar -xzf psiphon3.tar.gz && \
    rm psiphon3.tar.gz

# 8️⃣ Копируем скомпилированные файлы из build
COPY --from=build /app/out .

# 9️⃣ Создаем скрипт для запуска Psiphon и приложения
RUN echo "#!/bin/bash\n./psiphon --config psiphon.config &\ndotnet RWParcer.dll" > start.sh && \
    chmod +x start.sh

# 10️⃣ Render.com ожидает порт из переменной окружения PORT
EXPOSE 8080

# 11️⃣ Запускаем скрипт
ENTRYPOINT ["./start.sh"]