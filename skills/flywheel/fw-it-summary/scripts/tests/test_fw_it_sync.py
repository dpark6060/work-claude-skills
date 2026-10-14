import json
import urllib.error
from datetime import datetime, timezone
from unittest import mock

import pytest

import fw_it_sync
from fw_it_sync import Desk, JsmClient, TrackedRequest

NOW = datetime(2026, 10, 13, tzinfo=timezone.utc)
FRESH = "2026-10-01T00:00:00+00:00"
OLD = "2026-08-01T00:00:00+00:00"


@pytest.fixture
def client():
    return mock.MagicMock(spec=JsmClient)


def _tracked(key, created=FRESH, stale_flagged=False, desk_id="2"):
    return TrackedRequest(
        key=key, desk_id=desk_id, summary=f"summary {key}", reporter="Pat",
        status="Open", created=created, stale_flagged=stale_flagged,
    )


def _raw_request(key, category="NEW", desk_id="2"):
    return {
        "issueKey": key,
        "serviceDeskId": desk_id,
        "summary": f"summary {key}",
        "reporter": {"displayName": "Pat"},
        "currentStatus": {"status": "Open", "statusCategory": category},
        "createdDate": {"epochMillis": 1791763200000},
    }


def _raw_comment(author, body, epoch_millis=1791763200000):
    return {"author": {"displayName": author}, "created": {"epochMillis": epoch_millis}, "body": body}


def _page(values, is_last=True):
    return {"values": values, "size": len(values), "isLastPage": is_last}


def test_get_paged_values_multiple_pages_collects_all(client):
    # Arrange
    client.get.side_effect = [_page([{"a": 1}], is_last=False), _page([{"a": 2}])]

    # Act
    values = fw_it_sync.get_paged_values(client, "/x")

    # Assert
    assert values == [{"a": 1}, {"a": 2}]
    assert client.get.call_args_list[1].args[1]["start"] == 1


def test_get_open_requests_done_category_excluded(client):
    # Arrange
    client.get.return_value = _page([_raw_request("FIS-1"), _raw_request("FIS-2", category="DONE")])

    # Act
    requests = fw_it_sync.get_open_requests(client, "2")

    # Assert
    assert [r.key for r in requests] == ["FIS-1"]


def test_get_human_comments_automation_dropped(client):
    # Arrange
    client.get.return_value = _page([
        _raw_comment("Dan", "one"),
        _raw_comment("Automation for Jira", "reminder"),
        _raw_comment("Caitlin", "two"),
    ])

    # Act
    comments = fw_it_sync.get_human_comments(client, "FIS-1")

    # Assert
    assert [c.body for c in comments] == ["one", "two"]


def test_get_closed_request_resolved_returns_status_and_last_three_comments(client):
    # Arrange
    client.get.side_effect = [
        {"currentStatus": {"status": "Done", "statusDate": {"epochMillis": 1791763200000}}},
        _page([_raw_comment("Dan", body) for body in ["one", "two", "three", "fixed it"]]),
    ]

    # Act
    closed = fw_it_sync.get_closed_request(client, _tracked("FIS-1"))

    # Assert
    assert closed.final_status == "Done"
    assert closed.closed_at is not None
    assert [c.body for c in closed.comments] == ["two", "three", "fixed it"]


def test_get_comment_updates_tracked_request_reports_only_newer_comments(client):
    # Arrange
    client.get.return_value = _page([
        _raw_comment("Dan", "old", epoch_millis=1791763200000),
        _raw_comment("Dan", "new", epoch_millis=1791849600000),
    ])
    previous = _tracked("FIS-1")
    previous.last_comment_at = "2026-10-12T00:00:00+00:00"  # epoch 1791763200000
    request = _tracked("FIS-1")

    # Act
    updated = fw_it_sync.get_comment_updates(client, [request], [previous])

    # Assert
    assert [c.body for c in updated[0].comments] == ["new"]
    assert request.last_comment_at == "2026-10-13T00:00:00+00:00"


def test_get_comment_updates_untracked_request_reports_all_comments(client):
    # Arrange
    client.get.return_value = _page([_raw_comment("Dan", "one"), _raw_comment("Hans", "two")])
    request = _tracked("FIS-1")

    # Act
    updated = fw_it_sync.get_comment_updates(client, [request], [])

    # Assert
    assert [c.body for c in updated[0].comments] == ["one", "two"]


def test_get_comment_updates_no_new_comments_keeps_last_seen(client):
    # Arrange
    client.get.return_value = _page([_raw_comment("Dan", "old")])
    previous = _tracked("FIS-1")
    previous.last_comment_at = "2026-10-12T00:00:00+00:00"
    request = _tracked("FIS-1")

    # Act
    updated = fw_it_sync.get_comment_updates(client, [request], [previous])

    # Assert
    assert updated == []
    assert request.last_comment_at == "2026-10-12T00:00:00+00:00"


