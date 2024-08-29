"""
WSGI config for tako project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tako.settings')

application = get_wsgi_application()

# from tako.start import start_tasks_scheduler


# start_tasks_scheduler()
