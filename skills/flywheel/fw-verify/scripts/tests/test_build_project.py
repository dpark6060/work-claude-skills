from unittest import mock

import pytest

from build_project import (
    FAKE_DICOM_BYTES,
    ItemSpec,
    Target,
    add_containers,
    add_file,
    parse_item,
    parse_spec,
    process_metadata,
)


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
    parent = mock.MagicMock()
    registry = {
        "sub-01/image.dcm": Target(kind="file", container=parent, filename="image.dcm")
    }
    meta = {
        "sub-01/image.dcm": {
            "type": "dicom",
            "content": "fake-dicom",
            "info": {"SeriesDescription": "T1w"},
            "classification": {"Intent": ["Structural"]},
        }
    }

    # Act
    process_metadata(registry, meta)

    # Assert
    parent.update_file_info.assert_called_once_with(
        "image.dcm", {"SeriesDescription": "T1w"}
    )
    parent.update_file_classification.assert_called_once_with(
        "image.dcm", {"Intent": ["Structural"]}
    )
    parent.update_file.assert_called_once_with("image.dcm", {"type": "dicom"})


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
