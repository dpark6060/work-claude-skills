import json
from unittest import mock

import flywheel
import pytest

from build_project import (
    FAKE_DICOM_BYTES,
    BuildResult,
    ItemSpec,
    Target,
    add_containers,
    add_file,
    get_or_add_group,
    is_classification_applied,
    main,
    orchestrate_build,
    parse_item,
    parse_spec,
    process_metadata,
    set_file_classification,
)
from fwv_common import SiteConfig


def _parent_reading_back(classification):
    """Container mock whose fresh read reports this file classification."""
    parent = mock.MagicMock()
    parent.reload.return_value.get_file.return_value.classification = classification
    return parent


@pytest.fixture
def mock_fw():
    fw = mock.MagicMock()
    fw.projects.find_first.return_value = None
    project = fw.get_group.return_value.add_project.return_value
    project.subjects.find_first.return_value = None
    project.get_file.return_value = None
    project.add_subject.return_value.get_file.return_value = None
    return fw


def test_parse_item_single_segment_is_project_file():
    # Act
    item = parse_item("readme.txt", {})

    # Assert
    assert item.containers == ()
    assert item.filename == "readme.txt"


def test_parse_item_four_segments_is_acquisition_file():
    # Act
    item = parse_item("sub-01/ses-01/acq-01/image.dcm", {})

    # Assert
    assert item.containers == ("sub-01", "ses-01", "acq-01")
    assert item.filename == "image.dcm"


def test_parse_item_trailing_slash_is_container_only():
    # Act
    item = parse_item("sub-02/", {})

    # Assert
    assert item.containers == ("sub-02",)
    assert item.filename is None


def test_parse_item_too_deep_raises_valueerror():
    # Act & Assert
    with pytest.raises(ValueError, match="deeper"):
        parse_item("a/b/c/d/file.txt", {})


def test_parse_item_attaches_matching_metadata():
    # Arrange
    metadata = {"sub-01/notes.txt": {"content": "real", "info": {"a": "b"}}}

    # Act
    item = parse_item("sub-01/notes.txt", metadata)

    # Assert
    assert item.meta == {"content": "real", "info": {"a": "b"}}


def test_parse_item_path_property_joins_segments():
    # Act
    item = parse_item("sub-01/ses-01/acq-01/image.dcm", {})

    # Assert
    assert item.path == "sub-01/ses-01/acq-01/image.dcm"


def test_parse_spec_substitutes_run_id_in_project_label():
    # Arrange
    spec = {"project": "{run_id}-exit-codes", "items": ["readme.txt"]}

    # Act
    label, _ = parse_spec(spec, "fwv-0806-a3f2")

    # Assert
    assert label == "fwv-0806-a3f2-exit-codes"


def test_parse_spec_returns_one_itemspec_per_entry():
    # Arrange
    spec = {"project": "p-{run_id}", "items": ["readme.txt", "sub-01/"]}

    # Act
    _, items = parse_spec(spec, "fwv-0806-a3f2")

    # Assert
    assert [i.filename for i in items] == ["readme.txt", None]
    assert all(isinstance(i, ItemSpec) for i in items)


def test_add_containers_creates_missing_chain_and_registers_paths():
    # Arrange
    project = mock.MagicMock()
    project.subjects.find_first.return_value = None
    subject = project.add_subject.return_value
    subject.sessions.find_first.return_value = None
    session = subject.add_session.return_value
    session.acquisitions.find_first.return_value = None
    registry = {}

    # Act
    leaf = add_containers(project, ("sub-01", "ses-01", "acq-01"), registry)

    # Assert
    project.subjects.find_first.assert_called_once_with('label="sub-01"')
    project.add_subject.assert_called_once_with(label="sub-01")
    subject.add_session.assert_called_once_with(label="ses-01")
    session.add_acquisition.assert_called_once_with(label="acq-01")
    assert leaf is session.add_acquisition.return_value
    assert set(registry) == {"sub-01", "sub-01/ses-01", "sub-01/ses-01/acq-01"}


