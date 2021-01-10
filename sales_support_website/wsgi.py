"""
WSGI config for sales_support_website project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from elasticsearch_client import es as elasticsearch
from .setup import setup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sales_support_website.settings")

application = get_wsgi_application()

# Run elasticsearch index settings
elasticsearch.init()
elasticsearch.import_data()

# set up default group
setup()
