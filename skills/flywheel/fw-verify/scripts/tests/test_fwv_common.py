import json
import re

import pytest

from fwv_common import SiteConfig, get_api_key, get_run_id, get_site_config


@pytest.fixture
def config_file(tmp_path):
    data = {
        "default_site": {"api_key_env": "FW_DEV_API", "group": "fw-verify", "label": "dev"},
        "sites": {"alt": {"api_key_env": "FW_ALT_API", "group": "fw-verify", "label": "alt"}},
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    return path


def test_get_site_config_default_returns_default_site(config_file):
    # Act
    cfg = get_site_config(config_path=config_file)

    # Assert
    assert cfg == SiteConfig(api_key_env="FW_DEV_API", group="fw-verify", label="dev")


def test_get_site_config_named_site_returns_that_entry(config_file):
    # Act
    cfg = get_site_config(site="alt", config_path=config_file)

    # Assert
    assert cfg.api_key_env == "FW_ALT_API"


def test_get_site_config_missing_file_raises_with_template_pointer(tmp_path):
    # Act & Assert
    with pytest.raises(FileNotFoundError, match="config.example.json"):
        get_site_config(config_path=tmp_path / "missing.json")


def test_get_site_config_unknown_site_raises_keyerror(config_file):
    # Act & Assert
    with pytest.raises(KeyError):
        get_site_config(site="nope", config_path=config_file)


def test_get_site_config_unknown_site_keyerror_lists_available_sites(config_file):
    # Act & Assert
    with pytest.raises(KeyError, match="Available sites.*alt"):
        get_site_config(site="nope", config_path=config_file)


def test_get_api_key_env_set_returns_value(monkeypatch):
    # Arrange
    monkeypatch.setenv("FW_DEV_API", "site.example.io:secret")
    cfg = SiteConfig(api_key_env="FW_DEV_API", group="g", label="dev")

    # Act & Assert
    assert get_api_key(cfg) == "site.example.io:secret"


def test_get_api_key_env_missing_raises_runtimeerror(monkeypatch):
    # Arrange
    monkeypatch.delenv("FW_DEV_API", raising=False)
    cfg = SiteConfig(api_key_env="FW_DEV_API", group="g", label="dev")

    # Act & Assert
    with pytest.raises(RuntimeError, match="FW_DEV_API"):
        get_api_key(cfg)


def test_get_run_id_matches_namespace_format():
    # Act
    run_id = get_run_id()

    # Assert
    assert re.fullmatch(r"fwv-\d{4}-[0-9a-f]{4}", run_id)
