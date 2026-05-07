from typing import Any

from backend.app.db.config import MongoSettings

_client: Any | None = None


def get_mongo_client(settings: MongoSettings | None = None) -> Any:
    """Return a lazily-created PyMongo client."""
    global _client

    if _client is not None:
        return _client

    resolved_settings = settings or MongoSettings.from_env()
    uri = resolved_settings.require_uri()

    from pymongo import MongoClient

    _client = MongoClient(
        uri,
        connectTimeoutMS=resolved_settings.connect_timeout_ms,
        serverSelectionTimeoutMS=resolved_settings.server_selection_timeout_ms,
    )
    return _client


def get_mongo_database(settings: MongoSettings | None = None) -> Any:
    """Return the configured MongoDB database."""
    resolved_settings = settings or MongoSettings.from_env()
    return get_mongo_client(resolved_settings)[resolved_settings.database_name]


def close_mongo_client() -> None:
    """Close the cached MongoDB client if it was created."""
    global _client

    if _client is not None:
        _client.close()
        _client = None
