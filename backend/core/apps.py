from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self) -> None:
        from core import schema  # noqa: F401  (registers the OpenAPI extension)
