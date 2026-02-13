import importlib

import pytest
from django.urls import clear_url_caches, reverse

import config.urls

SCHEMA_URL = reverse("schema")

EXPECTED_PATHS = [
    "/api/v1/auth/register/",
    "/api/v1/auth/login/",
    "/api/v1/auth/logout/",
    "/api/v1/auth/token/refresh/",
    "/api/v1/auth/email/verify/",
    "/api/v1/auth/email/resend/",
    "/api/v1/auth/password/change/",
    "/api/v1/auth/password/reset/",
    "/api/v1/auth/password/reset/confirm/",
    "/api/v1/users/me/profile-image/",
]

ALLOW_ANY_PATHS = [
    "/api/v1/auth/register/",
    "/api/v1/auth/login/",
    "/api/v1/auth/logout/",
    "/api/v1/auth/token/refresh/",
    "/api/v1/auth/email/verify/",
    "/api/v1/auth/email/resend/",
    "/api/v1/auth/password/reset/",
    "/api/v1/auth/password/reset/confirm/",
]

AUTHENTICATED_PATHS = [
    "/api/v1/auth/password/change/",
    "/api/v1/users/me/profile-image/",
]


@pytest.fixture
def schema(api_client):
    response = api_client.get(SCHEMA_URL, HTTP_ACCEPT="application/json")
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def _debug_urls(settings):
    settings.DEBUG = True
    importlib.reload(config.urls)
    clear_url_caches()
    yield
    settings.DEBUG = False
    importlib.reload(config.urls)
    clear_url_caches()


class TestSchemaEndpoint:
    def test_schema_returns_200(self, api_client):
        response = api_client.get(SCHEMA_URL)
        assert response.status_code == 200

    def test_schema_contains_api_info(self, schema):
        assert schema["info"]["title"] == "TaskFlow Auth API"
        assert schema["info"]["version"] == "1.0.0"

    def test_schema_contains_all_paths(self, schema):
        paths = schema["paths"]
        for path in EXPECTED_PATHS:
            assert path in paths, f"{path} not found in schema paths"

    def test_schema_has_auth_tag(self, schema):
        tag_names = [t["name"] for t in schema["tags"]]
        assert "auth" in tag_names

    def test_schema_has_users_tag(self, schema):
        tag_names = [t["name"] for t in schema["tags"]]
        assert "users" in tag_names

    def test_schema_has_jwt_security_scheme(self, schema):
        security_schemes = schema["components"]["securitySchemes"]
        assert "jwtAuth" in security_schemes
        jwt = security_schemes["jwtAuth"]
        assert jwt["type"] == "http"
        assert jwt["scheme"] == "bearer"
        assert jwt["bearerFormat"] == "JWT"


class TestSchemaSecurityConfig:
    def test_allow_any_views_do_not_require_auth(self, schema):
        for path in ALLOW_ANY_PATHS:
            operations = schema["paths"][path]
            for method, operation in operations.items():
                if method in ("get", "post", "put", "patch", "delete"):
                    security = operation.get("security")
                    assert security is None or security == [], (
                        f"{method.upper()} {path} should not require auth"
                    )

    def test_authenticated_views_require_jwt(self, schema):
        for path in AUTHENTICATED_PATHS:
            operations = schema["paths"][path]
            for method, operation in operations.items():
                if method in ("get", "post", "put", "patch", "delete"):
                    security = operation.get("security")
                    assert security is not None and any(
                        "jwtAuth" in s for s in security
                    ), f"{method.upper()} {path} should require JWT auth"


@pytest.mark.usefixtures("_debug_urls")
class TestDocumentationViews:
    def test_swagger_ui_returns_200(self, api_client):
        url = reverse("swagger-ui")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_redoc_returns_200(self, api_client):
        url = reverse("redoc")
        response = api_client.get(url)
        assert response.status_code == 200
