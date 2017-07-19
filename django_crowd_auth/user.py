import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist


LOGGER = logging.getLogger(__name__)


def from_data(client, data):
    """Get a Django user from a Crowd user data.
    """
    username = data['name']
    is_active = getattr(settings, 'CROWD_USERS_ARE_ACTIVE', True)
    superusers_group = getattr(settings, 'CROWD_SUPERUSERS_GROUP', None)
    is_superuser = False
    groups = []

    for group_name in client.get_nested_groups(username):
        if superusers_group and group_name == superusers_group:
            is_superuser = True

        try:
            group = Group.objects.get(name=group_name)
        except ObjectDoesNotExist:
            group = Group.objects.create(name=group_name)
            LOGGER.info('Group %s created', group_name)

        groups.append(group)

    is_staff = getattr(settings, 'CROWD_USERS_ARE_STAFF', is_superuser)

    try:
        user = get_user_model().objects.get(username=username)

    except ObjectDoesNotExist:
        user = get_user_model().objects.create(
            username=username,
            first_name=data.get('first-name'),
            last_name=data.get('last-name'),
            email=data.get('email'),
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser)
        LOGGER.info('User %s created', username)

    else:
        user_changed = False

        if is_superuser != user.is_superuser:
            LOGGER.info('User %s is_superuser attribute changed from %s to %s',
                        username, user.is_superuser, is_superuser)
            user.is_superuser = is_superuser
            user_changed = True

        if is_staff != user.is_staff:
            LOGGER.info('User %s is_staff attribute changed from %s to %s',
                        username, user.is_staff, is_staff)
            user.is_staff = is_staff
            user_changed = True

        if is_active != user.is_active:
            LOGGER.info('User %s is_active attribute changed from %s to %s',
                        username, user.is_active, is_active)
            user.is_active = is_active
            user_changed = True

        if user_changed:
            user.save()

    django_groups = set(user.groups.values_list('name', flat=True))
    crowd_groups = set(group.name for group in groups)

    if django_groups != crowd_groups:
        LOGGER.info('User groups updated from %r to %r',
                    list(django_groups), list(crowd_groups))
        user.groups.set(groups)

    return user
