"""Servicio de pagos con tarjeta simulado para las historias."""
from unittest import mock

from django.urls import reverse

from matricula.contrib.bills.tests import FakeService


class LiveFakeService(FakeService):
    """
    Igual que el FakeService de las pruebas de bills, pero el ``checkout_url``
    vuelve directo al servidor en vivo y la orden queda en ``final_status``.
    Así el navegador recorre el flujo completo sin salir del sitio.
    """

    def __init__(self, live_server_url, final_status='COMPLETED'):
        super().__init__()
        self.live_server_url = live_server_url
        self.final_status = final_status

    def __call__(self, method, url, timeout=None, json=None):
        response = super().__call__(method, url, timeout=timeout, json=json)
        if method == 'post' and url.endswith('/api/v1/orders/'):
            order = self.orders[response.json.return_value['id']]
            bill_pk = json['redirect_url'].rstrip('/').split('/')[-3]
            order['checkout_url'] = self.live_server_url + reverse('card_payment_return', args=[bill_pk])
            # Lo que responde la creación es una copia en PENDING, como el servicio real;
            # el pago "ocurre" después y la consulta posterior ve el estado final.
            response.json.return_value = dict(order)
            self.set_status(order['id'], self.final_status, 'AUTH-0001')
        return response


def patch_card_service(test_case, final_status='COMPLETED'):
    service = LiveFakeService(test_case.live_server_url, final_status)
    patcher = mock.patch('requests.Session.request', side_effect=service)
    patcher.start()
    test_case.addCleanup(patcher.stop)
    return service
