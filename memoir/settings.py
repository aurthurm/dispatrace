import os
from django.conf import settings

ATTACHMENT_UPLOAD_TO = getattr(settings, 'ATTACHMENT_UPLOAD_TO', 'uploads/attatchments')