def test_add_containers_reuses_existing_child():
    # Arrange
    project = mock.MagicMock()
    existing = mock.MagicMock()
    project.subjects.find_first.return_value = existing

    # Act
    leaf = add_containers(project, ("sub-01",), {})

    # Assert
    project.add_subject.assert_not_called()
    assert leaf is existing


def test_add_containers_empty_chain_returns_project():
    # Arrange
    project = mock.MagicMock()
    registry = {}

    # Act
    leaf = add_containers(project, (), registry)

    # Assert
    assert leaf is project
    assert registry == {}


def test_add_file_real_content_skips_upload_and_records_pending():
    # Arrange
    parent = mock.MagicMock()
    parent.get_file.side_effect = Exception("404 file not found")
    item = ItemSpec(("sub-01",), "notes.txt", {"content": "real"})
    pending = []
    registry = {}

    # Act
    add_file(parent, item, pending, registry)

    # Assert
    parent.upload_file.assert_not_called()
    assert pending == ["sub-01/notes.txt"]
    assert registry["sub-01/notes.txt"] == Target(
        kind="pending", container=parent, filename="notes.txt"
    )


def test_add_file_fake_dicom_uploads_fake_bytes():
    # Arrange
    parent = mock.MagicMock()
    item = ItemSpec((), "image.dcm", {"content": "fake-dicom"})

    # Act
    add_file(parent, item, [], {})

    # Assert
    spec_arg = parent.upload_file.call_args.args[0]
    assert spec_arg.name == "image.dcm"
    assert spec_arg.contents.getvalue() == FAKE_DICOM_BYTES
    assert spec_arg.size == len(FAKE_DICOM_BYTES)


def test_add_file_default_content_uploads_text_placeholder():
    # Arrange
    parent = mock.MagicMock()
    item = ItemSpec((), "readme.txt", {})

    # Act
    add_file(parent, item, [], {})

    # Assert
    parent.upload_file.assert_called_once()
    spec_arg = parent.upload_file.call_args.args[0]
    assert b"readme.txt" in spec_arg.contents.getvalue()


def test_add_file_uploaded_file_is_registered_by_path():
    # Arrange
    parent = mock.MagicMock()
    item = ItemSpec(("sub-01", "ses-01"), "image.dcm", {"content": "fake-dicom"})
    registry = {}

    # Act
    add_file(parent, item, [], registry)

    # Assert
    assert registry["sub-01/ses-01/image.dcm"] == Target(
        kind="file", container=parent, filename="image.dcm"
    )


def test_process_metadata_container_entry_updates_info():
    # Arrange
    container = mock.MagicMock()
    registry = {"sub-01": Target(kind="container", container=container)}

    # Act
    process_metadata(registry, {"sub-01": {"info": {"cohort": "A"}}})

    # Assert
    container.update_info.assert_called_once_with({"cohort": "A"})


def test_process_metadata_file_entry_sets_info_classification_and_type():
    # Arrange
    parent = _parent_reading_back({"Intent": ["Structural"]})
    registry = {
        "sub-01/image.dcm": Target(kind="file", container=parent, filename="image.dcm")
    }
    meta = {
        "sub-01/image.dcm": {
            "type": "dicom",
            "modality": "MR",
            "content": "fake-dicom",
            "info": {"SeriesDescription": "T1w"},
            "classification": {"Intent": ["Structural"]},
        }
    }

    # Act
    process_metadata(registry, meta)

    # Assert
    parent.update_file.assert_called_once_with(
        "image.dcm", {"type": "dicom", "modality": "MR"}
    )
    parent.update_file_classification.assert_called_once_with(
        "image.dcm", {"Intent": ["Structural"]}
    )
    parent.update_file_info.assert_called_once_with(
        "image.dcm", {"SeriesDescription": "T1w"}
    )


