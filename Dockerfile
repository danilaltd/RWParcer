# 1️⃣ Use .NET SDK to build the project
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# 2️⃣ Copy only the .csproj files for fast restore
COPY RWParcerCore/RWParcerCore.csproj RWParcerCore/
COPY RWParcer/RWParcer.csproj RWParcer/

# 3️⃣ Restore dependencies
RUN dotnet restore RWParcerCore/RWParcerCore.csproj \
    && dotnet restore RWParcer/RWParcer.csproj

# 4️⃣ Copy the rest of the source code and psiphon.config
COPY RWParcerCore/ RWParcerCore/
COPY RWParcer/ RWParcer/
# Copy your Psiphon configuration file into the image
COPY psiphon.config ./

# 5️⃣ Publish projects
RUN dotnet publish RWParcerCore/RWParcerCore.csproj -c Release -o /app/out
RUN dotnet publish RWParcer/RWParcer.csproj       -c Release -o /app/out

# 6️⃣ Use lightweight .NET runtime image
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app

# 7️⃣ Download Psiphon binary and make it executable
RUN apt-get update \
    && apt-get install -y wget \
    && wget -O psiphon https://github.com/Psiphon-Labs/psiphon-tunnel-core-binaries/raw/master/linux/psiphon-tunnel-core-x86_64 \
    && chmod +x psiphon

# 8️⃣ Copy published output and configuration from build stage
COPY --from=build /app/out ./
COPY --from=build /src/psiphon.config ./

# 9️⃣ Expose port from environment variable and configure ASP.NET Core
ENV ASPNETCORE_URLS=http://*:${PORT}
EXPOSE ${PORT}

# 🔟 Create startup script to run Psiphon + app
RUN echo "#!/bin/bash\n" \
         "# Start Psiphon in background\n" \
         "./psiphon --config psiphon.config &\n" \
         "# Run the .NET application\n" \
         "exec dotnet RWParcer.dll" \
    > start.sh \
    && chmod +x start.sh

# 1️⃣1️⃣ Run startup script
ENTRYPOINT ["./start.sh"]
