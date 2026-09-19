"""
Cliente del servicio de pagos con tarjeta webcheckout (repositorio ``payments``).

La API se autentica con dos encabezados: ``Authorization: Token <token>`` y
``X-Business-Id: <uuid>``. Solo acepta CRC y USD.
"""
import logging
from decimal import Decimal, ROUND_HALF_UP

import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)

SUPPORTED_CURRENCIES = ('CRC', 'USD')
FALLBACK_CURRENCY = 'USD'
CENTS = Decimal('0.01')


class WebCheckoutError(Exception):
    """El servicio de pagos no respondió o respondió con un error."""


def _session():
    session = requests.Session()
    session.headers.update({
        'Authorization': 'Token %s' % settings.WEBCHECKOUT_API_TOKEN,
        'X-Business-Id': settings.WEBCHECKOUT_BUSINESS_ID,
    })
    return session


def _request(method, path, expected=(200,), **kwargs):
    url = settings.WEBCHECKOUT_BASE_URL + path
    try:
        response = _session().request(method, url, timeout=settings.WEBCHECKOUT_TIMEOUT, **kwargs)
    except requests.RequestException as exc:
        logger.warning("Error de conexión con webcheckout %s %s: %s", method, url, exc)
        raise WebCheckoutError(str(exc)) from exc
    if response.status_code not in expected:
        logger.warning("webcheckout %s %s respondió %s: %s", method, url,
                       response.status_code, response.text[:500])
        raise WebCheckoutError("HTTP %s" % response.status_code)
    return response.json()


def site_url(name, *args):
    return settings.SITE_BASE_URL + reverse(name, args=args)


def charge_amount(bill):
    """Monto y moneda a cobrar: CRC y USD tal cual, las demás monedas se pasan a USD."""
    currency = bill.currency.currency
    amount = Decimal(bill.amount)
    if currency not in SUPPORTED_CURRENCIES:
        amount = amount / Decimal(bill.currency.rates)
        currency = FALLBACK_CURRENCY
    return amount.quantize(CENTS, rounding=ROUND_HALF_UP), currency


def _product_payload(course):
    return {
        'name': course.name[:255],
        'short_description': str(course.category)[:500],
        'active': True,
    }


def ensure_course_product(course):
    """Devuelve el id del producto del curso en el servicio, creándolo si no existe."""
    if course.gateway_product_id:
        return course.gateway_product_id
    data = _request('post', '/api/v1/products/', expected=(201,), json=_product_payload(course))
    course.gateway_product_id = data['id']
    course.save(update_fields=['gateway_product_id'])
    return course.gateway_product_id


def sync_course_product(course):
    """Crea el producto del curso o actualiza su nombre en el servicio."""
    if not course.gateway_product_id:
        return ensure_course_product(course)
    _request('patch', '/api/v1/products/%s/' % course.gateway_product_id,
             json=_product_payload(course))
    return course.gateway_product_id


def create_order(bill):
    """Crea la orden de pago de la factura y devuelve la respuesta del servicio."""
    amount, currency = charge_amount(bill)
    user = bill.student.user
    payload = {
        'product_id': str(ensure_course_product(bill.enrollment.group.course)),
        'price': str(amount),
        'currency': currency,
        'language': 'es',
        'notification_url': site_url('card_payment_webhook'),
        'redirect_url': site_url('card_payment_return', bill.pk),
        'buyer_name': user.first_name[:100],
        'buyer_surname': user.last_name[:100],
        'buyer_email': user.email,
        'buyer_phone': (bill.student.phone_number or '')[:30],
    }
    return _request('post', '/api/v1/orders/', expected=(201,),
                    json={key: value for key, value in payload.items() if value})


def get_order(order_id):
    return _request('get', '/api/v1/orders/%s/' % order_id)
