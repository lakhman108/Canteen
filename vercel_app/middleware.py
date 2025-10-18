import logging
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class ErrorLoggingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        logger.error(f"Unhandled exception in {request.path}: {str(exception)}", exc_info=True)
        logger.error(f"Request method: {request.method}")
        logger.error(f"Request user: {request.user}")
        logger.error(f"Request META: {request.META}")
        return None  # Let Django handle the exception normally