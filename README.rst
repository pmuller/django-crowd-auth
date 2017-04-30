django-crowd-auth
=================


This package includes a authentication backend and an authentication
middleware to integrate Django's authentication system with Atlassian Crowd.

When authenticating an user against Crowd,
its nested groups are retrieved and mirrored in Django.


Usage
-----

* To authenticate users against Crowd,
  add ``django_crowd_auth.backends.Backend`` to ``AUTHENTICATION_BACKENDS``.
* To enable single-sign-on,
  add ``django_crowd_auth.middleware.sso`` to ``MIDDLEWARE``.
  Ensure you also have
  ``django.contrib.sessions.middleware.SessionMiddleware`` and
  ``django.contrib.auth.middleware.AuthenticationMiddleware`` placed before it.
* Ensure ``django.contrib.sessions`` is in ``INSTALLED_APPS``.
* Add settings (see below)


Middlewares
-----------

Often the SSL session does not terminates directly on the Django application,
but on an intermediate proxy.

This package also includes 3 middlewares that rewrites the user's
``REMOTE_ADDR`` using header set by these proxies:

* ``django_crowd_auth.middlewares.x_forwarded_for``:
  Override ``REMOTE_ADDR`` with the first ``X-Forwarded-For`` entry.
* ``django_crowd_auth.middlewares.x_real_ip``:
  Override ``REMOTE_ADDR`` with the ``X-Real-IP`` value.
* ``django_crowd_auth.middlewares.fake_remote_addr``:
  Override ``REMOTE_ADDR`` with the ``FAKE_REMOTE_ADDR`` settings value.


.. warning::

  Only use these middlewares when you *KNOW* what you're doing.
  Otherwise you could enable attackers to spoof their IP address.

.. note::

  As the SSO middleware needs ``REMOTE_ADDR``, these middlewares must be
  declared *BEFORE* the SSO middleware.


Settings
--------

* ``CROWD_CLIENT``: must be a dict with these keys:
  * ``crowd_url``: mandatory
  * ``app_name``: mandatory
  * ``app_pass``: mandatory
  * ``ssl_verify``: defaults to ``True``. Also accepts a path to a CA bundle.
  * ``timeout``: no timeout by default
  * ``client_cert``
* ``CROWD_USERS_ARE_ACTIVE``: Defaults to ``True``.
  If ``True``, set the ``is_active`` user model attribute to ``True`` when
  creating Django users.
* ``CROWD_USERS_ARE_STAFF``: Defaults to ``False``.
  If ``True``, set the ``is_staff`` user model attribute to ``True`` when
  creating Django users.
* ``CROWD_SUPERUSERS_GROUP``: If defined, set the ``is_superuser`` user model
  attribute to ``True`` when they belong to the chosen group. By side effect,
  these users also get the ``is_staff`` attribute set to ``True``.
* ``CROWD_SESSION_VALIDATION_INTERVAL``: Default to 300 seconds.
  The user's Crowd session is re-validated at this interval.


Example
+++++++

.. code-block:: python

    CROWD_CLIENT = {
        'crowd_url': 'https://crowd.foo.bar',
        'app_name': 'foo',
        'app_pass': 'bar',
        'ssl_verify': '/etc/pki/tls/certs/ca-bundle.crt',
        'timeout': 10,
    }
    CROWD_USERS_ARE_STAFF = True
    CROWD_SUPERUSERS_GROUP = 'administrators'
    AUTHENTICATION_BACKENDS = ['django_crowd_auth.backends.Backend']
    MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django_crowd_auth.middleware.sso',
    ]
