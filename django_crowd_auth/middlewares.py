import logging
from time import time

from django_crowd_auth.client import Client
from django_crowd_auth.backends import Backend
from django.contrib.auth import login, logout
from django.conf import settings


LOGGER = logging.getLogger(__name__)


def sso(get_response):
    """Crowd SSO middleware.
    """

    def middleware(request):
        """Authenticate users having a Crowd cookie.
        """
        if Client.cookie_config is None:
            return get_response(request)

        cookie_config = Client.cookie_config

        crowd_session_last_validation = \
            request.session.get('crowd_session_last_validation')

        # Handle expired token validations
        if crowd_session_last_validation:
            crowd_session_validation_interval = getattr(
                settings, 'CROWD_SESSION_VALIDATION_INTERVAL', 300)
            crowd_session_expiry = \
                crowd_session_last_validation + \
                crowd_session_validation_interval

            if crowd_session_expiry <= time():
                LOGGER.debug(
                    'Crowd session validation expired, logging out %s',
                    request.user.username)
                logout(request)

        cookie_token = request.COOKIES.get(cookie_config.get('name'))

        if not request.user.is_authenticated and cookie_token:
            LOGGER.debug('Trying to auth from cookie %s', cookie_token)
            user = Backend().authenticate(request, token=cookie_token)

            if user:
                login(request, user, 'django_crowd_auth.backends.Backend')
                LOGGER.info('User %s logged in from Crowd session',
                            request.user.username)

        response = get_response(request)
        crowd_session_expiry = request.session.get('crowd_session_expiry')

        if request.user.is_authenticated and crowd_session_expiry and (
                cookie_token or 'crowd_session_token' in request.session):
            if not cookie_token:
                cookie_token = request.session['crowd_session_token']

            response.set_cookie(
                key=cookie_config.get('name'), value=cookie_token,
                max_age=None, expires=crowd_session_expiry, path='/',
                domain=cookie_config.get('domain'),
                secure=cookie_config.get('secure'), httponly=True)

        else:
            response.delete_cookie(
                key=cookie_config.get('name'), path='/',
                domain=cookie_config.get('domain'))

        return response

    return middleware


def x_forwarded_for(get_response):
    """Override ``REMOTE_ADDR`` with the first ``X-Forwarded-For`` entry.

    .. warning::

        Only use this if your are *sure* requests pass through a trusted
        proxy. Otherwise, clients will be able to spoof their source IP
        addresses by settings the header value themselves.

    """
    def middleware(request):
        """The middleware callable.
        """
        request.META['REMOTE_ADDR'] = \
            request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        return get_response(request)

    return middleware


def x_real_ip(get_response):
    """Override ``REMOTE_ADDR`` with the ``X-Real-IP`` value.

    .. warning::

        Only use this if your are *sure* requests pass through a trusted
        proxy. Otherwise, clients will be able to spoof their source IP
        addresses by settings the header value themselves.

    """
    def middleware(request):
        """The middleware callable.
        """
        request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
        return get_response(request)

    return middleware


def fake_remote_addr(get_response):
    """Override ``REMOTE_ADDR`` with the ``fake_remote_addr``.
    """
    def middleware(request):
        """The middleware callable.
        """
        request.META['REMOTE_ADDR'] = settings.FAKE_REMOTE_ADDR
        return get_response(request)

    return middleware
