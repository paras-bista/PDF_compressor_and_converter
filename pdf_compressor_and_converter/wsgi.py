# pdf_compressor_and_converter/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdf_compressor_and_converter.settings")
application = get_wsgi_application()
