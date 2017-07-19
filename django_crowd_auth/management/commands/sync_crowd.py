import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from django_crowd_auth.client import Client
from django_crowd_auth import user


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Synchronize Django's auth with Crowd.
    """

    help = 'Synchronize Django\'s authentication with Crowd'

    def add_arguments(self, parser):  # pylint: disable=no-self-use
        """Configure the argument parser.
        """
        parser.add_argument(
            '-D', '--debug', default=False, action='store_true')

    def handle(  # pylint: disable=unused-argument
            self, debug, *args, **kwargs):
        """Command entry point.
        """
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
        client = Client.from_settings()
        users = set()
        groups = {}

        for group_name, group_data in client.get_memberships().items():
            users.update(group_data['users'])

            try:
                group = Group.objects.get(name=group_name)
                LOGGER.debug('Group %s already exists', group_name)
            except Group.DoesNotExist:
                group = Group.objects.create(name=group_name)
                LOGGER.info('Group %s created', group_name)

            groups[group_name] = group

        for username in users:
            user.from_data(client, client.get_user(username))
