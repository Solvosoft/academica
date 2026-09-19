import json
import uuid
from datetime import timedelta
from decimal import Decimal
from unittest import mock

import requests
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now

from djgentelella.async_notification.models import EmailNotification

from matricula.contrib.bills.models import Bill, CardPayment
from matricula.contrib.bills.webcheckout import charge_amount
from matricula.models import Category, Course, Enroll, Group, Period, Student
from matricula.tasks import poll_card_payments, remove_invoices
from membership_core.models import Country, SystemCurrency

WEBCHECKOUT = dict(
    WEBCHECKOUT_BASE_URL='https://pagos.test',
    WEBCHECKOUT_API_TOKEN='api-token',
    WEBCHECKOUT_BUSINESS_ID='11111111-1111-1111-1111-111111111111',
    WEBCHECKOUT_NOTIFICATION_TOKEN='s3cret',
    CARD_PAYMENTS_ENABLED=True,
    SITE_BASE_URL='https://academica.test',
    CELERY_TASK_ALWAYS_EAGER=True,
)
PRODUCT_ID = '22222222-2222-2222-2222-222222222222'


def fake_response(status_code, data):
    response = mock.Mock(status_code=status_code, text=json.dumps(data))
    response.json.return_value = data
    return response


class FakeService:
    """Simula la API de webcheckout sobre ``requests.Session.request``."""

    def __init__(self):
        self.calls = []
        self.orders = {}

    def __call__(self, method, url, timeout=None, json=None):
        self.calls.append((method, url, json))
        path = url.replace(WEBCHECKOUT['WEBCHECKOUT_BASE_URL'], '')
        if method == 'post' and path == '/api/v1/products/':
            return fake_response(201, {'id': PRODUCT_ID, **json})
        if method == 'post' and path == '/api/v1/orders/':
            order_id = str(uuid.uuid4())
            self.orders[order_id] = {'id': order_id, 'status': 'PENDING', 'authorization_code': '',
                                     'checkout_url': 'https://pagos.test/p/%s/' % order_id, **json}
            return fake_response(201, self.orders[order_id])
        if method == 'get' and path.startswith('/api/v1/orders/'):
            return fake_response(200, self.orders[path.split('/')[4]])
        return fake_response(404, {})

    def set_status(self, order_id, status, authorization_code=''):
        self.orders[str(order_id)].update(status=status, authorization_code=authorization_code)

    def count(self, method, path):
        return len([c for c in self.calls if c[0] == method and c[1].endswith(path)])


