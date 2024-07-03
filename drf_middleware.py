from abc import ABC, abstractmethod

from django.utils.functional import SimpleLazyObject
from django.utils.module_loading import import_string

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response


def load_middleware_classes():
    # keeping it here to prevent circular import
    from django.conf import settings

    class_names = settings.DRF_MIDDLEWARE_CLASSES

    classes = []

    for class_name in class_names:
        classes.append(import_string(class_name))

    return classes


MIDDLEWARE_CLASSES = SimpleLazyObject(func=load_middleware_classes)


class DRFMiddleware(ABC):
    """Base middleware class for DRF

    Example::

        class UserActivityMiddleware(DRFMiddleware):
            def process_request(self, request):

                if request.user and request.user.is_authenticated():
                    logger.info(f"API request by user: {user.email} ")
                return request

            def process_response(self, request, response):
                if request.user and request.user.is_authenticated():
                    logger.info(
                        f"API request completed with status code {response.status_code}"
                        f"by user: {user.email}"
                    )
                return request

    """

    @abstractmethod
    def process_request(self, request: Request):
        """Process request before executing view"""
        return request

    @abstractmethod
    def process_response(self, request: Request, response: Response):
        """Process response after processing view"""
        return response


class MiddlewareEnabledAPIView(APIView):
    """Extension of APIView to support middlewares in rest-framework

    Using this as base class of your view will allow you to use middleware in
    `django-rest-framework`.

    When to use this ?

      When you need DRF parsed request and response in your middleware because
      they are not available in django middlewares.

    Usage:

        Monkey patch all view in your system by adding this in `settings.py`
        ::

            # ---------- patch for drf-middleware -----------------#

            from rest_framework import views
            from drf_middleware import MiddlewareEnabledAPIView

            # Monkey patch DRF's `APIView` to support middleware
            views.APIView = MiddlewareEnabledAPIView

            # now set middleware classes like
            DRF_MIDDLEWARE_CLASSES = ["src.UserActivityMiddleware"]

            # -------  end patch for drf-middleware ---------------#
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__middlewares: list[DRFMiddleware] | None = None

    def initial(self, request, *args, **kwargs):
        self.initialize_middlewares()
        super().initial(request, *args, **kwargs)
        self.middleware_process_request(request)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        return self.middleware_process_response(request, response)

    def initialize_middlewares(self):
        middleware_classes = MIDDLEWARE_CLASSES
        self.__middlewares = [
            MiddlewareClass() for MiddlewareClass in middleware_classes
        ]

    def middleware_process_request(self, request):
        if self.__middlewares:
            for middleware in self.__middlewares:
                middleware.process_request(request)

    def middleware_process_response(self, request, response):

        if self.__middlewares:
            for middleware in self.__middlewares[-1:]:
                response = middleware.process_response(request, response)
        return response