def test_process_metadata_file_entry_sets_modality_before_classification():
    # Arrange - the API rejects non-Custom classification keys on a file whose
    # modality is unset, so this ordering is a correctness requirement.
    parent = _parent_reading_back({"Intent": ["Structural"]})
    registry = {
        "sub-01/image.dcm": Target(kind="file", container=parent, filename="image.dcm")
    }
    meta = {
        "sub-01/image.dcm": {
            "modality": "MR",
            "classification": {"Intent": ["Structural"]},
        }
    }

    # Act
    process_metadata(registry, meta)

    # Assert
    called = [name for name, _, _ in parent.mock_calls]
    assert called.index("update_file") < called.index("update_file_classification")


def test_set_file_classification_returns_true_when_the_write_survives():
    # Arrange
    parent = _parent_reading_back({"Intent": ["Structural"]})
    target = Target(kind="file", container=parent, filename="image.dcm")

    # Act
    applied = set_file_classification(target, {"Intent": ["Structural"]})

    # Assert
    assert applied is True
    parent.update_file_classification.assert_called_once_with(
        "image.dcm", {"Intent": ["Structural"]}
    )


@mock.patch("build_project.time.sleep")
def test_set_file_classification_rewrites_until_the_value_sticks(mock_sleep):
    # Arrange - the ingest gears wipe the first two writes.
    parent = mock.MagicMock()
    fresh = parent.reload.return_value.get_file.return_value
    type(fresh).classification = mock.PropertyMock(
        side_effect=[{}, {}, {"Intent": ["Structural"]}]
    )
    target = Target(kind="file", container=parent, filename="image.dcm")

    # Act
    applied = set_file_classification(target, {"Intent": ["Structural"]})

    # Assert
    assert applied is True
    assert parent.update_file_classification.call_count == 3
    assert mock_sleep.call_count == 2


@mock.patch("build_project.time.sleep")
def test_set_file_classification_gives_up_and_warns_after_last_attempt(
    mock_sleep, capsys
):
    # Arrange
    parent = _parent_reading_back({})
    target = Target(kind="file", container=parent, filename="image.dcm")

    # Act
    applied = set_file_classification(target, {"Intent": ["Structural"]})

    # Assert
    assert applied is False
    assert parent.update_file_classification.call_count == 4
    assert "keeps getting overwritten" in capsys.readouterr().err


def test_is_classification_applied_ignores_keys_added_by_the_ingest_gears():
    # Arrange
    parent = _parent_reading_back({"Intent": ["Structural"], "Features": ["Derived"]})
    target = Target(kind="file", container=parent, filename="image.dcm")

    # Act & Assert
    assert is_classification_applied(target, {"Intent": ["Structural"]}) is True


def test_is_classification_applied_missing_file_is_false():
    # Arrange
    parent = mock.MagicMock()
    parent.reload.return_value.get_file.return_value = None
    target = Target(kind="file", container=parent, filename="image.dcm")

    # Act & Assert
    assert is_classification_applied(target, {"Intent": ["Structural"]}) is False


def test_process_metadata_file_entry_without_type_or_modality_skips_update_file():
    # Arrange
    parent = mock.MagicMock()
    registry = {
        "sub-01/notes.txt": Target(kind="file", container=parent, filename="notes.txt")
    }

    # Act
    process_metadata(registry, {"sub-01/notes.txt": {"info": {"a": 1}}})

    # Assert
    parent.update_file.assert_not_called()
    parent.update_file_info.assert_called_once_with("notes.txt", {"a": 1})


def test_process_metadata_unknown_path_raises_valueerror():
    # Act & Assert
    with pytest.raises(ValueError, match="no created container or file"):
        process_metadata({}, {"ghost/file.txt": {"info": {}}})


def test_process_metadata_pending_file_is_skipped_silently():
    # Arrange
    registry = {
        "sub-01/notes.txt": Target(
            kind="pending", container=mock.MagicMock(), filename="notes.txt"
        )
    }

    # Act
    process_metadata(
        registry, {"sub-01/notes.txt": {"content": "real", "info": {"a": 1}}}
    )

    # Assert — no exception, no calls
    registry["sub-01/notes.txt"].container.update_file_info.assert_not_called()


