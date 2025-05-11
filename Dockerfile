# ✅ Use lightweight Debian base with bash and wget
FROM debian:bullseye-slim AS psiphon-test
WORKDIR /app

# 1️⃣ Install wget and bash
RUN apt-get update && apt-get install -y wget bash && rm -rf /var/lib/apt/lists/*

# 2️⃣ Download Psiphon binary
RUN wget -O psiphon https://github.com/Psiphon-Labs/psiphon-tunnel-core-binaries/raw/master/linux/psiphon-tunnel-core-x86_64 \
    && chmod +x psiphon

COPY start.sh .
RUN chmod +x start.sh
ENTRYPOINT ["./start.sh"]
