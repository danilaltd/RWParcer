# 1️⃣ Используем .NET SDK для сборки проекта
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /app

# 2️⃣ Копируем только .csproj файлы для быстрого restore
COPY RWParcerCore/RWParcerCore.csproj RWParcerCore/
COPY RWParcer/RWParcer.csproj RWParcer/

# 3️⃣ Восстанавливаем зависимости (чтобы избежать перересчета слоев при изменениях в коде)
RUN dotnet restore RWParcerCore/RWParcerCore.csproj && dotnet restore RWParcer/RWParcer.csproj

# 4️⃣ Теперь копируем весь проект после restore
COPY RWParcerCore/ RWParcerCore/
COPY RWParcer/ RWParcer/

# 5️⃣ Компилируем проекты
RUN dotnet publish RWParcerCore/RWParcerCore.csproj -c Release -o /app/out
RUN dotnet publish RWParcer/RWParcer.csproj -c Release -o /app/out

# 6️⃣ Используем легкий .NET runtime для запуска
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app
COPY --from=build /app/out .

# 7️⃣ Render.com ожидает, что приложение слушает порт, указанный в переменной окружения PORT
EXPOSE 8080

# 8️⃣ Запускаем приложение
ENTRYPOINT ["dotnet", "RWParcer.dll"]
