from drf_spectacular.extensions import OpenApiAuthenticationExtension


class StandInAuthenticationScheme(OpenApiAuthenticationExtension):
    """Documents the X-Demo-User header in the OpenAPI schema."""

    target_class = "core.identity.StandInAuthentication"
    name = "demoUser"

    def get_security_definition(self, auto_schema):
        return {"type": "apiKey", "in": "header", "name": "X-Demo-User"}