def test_get_closed_request_not_found_reports_no_longer_visible(client):
    # Arrange
    client.get.side_effect = urllib.error.HTTPError("url", 404, "Not Found", {}, None)

    # Act
    closed = fw_it_sync.get_closed_request(client, _tracked("FIS-1"))

    # Assert
    assert closed.final_status.startswith("no longer visible")
    assert closed.closed_at is None
    assert closed.comments == []


def test_get_closed_request_server_error_raises(client):
    # Arrange
    client.get.side_effect = urllib.error.HTTPError("url", 500, "Server Error", {}, None)

    # Act & Assert
    with pytest.raises(urllib.error.HTTPError):
        fw_it_sync.get_closed_request(client, _tracked("FIS-1"))


@pytest.mark.parametrize("created, expected", [(FRESH, False), (OLD, True)])
def test_is_stale_by_age(created, expected):
    assert fw_it_sync.is_stale(_tracked("FIS-1", created=created), NOW) is expected


def test_get_request_changes_splits_new_gone_and_newly_stale():
    # Arrange
    open_requests = [_tracked("NEW-1"), _tracked("KEEP-1"), _tracked("AGED-1", created=OLD)]
    tracked = [_tracked("KEEP-1"), _tracked("AGED-1", created=OLD), _tracked("GONE-1")]

    # Act
    new, gone, newly_stale = fw_it_sync.get_request_changes(open_requests, tracked, NOW)

    # Assert
    assert [r.key for r in new] == ["NEW-1"]
    assert [r.key for r in gone] == ["GONE-1"]
    assert [r.key for r in newly_stale] == ["AGED-1"]


def test_get_request_changes_already_flagged_not_reported_again():
    # Arrange
    open_requests = [_tracked("AGED-1", created=OLD)]
    tracked = [_tracked("AGED-1", created=OLD, stale_flagged=True)]

    # Act
    _, _, newly_stale = fw_it_sync.get_request_changes(open_requests, tracked, NOW)

    # Assert
    assert newly_stale == []


def test_get_request_changes_new_old_request_not_newly_stale():
    # Act
    new, _, newly_stale = fw_it_sync.get_request_changes([_tracked("AGED-1", created=OLD)], [], NOW)

    # Assert
    assert [r.key for r in new] == ["AGED-1"]
    assert newly_stale == []


@mock.patch("fw_it_sync.build_desk_digest")
@mock.patch("fw_it_sync.get_service_desks")
def test_run_sync_no_tracked_file_is_baseline_and_writes_pending(
    mock_desks, mock_digest, client, tmp_path
):
    # Arrange
    mock_desks.return_value = [Desk(desk_id="2", project_key="FIS", name="IT")]
    mock_digest.return_value = fw_it_sync.DeskDigest("2", "FIS", "IT", [], [], [], [], [])

    # Act
    digest = fw_it_sync.run_sync(client, tmp_path, NOW)

    # Assert
    assert digest.baseline is True
    mock_digest.assert_called_once_with(client, mock_desks.return_value[0], [], NOW)
    assert json.loads((tmp_path / "pending.json").read_text())["baseline"] is True
    assert not (tmp_path / "tracked.json").exists()


@mock.patch("fw_it_sync.build_desk_digest")
@mock.patch("fw_it_sync.get_service_desks")
def test_run_sync_tracked_desk_no_longer_visible_raises(mock_desks, mock_digest, client, tmp_path):
    # Arrange
    tracked = {"requests": [vars(_tracked("RA-1", desk_id="6"))]}
    (tmp_path / "tracked.json").write_text(json.dumps(tracked))
    mock_desks.return_value = [Desk(desk_id="2", project_key="FIS", name="IT")]

    # Act & Assert
    with pytest.raises(ValueError, match="6"):
        fw_it_sync.run_sync(client, tmp_path, NOW)
    mock_digest.assert_not_called()


def test_run_commit_tracks_open_requests_marks_stale_and_removes_pending(tmp_path):
    # Arrange
    pending = {"desks": [{"open": [vars(_tracked("FIS-1")), vars(_tracked("FIS-2", created=OLD))]}]}
    (tmp_path / "pending.json").write_text(json.dumps(pending))

    # Act
    count = fw_it_sync.run_commit(tmp_path, NOW)

    # Assert
    tracked = json.loads((tmp_path / "tracked.json").read_text())["requests"]
    assert count == 2
    assert {r["key"]: r["stale_flagged"] for r in tracked} == {"FIS-1": False, "FIS-2": True}
    assert "last_comment_at" in tracked[0]
    assert not (tmp_path / "pending.json").exists()


def test_run_commit_no_pending_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        fw_it_sync.run_commit(tmp_path, NOW)


@mock.patch.dict("os.environ", {}, clear=True)
def test_get_token_missing_raises():
    with pytest.raises(ValueError):
        fw_it_sync.get_token(None)


@mock.patch.dict("os.environ", {"JIRA_TOKEN": "env-token"})
def test_get_token_argument_wins_over_env():
    assert fw_it_sync.get_token("arg-token") == "arg-token"
