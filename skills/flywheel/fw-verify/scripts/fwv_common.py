"""Shared helpers for fw-verify scripts: config loading, API key resolution, run ids."""

import json
import os
import secrets
import typing as t
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CONFIG_PATH = CACHE_DIR / "config.json"
RUN_ID_PREFIX = "fwv-"

# Every way a user can misconfigure a script before it reaches the instance:
# missing config.json, unknown --site, unset key env var, malformed JSON. Shared
# so both entrypoints report them identically — they drifted once, and cleanup
# tracebacked on a malformed config while build_project printed a clean message.
SETUP_ERRORS = (KeyError, FileNotFoundError, RuntimeError, json.JSONDecodeError)


def get_error_message(exc: Exception) -> str:
    """Return an exception's message, unwrapping KeyError's repr quoting.

    Args:
        exc: The caught setup exception.

    Returns:
        str: the message, without the extra quotes KeyError's str() adds.
    """
    if isinstance(exc, KeyError) and exc.args:
        return str(exc.args[0])
    return str(exc)


@dataclass
class SiteConfig:
    """One site entry from cache/config.json."""

    api_key_env: str
    group: str
    label: str


def get_site_config(
    site: t.Optional[str] = None, config_path: Path = CONFIG_PATH
) -> SiteConfig:
    """Load a site's settings from the untracked skill config.

    The config is deliberately asymmetric: "default_site" is an inline anonymous
    object while "sites" holds the same shape keyed by name.

    Args:
        site: Named entry under "sites"; None selects "default_site".
        config_path: Path to config.json (overridable for tests).

    Returns:
        SiteConfig: the selected site's settings.

    Raises:
        FileNotFoundError: config.json is missing.
        KeyError: the named site is not present; the message lists the available names.
    """
    if not config_path.exists():
        raise FileNotFoundError(
            f"{config_path} not found. Copy assets/config.example.json to "
            f"cache/config.json and fill in your site details."
        )
    data = json.loads(config_path.read_text())
    if site is None:
        return SiteConfig(**data["default_site"])
    sites = data["sites"]
    if site not in sites:
        raise KeyError(
            f"Site {site!r} not found in config. Available sites: {sorted(sites)}"
        )
    return SiteConfig(**sites[site])


def get_api_key(cfg: SiteConfig) -> str:
    """Resolve the API key from the configured environment variable.

    Args:
        cfg: The site config naming the environment variable.

    Returns:
        str: the API key value.

    Raises:
        RuntimeError: the environment variable is unset or empty.
    """
    key = os.environ.get(cfg.api_key_env)
    if not key:
        raise RuntimeError(
            f"Environment variable {cfg.api_key_env} is not set. "
            f"Export it with the API key for site '{cfg.label}'."
        )
    return key


def get_run_id() -> str:
    """Generate a namespaced run id like fwv-0806-a3f2."""
    return f"{RUN_ID_PREFIX}{datetime.now():%m%d}-{secrets.token_hex(2)}"
