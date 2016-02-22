"""
WSGI config for SoundMatching project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

# try to fix virtualenv path
activate_this = '/Users/acoustics/Documents/VirtualEnvs/DjangoVibrato/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SoundMatching.settings")
import django
django.setup()


application = get_wsgi_application()
