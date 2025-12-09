"""
WSGI config for MAIN project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MAIN.settings")

application = get_wsgi_application()

#chdir = os.path.dirname(os.path.abspath(__file__))
#env = r"C:\\Users\\AULA-1\\Documents\\GitHub\\pievdcs\\virtual_env\\Scripts\\activate"