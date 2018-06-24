import logging
from time import time
from datetime import datetime

from django.conf import settings
from django.contrib.auth.backends import ModelBackend

from django_crowd_auth.client import Client
from django_crowd_auth import user
from requests.exceptions import ConnectionError


LOGGER = logging.getLogger(__name__)


class Backend(ModelBackend):
    """Django authentication backend for Atlassian Crowd.
    """

    def authenticate(self, request, **credentials):
        """Authenticate an user.
        """

        try:
            # Only try and init cookie config if it is None
            client = Client.from_settings()
            if client.cookie_config is None:
                client.init_cookie_config()

            remote_addr = request.META['REMOTE_ADDR']
            if 'token' in credentials:
                session = client.validate_session(
                    credentials['token'], remote_addr)
            elif 'username' in credentials and 'password' in credentials:
                session = client.get_session(
                    credentials['username'], credentials['password'],
                    remote_addr)
        except ConnectionError as ex:
            LOGGER.exception(ex)
            if getattr(settings, 'CROWD_RAISE_CONNECTION_ERROR', True):
                raise ex
            session = None

        if session:
            request.session['crowd_session_last_validation'] = time()
            request.session['crowd_session_expiry'] = \
                datetime.fromtimestamp(session['expiry-date'] / 1000).strftime(
                    '%a, %d-%b-%y %H:%M:%S GMT')

            if 'django_crowd_auth.middlewares.sso' in settings.MIDDLEWARE:
                # We do not want to store the token in the session because it
                # is too sensitive, but we still store it temporarily there to
                # make it accessible to the SSO middleware. It retrieve it to
                # set the Crowd cookie, then remote it.
                # XXX: Find a better way to pass the token to the SSO
                #      middleware.
                request.session['crowd_session_token'] = session['token']

            request.session.save()

            return user.from_data(client, session['user'])

        else:
            if 'crowd_session_last_validation' in request.session:
                del request.session['crowd_session_last_validation']

            if 'crowd_session_expiry' in request.session:
                del request.session['crowd_session_expiry']

            request.session.save()
