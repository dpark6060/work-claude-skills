import pytest

from build_project import ItemSpec, parse_item, parse_spec


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