def test_add_file_real_content_absent_file_records_pending():
    # Arrange
    parent = mock.MagicMock()
    parent.get_file.return_value = None
    item = ItemSpec(("sub-01",), "notes.txt", {"content": "real"})
    pending = []
    registry = {}

    # Act
    add_file(parent, item, pending, registry)

    # Assert
    parent.upload_file.assert_not_called()
    assert pending == ["sub-01/notes.txt"]
    assert registry["sub-01/notes.txt"].kind == "pending"


def test_add_file_real_content_already_on_container_registers_as_file():
    # Arrange
    parent = mock.MagicMock()
    parent.get_file.return_value = mock.MagicMock()
    item = ItemSpec(("sub-01",), "notes.txt", {"content": "real"})
    pending = []
    registry = {}

    # Act
    add_file(parent, item, pending, registry)

    # Assert
    parent.upload_file.assert_not_called()
    assert pending == []
    assert registry["sub-01/notes.txt"] == Target(
        kind="file", container=parent, filename="notes.txt"
    )


def test_process_metadata_applies_info_to_intermediate_container_from_chain():
    # Arrange — metadata keyed on a subject that only appears inside deeper item paths
    project = mock.MagicMock()
    project.subjects.find_first.return_value = None
    subject = project.add_subject.return_value
    subject.sessions.find_first.return_value = None
    session = subject.add_session.return_value
    session.acquisitions.find_first.return_value = None
    registry = {}
    add_containers(project, ("sub-01", "ses-01", "acq-01"), registry)

    # Act
    process_metadata(registry, {"sub-01": {"info": {"cohort": "A"}}})

    # Assert
    subject.update_info.assert_called_once_with({"cohort": "A"})


def test_get_or_add_group_existing_group_is_returned_without_creating():
    # Arrange
    fw = mock.MagicMock()

    # Act
    group = get_or_add_group(fw, "fw-verify")

    # Assert
    assert group is fw.get_group.return_value
    fw.get_group.assert_called_once_with("fw-verify")
    fw.add_group.assert_not_called()


def test_get_or_add_group_missing_group_is_created_then_fetched():
    # Arrange
    fw = mock.MagicMock()
    created = mock.MagicMock()
    fw.get_group.side_effect = [flywheel.ApiException(status=404), created]

    # Act
    group = get_or_add_group(fw, "fw-verify")

    # Assert
    assert group is created
    fw.add_group.assert_called_once()
    body = fw.add_group.call_args.args[0]
    assert body.id == "fw-verify"
    assert body.label == "fw-verify"


def test_get_or_add_group_non_404_error_is_reraised():
    # Arrange
    fw = mock.MagicMock()
    fw.get_group.side_effect = flywheel.ApiException(status=403)

    # Act & Assert
    with pytest.raises(flywheel.ApiException):
        get_or_add_group(fw, "fw-verify")

    fw.add_group.assert_not_called()


def test_orchestrate_build_creates_project_under_group(mock_fw):
    # Arrange
    spec = {"project": "{run_id}-t", "items": ["readme.txt"]}

    # Act
    result = orchestrate_build(mock_fw, "fw-verify", spec, "fwv-0806-a3f2")

    # Assert
    mock_fw.get_group.assert_called_once_with("fw-verify")
    mock_fw.get_group.return_value.add_project.assert_called_once_with(
        label="fwv-0806-a3f2-t"
    )
    assert isinstance(result, BuildResult)
    assert result.project_label == "fwv-0806-a3f2-t"
    assert result.run_id == "fwv-0806-a3f2"


def test_orchestrate_build_collects_pending_uploads(mock_fw):
    # Arrange
    spec = {
        "project": "{run_id}-t",
        "items": ["sub-01/notes.txt"],
        "metadata": {"sub-01/notes.txt": {"content": "real"}},
    }

    # Act
    result = orchestrate_build(mock_fw, "fw-verify", spec, "fwv-0806-a3f2")

    # Assert
    assert result.pending_uploads == ["sub-01/notes.txt"]


