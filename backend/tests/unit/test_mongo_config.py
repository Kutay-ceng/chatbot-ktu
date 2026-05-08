import pytest

from backend.app.db.config import DEFAULT_MONGODB_DB, MongoConfigError, MongoSettings


def test_mongo_settings_from_env_uses_safe_defaults():
    settings = MongoSettings.from_env({})

    assert settings.uri is None
    assert settings.database_name == DEFAULT_MONGODB_DB
    assert settings.connect_timeout_ms == 5000
    assert settings.server_selection_timeout_ms == 5000


def test_mongo_settings_from_env_trims_values():
    settings = MongoSettings.from_env(
        {
            "MONGODB_URI": "  mongodb+srv://example  ",
            "MONGODB_DB": "  chatbot_test  ",
            "MONGODB_CONNECT_TIMEOUT_MS": " 1000 ",
            "MONGODB_SERVER_SELECTION_TIMEOUT_MS": " 2000 ",
        }
    )

    assert settings.uri == "mongodb+srv://example"
    assert settings.database_name == "chatbot_test"
    assert settings.connect_timeout_ms == 1000
    assert settings.server_selection_timeout_ms == 2000


def test_mongo_settings_require_uri_raises_when_missing():
    settings = MongoSettings.from_env({})

    with pytest.raises(MongoConfigError, match="MONGODB_URI"):
        settings.require_uri()


@pytest.mark.parametrize(
    "key",
    ["MONGODB_CONNECT_TIMEOUT_MS", "MONGODB_SERVER_SELECTION_TIMEOUT_MS"],
)
def test_mongo_settings_rejects_invalid_timeouts(key):
    with pytest.raises(MongoConfigError, match=key):
        MongoSettings.from_env({key: "0"})
