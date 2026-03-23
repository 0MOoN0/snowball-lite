FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app:/app/apps/backend \
    TZ=Asia/Shanghai

RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

COPY apps/backend /app/apps/backend
COPY xalpha /app/xalpha

RUN mkdir -p /app/apps/backend/weblogs /app/apps/backend/web/data/lite_runtime

WORKDIR /app/apps/backend

EXPOSE 5001

CMD ["gunicorn", "-c", "web/gunicorn_lite.config.py", "web.lite_application:app"]
