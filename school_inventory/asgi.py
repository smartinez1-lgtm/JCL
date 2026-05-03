"""
ASGI config for the school_inventory project.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_inventory.settings")

application = get_asgi_application()
