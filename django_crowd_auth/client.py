from django.conf import settings
import crowd


class Client(crowd.CrowdServer):
    """Crowd client.
    """

    def get_cookie_config(self):
        """Get Crowd's cookie configuration.
        """
        url = self.rest_url + '/config/cookie.json'
        response = self._get(url)

        if response.ok:
            return response.json()

    @classmethod
    def from_settings(cls):
        """Return a Client from Django settings.
        """
        return cls(**settings.CROWD_CLIENT)
