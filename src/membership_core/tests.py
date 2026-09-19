import json

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from membership_core.models import Country, SystemCurrency


class CatalogSeedTestCase(TestCase):
    def test_initial_data(self):
        """La migración de datos carga todos los países y las monedas base."""
        self.assertGreater(Country.objects.count(), 200)
        self.assertTrue(Country.objects.filter(code='CR').exists())
        self.assertTrue(SystemCurrency.objects.filter(currency='USD').exists())

    def test_country_flag_url(self):
        self.assertIn('/flags/cr.svg', Country.objects.get(code='CR').flag)


class CurrencyCatalogAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('catalog', 'catalog@example.com', 'x')
        self.list_url = reverse('api-currency-list')

    def give_perms(self, *codenames):
        self.user.user_permissions.add(*Permission.objects.filter(
            content_type__app_label='membership_core', codename__in=codenames))
        self.client.force_login(self.user)

    def test_requires_login(self):
        self.assertEqual(self.client.get(self.list_url).status_code, 403)

    def test_requires_permission(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.list_url).status_code, 403)
        self.assertEqual(self.client.get(reverse('catalog_currency')).status_code, 302)

    def test_list(self):
        self.give_perms('view_systemcurrency')
        response = self.client.get(self.list_url, {'limit': 10, 'offset': 0})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['recordsTotal'], SystemCurrency.objects.count())
        self.assertIn('currency_display', data['data'][0])
        self.assertEqual(self.client.get(reverse('catalog_currency')).status_code, 200)

    def test_create_update_delete(self):
        self.give_perms('view_systemcurrency', 'add_systemcurrency',
                        'change_systemcurrency', 'delete_systemcurrency')
        response = self.client.post(self.list_url, json.dumps({'currency': 'EUR', 'rates': '0.92'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        pk = response.json()['id']
        detail_url = reverse('api-currency-detail', args=[pk])
        response = self.client.put(detail_url, json.dumps({'currency': 'EUR', 'rates': '0.95'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(SystemCurrency.objects.get(pk=pk).rates), '0.95')
        self.assertEqual(self.client.delete(detail_url).status_code, 204)
        self.assertFalse(SystemCurrency.objects.filter(pk=pk).exists())

    def test_currency_is_unique(self):
        self.give_perms('add_systemcurrency')
        response = self.client.post(self.list_url, json.dumps({'currency': 'USD', 'rates': '1'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)


class CountryCatalogAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('catalog', 'catalog@example.com', 'x')
        self.user.user_permissions.add(*Permission.objects.filter(
            content_type__app_label='membership_core', codename__in=['view_country', 'change_country']))
        self.client.force_login(self.user)

    def test_search(self):
        response = self.client.get(reverse('api-country-list'), {'search': 'Costa Rica', 'limit': 5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([c['code'] for c in response.json()['data']], ['CR'])

    def test_add_without_permission(self):
        response = self.client.post(reverse('api-country-list'),
                                    json.dumps({'name': 'Nuevo', 'code': 'ZZ'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_page(self):
        self.assertEqual(self.client.get(reverse('catalog_country')).status_code, 200)
