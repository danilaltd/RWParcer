FROM python:3.11-slim

WORKDIR /app

COPY ./proxy-manager/app.py ./

RUN pip install --no-cache-dir "requests[socks]"

ENV PYTHONUNBUFFERED=1 \
    PROXY_MANAGER_PORT=8080

EXPOSE 8080

CMD ["python", "app.py"]
