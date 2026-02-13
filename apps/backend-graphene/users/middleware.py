import logging

from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed,
    InvalidToken,
    TokenError,
)

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware:
    """Middleware to authenticate requests via JWT Bearer token.

    Parses the Authorization header and sets request.user for both
    REST and GraphQL views.

    This middleware runs after Django's AuthenticationMiddleware. When a
    Bearer token is present in the Authorization header, it overrides the
    session-authenticated user (request.user) with the JWT-authenticated user.
    This is intentional: JWT takes precedence over session auth so that
    API clients can authenticate independently of browser sessions.
    If the token is invalid or expired, request.user is set to AnonymousUser.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if header.startswith("Bearer "):
            try:
                validated_token = self.jwt_auth.get_validated_token(
                    header.split(" ", 1)[1]
                )
                request.user = self.jwt_auth.get_user(validated_token)
            except (AuthenticationFailed, InvalidToken, TokenError):
                request.user = AnonymousUser()
            except Exception:
                logger.exception("Unexpected error in JWT middleware")
                request.user = AnonymousUser()
        return self.get_response(request)
