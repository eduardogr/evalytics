import tornado
from tornado.options import define, options
import json


from server import App # isort:skip


class TestHelloApp(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        app = App()
        return app.create()
    
    def setUp(self):
        super().setUp()
        self._old_value = options.config

    def tearDown(self):
        options.config = self._old_value
        super().tearDown()

    def test_employees(self):
        # Given:
        options.config = "config.tests.yaml"

        # When:
        response = self.fetch(
            '/employees',
            method='GET',
            headers=None,

        )

        # Then:
        assert response.code == 200, print(f"Response: {response}")

        data = json.loads(response.body)
        assert data['success']
        assert len(data['response']['employees']) > 0

    def test_healthcheck(self):
        # When
        response = self.fetch(
            '/health',
            method='GET',
            headers=None,

        )

        # Then:
        assert response.code == 200, print(f"Response: {response}")

        # Assertion of body response content:
