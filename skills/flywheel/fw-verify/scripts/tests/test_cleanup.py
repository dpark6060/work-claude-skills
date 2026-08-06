import json
from unittest import mock

import pytest

from cleanup import delete_gears, delete_projects, main, validate_run_id
from fwv_common import SiteConfig, get_run_id


def _project(label):
    p = mock.MagicMock()
    p.label = label
    return p


def _gear(name):
    g = mock.MagicMock()
    g.gear.name = name
    return g


def test_validate_run_id_without_prefix_raises_valueerror():
    # Act & Assert
    with pytest.raises(ValueError, match="fwv-"):
        validate_run_id("prod-data")


def test_validate_run_id_with_prefix_passes():
    validate_run_id("fwv-0806-a3f2")


def test_validate_run_id_bare_prefix_raises_valueerror():
    # Act & Assert
    with pytest.raises(ValueError, match="fwv-"):
        validate_run_id("fwv-")


def test_validate_run_id_truncated_suffix_raises_valueerror():
    # Act & Assert
    with pytest.raises(ValueError, match="fwv-"):
        validate_run_id("fwv-0806")


def test_validate_run_id_accepts_generated_run_id():
    # Act & Assert
    validate_run_id(get_run_id())


def test_delete_projects_deletes_only_matching_labels():
    # Arrange
    fw = mock.MagicMock()
    keep = _project("some-real-project")
    kill = _project("fwv-0806-a3f2-exit-codes")
    fw.projects.iter_find.return_value = iter([keep, kill])

    # Act
    deleted = delete_projects(fw, "fw-verify", "fwv-0806-a3f2", dry_run=False)

    # Assert
    assert deleted == ["fwv-0806-a3f2-exit-codes"]
    fw.delete_project.assert_called_once_with(kill.id)


def test_delete_projects_dry_run_deletes_nothing():
    # Arrange
    fw = mock.MagicMock()
    fw.projects.iter_find.return_value = iter([_project("fwv-0806-a3f2-t")])

    # Act
    deleted = delete_projects(fw, "fw-verify", "fwv-0806-a3f2", dry_run=True)

    # Assert
    assert deleted == ["fwv-0806-a3f2-t"]
    fw.delete_project.assert_not_called()


def test_delete_gears_deletes_only_matching_names():
    # Arrange
    fw = mock.MagicMock()
    keep = _gear("file-curator")
    kill = _gear("fwv-0806-a3f2-probe")
    fw.gears.iter_find.return_value = iter([keep, kill])

    # Act
    deleted = delete_gears(fw, "fwv-0806-a3f2", dry_run=False)

    # Assert
    assert deleted == ["fwv-0806-a3f2-probe"]
    fw.delete_gear.assert_called_once_with(kill.id)


def test_delete_gears_dry_run_deletes_nothing():
    # Arrange
    fw = mock.MagicMock()
    fw.gears.iter_find.return_value = iter([_gear("fwv-0806-a3f2-probe")])

    # Act
    deleted = delete_gears(fw, "fwv-0806-a3f2", dry_run=True)

    # Assert
    assert deleted == ["fwv-0806-a3f2-probe"]
    fw.delete_gear.assert_not_called()


def test_delete_gears_asks_for_every_gear_version():
    # Arrange
    fw = mock.MagicMock()
    fw.gears.iter_find.return_value = iter([])

    # Act
    delete_gears(fw, "fwv-0806-a3f2", dry_run=False)

    # Assert
    fw.gears.iter_find.assert_called_once_with(all_versions=True)


@mock.patch("cleanup.flywheel.Client")
@mock.patch("cleanup.get_site_config")
def test_main_rejects_bad_run_id(mock_cfg, mock_client):
    # Act & Assert
    with pytest.raises(ValueError):
        main(["--run-id", "everything"])


@mock.patch("cleanup.flywheel.Client")
@mock.patch("cleanup.get_site_config")
def test_main_prints_deletion_summary_json(mock_cfg, mock_client, monkeypatch, capsys):
    # Arrange
    monkeypatch.setenv("FW_DEV_API", "site:key")
    mock_cfg.return_value = mock.MagicMock(api_key_env="FW_DEV_API", group="fw-verify")
    fw = mock_client.return_value
    fw.projects.iter_find.return_value = iter([])
    fw.gears.iter_find.return_value = iter([])

    # Act
    rc = main(["--run-id", "fwv-0806-a3f2", "--dry-run"])

    # Assert
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out == {"projects": [], "gears": [], "dry_run": True}


@mock.patch("cleanup.flywheel.Client")
@mock.patch("cleanup.get_site_config")
def test_main_dry_run_reports_matches_without_deleting(
    mock_cfg, mock_client, monkeypatch, capsys
):
    # Arrange
    monkeypatch.setenv("FW_DEV_API", "site:key")
    mock_cfg.return_value = mock.MagicMock(api_key_env="FW_DEV_API", group="fw-verify")
    fw = mock_client.return_value
    fw.projects.iter_find.return_value = iter([_project("fwv-0806-a3f2-exit-codes")])
    fw.gears.iter_find.return_value = iter([_gear("fwv-0806-a3f2-probe")])

    # Act
    rc = main(["--run-id", "fwv-0806-a3f2", "--dry-run"])

    # Assert
    assert rc == 0
    assert json.loads(capsys.readouterr().out) == {
        "projects": ["fwv-0806-a3f2-exit-codes"],
        "gears": ["fwv-0806-a3f2-probe"],
        "dry_run": True,
    }
    fw.delete_project.assert_not_called()
    fw.delete_gear.assert_not_called()


@mock.patch("cleanup.get_site_config")
def test_main_unset_api_key_env_returns_nonzero(mock_cfg, monkeypatch, capsys):
    # Arrange
    monkeypatch.delenv("FW_MISSING_API", raising=False)
    mock_cfg.return_value = SiteConfig(
        api_key_env="FW_MISSING_API", group="fw-verify", label="dev"
    )

    # Act
    rc = main(["--run-id", "fwv-0806-a3f2"])

    # Assert
    assert rc == 1
    assert "FW_MISSING_API" in capsys.readouterr().err