@override_settings(**WEBCHECKOUT)
class CardPaymentTestCase(TestCase):
    def setUp(self):
        self.service = FakeService()
        patcher = mock.patch('requests.Session.request', side_effect=self.service)
        patcher.start()
        self.addCleanup(patcher.stop)

        category = Category.objects.create(name='Programación', description='x')
        self.course = Course.objects.create(category=category, name='Python básico', content='x')
        period = Period.objects.create(name='p1', start_date=now(), finish_date=now())
        self.group = Group.objects.create(
            period=period, course=self.course, name='g1', schedule='x', pre_enroll_start=now(),
            pre_enroll_finish=now(), enroll_start=now(), enroll_finish=now(), cost=10000,
            maximum=20, is_open=True, flow=0, currency=SystemCurrency.objects.get(currency='CRC'))
        self.user = User.objects.create_user('est', 'est@example.com', 'x',
                                             first_name='Ana', last_name='Mora')
        student = Student.objects.create(
            user=self.user, organization='UCR', country=Country.objects.get(code='CR'),
            city='SJ', phone_number='88888888', expired_at=now())
        # Al finalizar la matrícula la señal create_bill genera la factura.
        self.enroll = Enroll.objects.create(group=self.group, student=student, enroll_finished=True)
        self.bill = Bill.objects.get(enrollment=self.enroll)
        self.client.force_login(self.user)

    def pay(self):
        return self.client.post(reverse('pay_with_card', args=[self.bill.pk]))

    def notify(self, card_payment, status='COMPLETED', token='s3cret'):
        headers = {'HTTP_AUTHORIZATION': 'Token %s' % token} if token else {}
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(
                reverse('card_payment_webhook'),
                data={'order_id': str(card_payment.order_id), 'status': status,
                      'product_hash': 'x', 'status_reason': ''},
                content_type='application/json', **headers)

    # --- montos -------------------------------------------------------------
    def test_charge_amount_supported_currency(self):
        self.assertEqual(charge_amount(self.bill), (Decimal('10000.00'), 'CRC'))

    def test_charge_amount_other_currency_to_usd(self):
        eur = SystemCurrency.objects.create(currency='EUR', rates=Decimal('0.80'))
        self.bill.currency = eur
        self.bill.amount = Decimal('100')
        self.assertEqual(charge_amount(self.bill), (Decimal('125.00'), 'USD'))

    # --- inicio del pago ----------------------------------------------------
    def test_pay_creates_product_and_order(self):
        response = self.pay()
        card_payment = CardPayment.objects.get(bill=self.bill)
        self.assertRedirects(response, card_payment.checkout_url, fetch_redirect_response=False)
        self.course.refresh_from_db()
        self.assertEqual(str(self.course.gateway_product_id), PRODUCT_ID)
        payload = self.service.calls[-1][2]
        self.assertEqual(payload['product_id'], PRODUCT_ID)
        self.assertEqual((payload['price'], payload['currency']), ('10000.00', 'CRC'))
        self.assertEqual(payload['notification_url'], 'https://academica.test/bills/card/webhook/')
        self.assertEqual(payload['redirect_url'],
                         'https://academica.test/bills/%d/card/return/' % self.bill.pk)
        self.assertEqual(payload['buyer_email'], 'est@example.com')

    def test_pay_reuses_open_order_and_product(self):
        self.pay()
        self.pay()
        self.assertEqual(CardPayment.objects.count(), 1)
        self.assertEqual(self.service.count('post', '/api/v1/orders/'), 1)
        CardPayment.objects.update(status=CardPayment.Status.EXPIRED)
        self.pay()
        self.assertEqual(CardPayment.objects.count(), 2)
        self.assertEqual(self.service.count('post', '/api/v1/products/'), 1)

    def test_pay_other_student_bill(self):
        self.client.force_login(User.objects.create_user('otro', 'otro@example.com', 'x'))
        self.assertEqual(self.pay().status_code, 404)

    @override_settings(CARD_PAYMENTS_ENABLED=False)
    def test_pay_disabled(self):
        self.assertEqual(self.pay().status_code, 404)

    def test_pay_service_error(self):
        with mock.patch('requests.Session.request', side_effect=requests.ConnectionError):
            response = self.pay()
        self.assertRedirects(response, reverse('bills'), fetch_redirect_response=False)
        self.assertFalse(CardPayment.objects.exists())

    def test_bills_page_shows_card_option(self):
        response = self.client.get(reverse('bills'))
        self.assertContains(response, reverse('pay_with_card', args=[self.bill.pk]))
        self.assertContains(response, '10000,00 CRC')

    # --- webhook ------------------------------------------------------------
    def test_webhook_requires_token(self):
        self.pay()
        card_payment = CardPayment.objects.get()
        self.assertEqual(self.notify(card_payment, token=None).status_code, 401)
        self.assertEqual(self.notify(card_payment, token='mal').status_code, 401)

    def test_webhook_unknown_order(self):
        missing = CardPayment(order_id=uuid.uuid4())
        self.assertEqual(self.notify(missing).status_code, 404)

    def test_webhook_does_not_trust_payload(self):
        """Un COMPLETED en el cuerpo no basta: manda el estado que devuelve la API."""
        self.pay()
        card_payment = CardPayment.objects.get()
        self.assertEqual(self.notify(card_payment, 'COMPLETED').status_code, 200)
        self.bill.refresh_from_db()
        self.assertFalse(self.bill.is_paid)

    def test_webhook_completed_marks_bill_paid_once(self):
        self.pay()
        card_payment = CardPayment.objects.get()
        self.service.set_status(card_payment.order_id, 'COMPLETED', 'AUTH123')
        self.notify(card_payment)
        self.notify(card_payment)
        self.bill.refresh_from_db()
        card_payment.refresh_from_db()
        self.assertTrue(self.bill.is_paid)
        self.assertIn('AUTH123', self.bill.transaction_id)
        self.assertEqual(card_payment.status, CardPayment.Status.COMPLETED)
        self.assertEqual(EmailNotification.objects.filter(recipients=['est@example.com'],
                                                          subject__icontains='pago').count(), 1)

    def test_terminal_status_is_final(self):
        self.pay()
        card_payment = CardPayment.objects.get()
        self.service.set_status(card_payment.order_id, 'COMPLETED')
        self.notify(card_payment)
        self.service.set_status(card_payment.order_id, 'IN_PROCESS')
        self.notify(card_payment)
        card_payment.refresh_from_db()
        self.assertEqual(card_payment.status, CardPayment.Status.COMPLETED)

    # --- retorno y respaldo -------------------------------------------------
    def test_return_refreshes_status(self):
        self.pay()
        card_payment = CardPayment.objects.get()
        self.service.set_status(card_payment.order_id, 'FAILED')
        response = self.client.get(reverse('card_payment_return', args=[self.bill.pk]))
        self.assertRedirects(response, reverse('bills'), fetch_redirect_response=False)
        card_payment.refresh_from_db()
        self.assertEqual(card_payment.status, CardPayment.Status.FAILED)

    def test_poll_only_open_orders(self):
        self.pay()
        card_payment = CardPayment.objects.get()
        CardPayment.objects.update(created_at=timezone.now() - timedelta(minutes=5))
        self.service.set_status(card_payment.order_id, 'COMPLETED')
        poll_card_payments()
        self.bill.refresh_from_db()
        self.assertTrue(self.bill.is_paid)
        gets = self.service.count('get', '/api/v1/orders/%s/' % card_payment.order_id)
        poll_card_payments()
        self.assertEqual(self.service.count('get', '/api/v1/orders/%s/' % card_payment.order_id), gets)

    def test_remove_invoices_keeps_card_payment_in_process(self):
        self.pay()
        CardPayment.objects.update(status=CardPayment.Status.IN_PROCESS)
        Bill.objects.update(created_at=timezone.now() - timedelta(days=1))
        remove_invoices()
        self.assertTrue(Bill.objects.filter(pk=self.bill.pk).exists())
