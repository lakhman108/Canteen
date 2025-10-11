from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """Custom storage backend for static files"""
    location = settings.STATIC_LOCATION
    default_acl = 'public-read'
    file_overwrite = False


class MediaStorage(S3Boto3Storage):
    """Custom storage backend for media files"""
    location = settings.MEDIA_LOCATION
    default_acl = 'public-read'
    file_overwrite = False
