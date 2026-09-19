"""
`/health/` es la sonda con la que la plataforma decide si el tenant está sano:
la usa el panel y el rollout del autodeploy, que se pausa si da algo distinto
de 200. Tiene que responder sin sesión y caer a 503 si falla una pieza.
"""
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse


class HealthTest(TestCase):
    def test_url_has_trailing_slash(self):
        # Sin barra, Django responde 301 y la sonda lo leería como no-sano.
        self.assertEqual(reverse("health"), "/health/")

    @mock.patch("academica.health._broker_ok", return_value=True)
    def test_healthy_without_session(self, _broker):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"database": "ok", "broker": "ok"})

    @mock.patch("academica.health._broker_ok", return_value=False)
    def test_broker_down_is_503(self, _broker):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["broker"], "error")

    @override_settings(CELERY_BROKER_URL="amqp://nadie:nada@127.0.0.1:1/vhost",
                       CELERY_TASK_ALWAYS_EAGER=False)
    def test_unreachable_broker_is_detected_not_raised(self):
        # Un broker inalcanzable no puede convertir la sonda en un 500: tiene
        # que decir cuál pieza falló.
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["broker"], "error")