def test_orchestrate_build_reuses_existing_project(mock_fw):
    # Arrange
    existing = mock.MagicMock()
    mock_fw.projects.find_first.return_value = existing
    spec = {"project": "{run_id}-t", "items": []}

    # Act
    orchestrate_build(mock_fw, "fw-verify", spec, "fwv-0806-a3f2")

    # Assert
    mock_fw.get_group.return_value.add_project.assert_not_called()
    mock_fw.projects.find_first.assert_called_once_with(
        'group._id=fw-verify,label="fwv-0806-a3f2-t"'
    )


def test_orchestrate_build_uploads_files_for_non_real_items(mock_fw):
    # Arrange
    spec = {"project": "{run_id}-t", "items": ["sub-01/notes.txt"]}

    # Act
    orchestrate_build(mock_fw, "fw-verify", spec, "fwv-0806-a3f2")

    # Assert
    subject = mock_fw.get_group.return_value.add_project.return_value.add_subject
    subject.return_value.upload_file.assert_called_once()


@mock.patch("build_project.flywheel.Client")
@mock.patch("build_project.get_site_config")
def test_main_prints_result_json(
    mock_get_cfg, mock_client, tmp_path, monkeypatch, capsys
):
    # Arrange
    monkeypatch.setenv("FW_DEV_API", "site:key")
    mock_get_cfg.return_value = mock.MagicMock(
        api_key_env="FW_DEV_API", group="fw-verify"
    )
    fw = mock_client.return_value
    fw.projects.find_first.return_value = None
    spec_path = tmp_path / "spec.json"
    spec_path.write_text('{"project": "{run_id}-t", "items": []}')

    # Act
    rc = main(["--spec", str(spec_path), "--run-id", "fwv-0806-beef"])

    # Assert
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["run_id"] == "fwv-0806-beef"
    assert out["pending_uploads"] == []


@mock.patch("build_project.get_site_config")
def test_main_unset_api_key_env_returns_nonzero(
    mock_get_cfg, tmp_path, monkeypatch, capsys
):
    # Arrange
    monkeypatch.delenv("FW_MISSING_API", raising=False)
    mock_get_cfg.return_value = SiteConfig(
        api_key_env="FW_MISSING_API", group="fw-verify", label="dev"
    )
    spec_path = tmp_path / "spec.json"
    spec_path.write_text('{"project": "{run_id}-t", "items": []}')

    # Act
    rc = main(["--spec", str(spec_path)])

    # Assert
    assert rc == 1
    assert "FW_MISSING_API" in capsys.readouterr().err


@mock.patch("build_project.flywheel.Client")
@mock.patch("build_project.get_site_config")
def test_main_missing_spec_file_returns_nonzero(
    mock_get_cfg, mock_client, tmp_path, monkeypatch, capsys
):
    # Arrange
    monkeypatch.setenv("FW_DEV_API", "site:key")
    mock_get_cfg.return_value = SiteConfig(
        api_key_env="FW_DEV_API", group="fw-verify", label="dev"
    )
    missing_spec = tmp_path / "ghost.json"

    # Act
    rc = main(["--spec", str(missing_spec)])

    # Assert
    assert rc == 1
    assert "ghost.json" in capsys.readouterr().err
    mock_client.return_value.get_group.assert_not_called()


@mock.patch("build_project.get_site_config")
def test_main_unknown_site_returns_nonzero(mock_get_cfg, tmp_path, capsys):
    # Arrange
    mock_get_cfg.side_effect = KeyError(
        "Site 'nope' not found in config. Available sites: ['dev']"
    )
    spec_path = tmp_path / "spec.json"
    spec_path.write_text('{"project": "{run_id}-t", "items": []}')

    # Act
    rc = main(["--spec", str(spec_path), "--site", "nope"])

    # Assert
    assert rc != 0
    assert "nope" in capsys.readouterr().err
