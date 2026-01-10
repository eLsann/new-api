"""
Test configuration and ensure all settings are properly defined.
"""
import pytest
from app.config import settings


def test_config_has_all_required_attributes():
    """Test that all required configuration attributes exist."""
    required_attrs = [
        # App
        "app_name",
        "env",
        # Database
        "database_url",
        # Security
        "secret_key",
        "admin_token_expire_hours",
        # Device tokens
        "device_tokens",
        # Face recognition
        "max_distance",
        "min_face_px",
        # Attendance/Cooldown
        "cooldown_seconds",
        # Snapshots
        "save_snapshots",
        "snapshot_dir",
        "snapshot_on_unknown",
        "snapshot_on_low_conf",
        "low_conf_distance",
    ]
    
    for attr in required_attrs:
        assert hasattr(settings, attr), f"Missing attribute: {attr}"
        value = getattr(settings, attr)
        assert value is not None, f"Attribute {attr} is None"


def test_config_types():
    """Test that config attributes have correct types."""
    assert isinstance(settings.app_name, str)
    assert isinstance(settings.env, str)
    assert isinstance(settings.database_url, str)
    assert isinstance(settings.secret_key, str)
    assert isinstance(settings.admin_token_expire_hours, int)
    assert isinstance(settings.device_tokens, str)
    assert isinstance(settings.max_distance, float)
    assert isinstance(settings.min_face_px, int)
    assert isinstance(settings.cooldown_seconds, int)
    assert isinstance(settings.save_snapshots, bool)
    assert isinstance(settings.snapshot_dir, str)
    assert isinstance(settings.snapshot_on_unknown, bool)
    assert isinstance(settings.snapshot_on_low_conf, bool)
    assert isinstance(settings.low_conf_distance, float)


def test_config_backwards_compatibility():
    """Test that uppercase property aliases work."""
    assert settings.DATABASE_URL == settings.database_url
    assert settings.SECRET_KEY == settings.secret_key
    assert settings.ADMIN_TOKEN_EXPIRE_HOURS == settings.admin_token_expire_hours
    assert settings.DEVICE_TOKENS == settings.device_tokens
    assert settings.MAX_DISTANCE == settings.max_distance
    assert settings.MIN_FACE_PX == settings.min_face_px
    assert settings.COOLDOWN_SECONDS == settings.cooldown_seconds
    assert settings.SAVE_SNAPSHOTS == settings.save_snapshots
    assert settings.SNAPSHOT_DIR == settings.snapshot_dir
    assert settings.SNAPSHOT_ON_UNKNOWN == settings.snapshot_on_unknown
    assert settings.SNAPSHOT_ON_LOW_CONF == settings.snapshot_on_low_conf
    assert settings.LOW_CONF_DISTANCE == settings.low_conf_distance


def test_config_secret_key_not_empty():
    """Test that SECRET_KEY is set and not empty."""
    assert settings.secret_key
    assert len(settings.secret_key) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
