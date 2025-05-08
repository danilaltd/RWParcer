# Используем .NET SDK для сборки проекта
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app

# Копируем .csproj и восстанавливаем зависимости
COPY RWParcer/RWParcer.csproj RWParcer/
WORKDIR /app/RWParcer
RUN dotnet restore RWParcer.csproj

# Копируем весь проект
COPY RWParcer/ .

# Компилируем проект
RUN dotnet publish RWParcer.csproj -c Release -o /app/out

WORKDIR /app

# Копируем .csproj и восстанавливаем зависимости
COPY RWParcerCore/RWParcerCore.csproj RWParcerCore/
WORKDIR /app/RWParcerCore
RUN dotnet restore RWParcerCore.csproj

# Копируем весь проект
COPY RWParcerCore/ .

# Компилируем проект
RUN dotnet publish RWParcerCore.csproj -c Release -o /app/out

# Используем легкий .NET runtime для запуска
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/out .

# Render.com ожидает, что приложение слушает порт, указанный в переменной окружения PORT
# EXPOSE не обязателен, так как Render.com использует PORT, но оставим для документации
EXPOSE 8080

# Запускаем приложение
CMD ["dotnet", "RWParcer.dll"]