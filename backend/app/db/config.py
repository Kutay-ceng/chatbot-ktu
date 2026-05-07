import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_MONGODB_DB = "chatbot_ktu"
DEFAULT_TIMEOUT_MS = 5000


class MongoConfigError(RuntimeError):
    """Raised when MongoDB configuration is missing or invalid."""


@dataclass(frozen=True)
class MongoSettings:
    uri: str | None
    database_name: str = DEFAULT_MONGODB_DB
    connect_timeout_ms: int = DEFAULT_TIMEOUT_MS
    server_selection_timeout_ms: int = DEFAULT_TIMEOUT_MS

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "MongoSettings":
        source = os.environ if environ is None else environ
        return cls(
            uri=_clean(source.get("MONGODB_URI")),
            database_name=_clean(source.get("MONGODB_DB")) or DEFAULT_MONGODB_DB,
            connect_timeout_ms=_read_positive_int(
                source,
                "MONGODB_CONNECT_TIMEOUT_MS",
                DEFAULT_TIMEOUT_MS,
            ),
            server_selection_timeout_ms=_read_positive_int(
                source,
                "MONGODB_SERVER_SELECTION_TIMEOUT_MS",
                DEFAULT_TIMEOUT_MS,
            ),
        )

    def require_uri(self) -> str:
        if not self.uri:
            raise MongoConfigError("MONGODB_URI is required to connect to MongoDB.")
        return self.uri


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned_value = value.strip()
    return cleaned_value or None


def _read_positive_int(
    environ: Mapping[str, str],
    key: str,
    default: int,
) -> int:
    value = _clean(environ.get(key))
    if value is None:
        return default

    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise MongoConfigError(f"{key} must be a positive integer.") from exc

    if parsed_value <= 0:
        raise MongoConfigError(f"{key} must be a positive integer.")
    return parsed_value
