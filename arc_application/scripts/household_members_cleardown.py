import os

import django


def household_members_cleardown():
    from arc_application.models.arc import Arc

    Arc.objects.filter(app_type='Adult update').delete()


if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('PROJECT_SETTINGS'))

    django.setup()

    household_members_cleardown()
