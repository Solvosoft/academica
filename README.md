# Académica

Gestor de cursos, matrícula y facturación de cursos.

- Python 3.13, Django 6.0, [djgentelella](https://github.com/solvosoft/djgentelella) 0.6
- PostgreSQL (con la extensión `unaccent`), Redis como broker de Celery
- Correos con `djgentelella.async_notification` (plantillas editables desde el sitio)

Todos los comandos del proyecto están en el `Makefile`: `make help` los lista.

## Instalación con Docker (recomendada)

```bash
make env        # crea deploy/academica.env (y .env) desde env.example
make build      # construye la imagen academica:<versión>
make up         # postgres, redis, mailhog, web, celery y beat
make dsuperuser # crea el usuario administrador
```

- Sitio: http://localhost:8011
- MailHog (correos enviados): http://localhost:8026

Al arrancar, el contenedor web ejecuta `manage.py academica_install`, que es
idempotente: migraciones, tabla de caché, grupos de permisos y plantillas de
correo. Otros comandos útiles: `make logs`, `make ps`, `make dshell`,
`make dtest`, `make dmanage CMD="showmigrations"`, `make down`.

### Desarrollo dentro de Docker

```bash
make dev        # monta ./src y corre runserver + celery -B en http://localhost:8000
```

## Desarrollo local

```bash
make setup      # crea .venv con python3.13 e instala dependencias
make env        # crea .env desde env.example
make services   # postgres (5433), redis (6379) y mailhog (1026 / http://localhost:8026)
make install    # migraciones, caché, grupos y plantillas de correo
make superuser
make run        # http://127.0.0.1:8000
make celery     # en otra terminal: worker + beat
```

Pruebas: `make test` (o `make test TEST=matricula.tests.test_upgrade`).

## Imagen y roles de contenedor

La imagen elige el proceso con `SERVICE_TYPE`:

| SERVICE_TYPE | Proceso |
|---|---|
| `web` | gunicorn + nginx (supervisor) |
| `celery` | worker de Celery |
| `beat` | Celery beat (`django_celery_beat`) |
| `all` | web + worker + beat en un contenedor |
| `dev` | runserver + worker con beat embebido |

Con varias réplicas, solo una debe correr la instalación al arrancar; en las
demás se usa `ACADEMICA_BOOT_INSTALL=false`.

## Correos

Las plantillas viven en `EmailTemplate` (`djgentelella.async_notification`) y se
editan en `/async_notification/`. Su contenido inicial sale de los `.html` listados
en `matricula/utils.py:EMAIL_TEMPLATES`:

- `make load-templates` crea las que falten.
- `make load-templates OVERWRITE=1` las reemplaza con el contenido de los archivos.

Los correos con `enqueued=True` los envía la tarea `process_async_notifications`
cada 5 minutos (Celery beat), o a mano con `make send-emails`.

## Catálogos

Los países y las monedas (con su tipo de cambio respecto al dólar) se administran
en *Catálogos* (`/catalog/countries/`, `/catalog/currencies/`). La instalación
carga todos los países y las monedas USD y CRC. **El tipo de cambio de CRC hay que
ajustarlo en el catálogo.**

## Pago con tarjeta

En `/bills/`, además de PayPal, Sinpe Móvil y depósito, el estudiante puede pagar
con tarjeta a través del servicio de pagos webcheckout (repositorio `payments`,
que usa PlaceToPay/Evertec). La opción aparece cuando están configurados
`WEBCHECKOUT_API_TOKEN` y `WEBCHECKOUT_BUSINESS_ID`.

| Variable | Uso |
|---|---|
| `WEBCHECKOUT_BASE_URL` | URL del servicio de pagos |
| `WEBCHECKOUT_API_TOKEN` | Token de API del usuario del Business |
| `WEBCHECKOUT_BUSINESS_ID` | UUID del Business |
| `WEBCHECKOUT_NOTIFICATION_TOKEN` | Igual al `id_token` del Business; autentica las notificaciones |
| `SITE_BASE_URL` | URL pública de Académica; el servicio vuelve y notifica aquí |

Funcionamiento:

- Cada curso tiene un producto en el servicio. Se crea al primer pago, o con
  `make sync-products`, que además actualiza los nombres.
- Las facturas en CRC o USD se cobran en su moneda; las demás se convierten a USD
  con el catálogo de monedas.
- El estudiante paga en el checkout del servicio, donde también puede pedir la
  factura electrónica.
- Las notificaciones llegan a `/bills/card/webhook/`. Académica **no confía en el
  estado que trae la notificación**: vuelve a consultar la orden en la API antes de
  marcar la factura como pagada.
- La tarea `poll_card_payments` revisa cada 5 minutos las órdenes abiertas, por si
  una notificación no llega.
- En el admin (*Pagos con tarjeta*) se puede consultar el estado de una orden a mano.
