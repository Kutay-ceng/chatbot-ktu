from typing import Any

from backend.app.db.config import MongoSettings

# PyMongo client tek kez oluşturulup cache'lenir.
# Her request'te yeni bağlantı açmak yerine aynı client yeniden kullanılır.
_client: Any | None = None


def get_mongo_client(settings: MongoSettings | None = None) -> Any:
    """İhtiyaç olduğunda oluşturulan PyMongo client'ını döndürür."""
    global _client

    if _client is not None:
        return _client

    resolved_settings = settings or MongoSettings.from_env()
    uri = resolved_settings.require_uri()

    # PyMongo importu fonksiyon içinde tutuldu.
    # Böylece MongoDB kullanılmayan test/akışlarda dependency hemen yüklenmek zorunda kalmaz.
    from pymongo import MongoClient

    _client = MongoClient(
        uri,
        connectTimeoutMS=resolved_settings.connect_timeout_ms,
        serverSelectionTimeoutMS=resolved_settings.server_selection_timeout_ms,
    )
    return _client


def get_mongo_database(settings: MongoSettings | None = None) -> Any:
    """Config'de belirtilen MongoDB database nesnesini döndürür."""
    resolved_settings = settings or MongoSettings.from_env()
    return get_mongo_client(resolved_settings)[resolved_settings.database_name]


def close_mongo_client() -> None:
    """Oluşturulmuş cache'li MongoDB client'ını kapatır."""
    global _client

    if _client is not None:
        _client.close()
        _client = None
