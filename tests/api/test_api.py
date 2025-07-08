import tornado


from server import create_app # isort:skip


class TestHelloApp(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return create_app()

    def test_employees(self):
        # When
        response = self.fetch(
            '/employees',
            method='GET',
            headers=None,

        )

        # Then:
        assert response.code == 200, print(f"Response: {response}")

        # Assertion of body response content:
        data = response.json()
        assert len(data) > 0

    def test_surveys(self):
        # When
        response = self.fetch(
            '/surveys',
            method='GET',
            headers=None,

        )

        # Then:
        assert response.code == 200, print(f"Response: {response}")

        # Assertion of body response content:
        data = response.json()
        assert len(data) > 0

    def test_peers_get(self):
        # When
        response = self.fetch(
            '/peers',
            method='GET',
            headers=None,

        )

        # Then:
        assert response.code == 200, print(f"Response: {response}")

        # Assertion of body response content:
        data = response.json()
        assert len(data) > 0

    def test_peers_post(self):
        # When
        response = self.fetch(
            '/peers',
            method='POST',
            headers=None,

        )

        # Then:
        assert response.code == 200, print(f"Response: {response}")

        # Assertion of body response content:
        data = response.json()
        assert len(data) > 0

    def test_reviewers_get(self):
        # When
        response = self.fetch(
            '/reviewers',
            method='GET',
            headers=None,

        )

        # Then:
        assert response.code == 200, print(f"Response: {response}")

        # Assertion of body response content:
        data = response.json()
        assert len(data) > 0

    def test_status_get(self):
        # When
        response = self.fetch(
            '/status',
            method='GET',
            headers=None,

        )

        # Then:
        assert response.code == 200, print(f"Response: {response}")

        # Assertion of body response content:
        data = response.json()
        assert len(data) > 0

    def test_evalreports_get(self):
        # When
        response = self.fetch(
            '/evalreports',
            method='GET',
            headers=None,

        )

        # Then:
        assert response.code == 200, print(f"Response: {response}")

        # Assertion of body response content:
        data = response.json()
        assert len(data) > 0

    def test_evalreports_post(self):
        # When
        response = self.fetch(
            '/evalreports',
            method='POST',
            headers=None,

        )

        # Then:
        assert response.code == 200, print(f"Response: {response}")

        # Assertion of body response content:
        data = response.json()
        assert len(data) > 0

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
