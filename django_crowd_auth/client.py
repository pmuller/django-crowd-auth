from django.conf import settings
import crowd


class Client(crowd.CrowdServer):
    """Crowd client.
    """

    cookie_config = None

    def init_cookie_config(self):
        """Get Crowd's cookie configuration.
        """
        url = self.rest_url + '/config/cookie.json'
        response = self._get(url)
        if response.ok:
            Client.cookie_config = self.cookie_config = response.json()
            assert 'domain' in self.cookie_config, \
                'Missing crowd cookie config property domain'
            assert 'name' in self.cookie_config, \
                'Missing crowd cookie config property name'
            assert 'secure' in self.cookie_config, \
                'Missing crowd cookie config property secure'

    @classmethod
    def from_settings(cls):
        """Return a Client from Django settings.
        """
        return cls(**settings.CROWD_CLIENT)
