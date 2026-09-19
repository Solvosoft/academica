# ============ ETAPA 1: BUILDER ============
FROM python:3.13-trixie AS builder

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev libffi-dev gettext && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY locale /app/locale
WORKDIR /app/src
# Traducciones y estáticos se generan una sola vez al construir la imagen.
RUN python manage.py compilemessages -l es && \
    mkdir -p /run/static/ && \
    STATIC_ROOT=/run/static/ python manage.py collectstatic --noinput

# ============ ETAPA 2: RUNTIME ============
FROM python:3.13-slim-trixie

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV STATIC_ROOT=/run/static/
ENV MEDIA_ROOT=/app/media/

ARG UID=1000
ARG GID=1000
ENV USER="academica"

# librsvg2-bin: rsvg-convert genera los certificados (matricula/certificate_utils.py)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 \
    librsvg2-bin fontconfig shared-mime-info \
    nginx supervisor gettext curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid $GID $USER && \
    useradd --uid $UID --gid $GID --no-create-home $USER && \
    mkdir -p /run/logs/ /run/static/ /app/run/ /app/media/

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

RUN echo "daemon off;" >> /etc/nginx/nginx.conf && \
    sed -i "s/user www-data;/user $USER;/g" /etc/nginx/nginx.conf && \
    ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log && \
    sed -i 's/proxy_set_header X-Forwarded-Proto $scheme;/proxy_set_header X-Forwarded-Proto https;/g' /etc/nginx/proxy_params

COPY deploy/nginx.conf /etc/nginx/sites-available/default
COPY deploy/supervisor.conf /etc/supervisor/conf.d/academica.conf
COPY deploy/nginx_personalize.py /app/nginx_personalize.py
COPY --chmod=755 deploy/gunicorn_start /app/gunicorn_start
COPY --chmod=755 deploy/entrypoint.sh /run/entrypoint.sh

COPY --from=builder --chown=academica:academica /app/src /app/src
COPY --from=builder --chown=academica:academica /app/locale /app/locale
COPY --from=builder --chown=academica:academica /run/static/ /run/static/
RUN chown -R academica:academica /run/logs/ /app/run/ /app/media/

WORKDIR /app/src

EXPOSE 80 8000

CMD ["/run/entrypoint.sh"]
