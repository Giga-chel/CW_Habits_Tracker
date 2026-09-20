from drf_spectacular.extensions import OpenApiAuthenticationExtension


class SimpleJWTScheme(OpenApiAuthenticationExtension):
    """Схема Bearer-авторизации для SimpleJWT в Swagger UI."""

    target_class = "rest_framework_simplejwt.authentication.JWTAuthentication"
    name = "jwtAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
