# drf-middleware
Middleware support for django-rest-framework request response

It is an xtension of APIView to support middlewares in rest-framework. Use this as the base class of your view will allow you to use middleware in
`django-rest-framework`.

## When to use this?

  When you need DRF parsed request and response in your middleware because
  they are not available in Django Middleware.

  We will have access to `request.user` after authentication and also `request.data` after DRF parses it.


## Writing a middleware
```python
from drf_middleware import DRFMiddleware

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
```

## Django setting

First you need to monkey patch DRF's API view in `settings.py`

```python
from rest_framework import views
from drf_middleware import MiddlewareEnabledAPIView

# Monkey patch DRF's `APIView` to support middleware
views.APIView = MiddlewareEnabledAPIView
```

Then list your middleware in `DRF_MIDDLEWARE_CLASSES` in `settings.py`

```python
DRF_MIDDLEWARE_CLASSES = ["src.UserActivityMiddleware"]
```

