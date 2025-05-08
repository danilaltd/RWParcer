# Используем .NET SDK для сборки проекта
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /app

# Копируем .csproj и восстанавливаем зависимости
COPY RWParcerCore/RWParcerCore.csproj RWParcerCore/
COPY RWParcer/RWParcer.csproj RWParcer/
RUN dotnet restore RWParcerCore.csproj && dotnet restore RWParcer.csproj

# Копируем весь проект
COPY RWParcerCore/ RWParcerCore/
COPY RWParcer/ RWParcer/

# Компилируем проекты
RUN dotnet publish RWParcerCore.csproj -c Release -o /app/out
RUN dotnet publish RWParcer.csproj -c Release -o /app/out

# Используем легкий .NET runtime для запуска
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app
COPY --from=build /app/out .

# Render.com ожидает, что приложение слушает порт, указанный в переменной окружения PORT
EXPOSE 8080

# Запускаем приложение
ENTRYPOINT ["dotnet", "RWParcer.dll"]
