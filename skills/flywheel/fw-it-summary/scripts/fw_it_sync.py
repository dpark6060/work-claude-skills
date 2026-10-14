#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Track Flywheel JSM portal requests across runs and report what changed.

`sync` fetches every open request on every visible service desk, diffs it against
cache/tracked.json, writes the result to cache/pending.json and prints it.
`commit` replaces tracked.json with pending.json's open requests. Run it only after
the digest has been posted, so a failed post never loses a run's changes.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

SITE = "https://flywheelio.atlassian.net"
DEFAULT_EMAIL = "davidparker@flywheel.io"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
STALE_AFTER = timedelta(days=30)
PAGE_SIZE = 100  # JSM customer API max page size
REQUEST_TIMEOUT = 30  # seconds; JSM calls normally return in under 2
CLOSING_COMMENT_COUNT = 3
COMMENT_BODY_LIMIT = 1000  # chars; keeps pending.json readable when someone pastes a log
AUTOMATION_AUTHORS = {"Automation for Jira"}


@dataclass
class Desk:
    """A JSM service desk visible to the portal account."""

    desk_id: str
    project_key: str
    name: str


@dataclass
class TrackedRequest:
    """An open request as stored in tracked.json."""

    key: str
    desk_id: str
    summary: str
    reporter: str
    status: str
    created: str  # ISO 8601, UTC
    stale_flagged: bool = False
    last_comment_at: str | None = None  # newest human comment already reported, ISO 8601 UTC


@dataclass
class Comment:
    """A public, human-written comment on a request."""

    author: str
    created: str
    body: str


@dataclass
class UpdatedRequest:
    """An open request with human comments posted since the last commit."""

    key: str
    summary: str
    status: str
    comments: list[Comment]


@dataclass
class ClosedRequest:
    """A tracked request that is no longer open, with what IT said when closing it."""

    key: str
    summary: str
    reporter: str
    created: str
    final_status: str
    closed_at: str | None
    comments: list[Comment] = field(default_factory=list)


@dataclass
class DeskDigest:
    """Everything that changed on one desk since the last commit."""

    desk_id: str
    project_key: str
    name: str
    new: list[TrackedRequest]
    closed: list[ClosedRequest]
    newly_stale: list[TrackedRequest]
    updated: list[UpdatedRequest]
    open: list[TrackedRequest]


@dataclass
class Digest:
    """The full sync result written to pending.json."""

    baseline: bool
    generated_at: str
    stale_after_days: int
    desks: list[DeskDigest]


class JsmClient:
    """Minimal JSM customer REST client using basic auth."""

    def __init__(self, site: str, email: str, token: str):
        self.base_url = f"{site}/rest/servicedeskapi"
        credentials = base64.b64encode(f"{email}:{token}".encode()).decode()
        self.headers = {"Authorization": f"Basic {credentials}", "Accept": "application/json"}

    def get(self, path: str, params: dict | None = None) -> dict:
        """GET a servicedeskapi path and return the decoded JSON body."""
        query = f"?{urllib.parse.urlencode(params)}" if params else ""
        request = urllib.request.Request(f"{self.base_url}{path}{query}", headers=self.headers)
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return json.load(response)


def get_paged_values(client: JsmClient, path: str, params: dict | None = None) -> list[dict]:
    """Collect `values` from every page of a paged JSM endpoint."""
    values = []
    start = 0
    while True:
        page = client.get(path, {**(params or {}), "start": start, "limit": PAGE_SIZE})
        values.extend(page["values"])
        if page["isLastPage"]:
            return values
        start += page["size"]


def get_service_desks(client: JsmClient) -> list[Desk]:
    """Return every service desk the portal account can see."""
    return [
        Desk(desk_id=raw["id"], project_key=raw["projectKey"], name=raw["projectName"])
        for raw in get_paged_values(client, "/servicedesk")
    ]


def get_open_requests(client: JsmClient, desk_id: str) -> list[TrackedRequest]:
    """Return a desk's requests whose status category is not DONE."""
    raw_requests = get_paged_values(
        client,
        "/request",
        {"requestOwnership": "ALL_REQUESTS", "requestStatus": "OPEN_REQUESTS", "serviceDeskId": desk_id},
    )
    # OPEN_REQUESTS still returns closed tickets on desks that never set a resolution
    # (e.g. "Expired"), so the status category is the only reliable open check.
    return [
        _build_tracked_request(raw)
        for raw in raw_requests
        if raw["currentStatus"]["statusCategory"] != "DONE"
    ]


def _build_tracked_request(raw: dict) -> TrackedRequest:
    """Build a TrackedRequest from a JSM request payload."""
    return TrackedRequest(
        key=raw["issueKey"],
        desk_id=raw["serviceDeskId"],
        summary=raw["summary"],
        reporter=raw["reporter"]["displayName"],
        status=raw["currentStatus"]["status"],
        created=_get_utc_iso(raw["createdDate"]["epochMillis"]),
    )


def _get_utc_iso(epoch_millis: int) -> str:
    """Convert JSM epoch milliseconds to an ISO 8601 UTC string."""
    return datetime.fromtimestamp(epoch_millis / 1000, tz=timezone.utc).isoformat()


def get_closed_request(client: JsmClient, tracked: TrackedRequest) -> ClosedRequest:
    """Fetch a no-longer-open request's final status and closing comments."""
    try:
        raw = client.get(f"/request/{tracked.key}")
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        # A deleted or moved ticket is still a closure the digest should report.
        return ClosedRequest(
            key=tracked.key,
            summary=tracked.summary,
            reporter=tracked.reporter,
            created=tracked.created,
            final_status="no longer visible (deleted or moved)",
            closed_at=None,
        )
    return ClosedRequest(
        key=tracked.key,
        summary=tracked.summary,
        reporter=tracked.reporter,
        created=tracked.created,
        final_status=raw["currentStatus"]["status"],
        closed_at=_get_utc_iso(raw["currentStatus"]["statusDate"]["epochMillis"]),
        comments=get_human_comments(client, tracked.key)[-CLOSING_COMMENT_COUNT:],
    )


def get_human_comments(client: JsmClient, key: str) -> list[Comment]:
    """Return every public, human-written comment on a request, oldest first."""
    raw_comments = get_paged_values(client, f"/request/{key}/comment", {"public": "true", "internal": "false"})
    return [
        Comment(
            author=raw["author"]["displayName"],
            created=_get_utc_iso(raw["created"]["epochMillis"]),
            body=raw["body"][:COMMENT_BODY_LIMIT],
        )
        for raw in raw_comments
        if raw["author"]["displayName"] not in AUTOMATION_AUTHORS
    ]


def get_comment_updates(
    client: JsmClient, open_requests: list[TrackedRequest], tracked: list[TrackedRequest]
) -> list[UpdatedRequest]:
    """Return the open requests with comments posted since the last commit.

    Also sets each open request's last_comment_at, so commit records which comments
    this run reported. Requests not tracked before report all their comments.
    """
    tracked_by_key = {request.key: request for request in tracked}
    updated = []
    for request in open_requests:
        previous = tracked_by_key.get(request.key)
        last_seen = previous.last_comment_at if previous else None
        comments = [
            comment
            for comment in get_human_comments(client, request.key)
            if last_seen is None or datetime.fromisoformat(comment.created) > datetime.fromisoformat(last_seen)
        ]
        request.last_comment_at = comments[-1].created if comments else last_seen
        if comments:
            updated.append(
                UpdatedRequest(key=request.key, summary=request.summary, status=request.status, comments=comments)
            )
    return updated


def is_stale(request: TrackedRequest, now: datetime) -> bool:
    """Return True when a request has been open longer than STALE_AFTER."""
    return now - datetime.fromisoformat(request.created) > STALE_AFTER


def get_request_changes(
    open_requests: list[TrackedRequest], tracked: list[TrackedRequest], now: datetime
) -> tuple[list[TrackedRequest], list[TrackedRequest], list[TrackedRequest]]:
    """Diff one desk's open requests against its tracked ones.

    Returns:
        tuple: (new requests, tracked requests no longer open, requests that crossed
            the stale line since they were last tracked)
    """
    tracked_by_key = {request.key: request for request in tracked}
    open_keys = {request.key for request in open_requests}
    new = [request for request in open_requests if request.key not in tracked_by_key]
    gone = [request for request in tracked if request.key not in open_keys]
    newly_stale = [
        request
        for request in open_requests
        if request.key in tracked_by_key
        and not tracked_by_key[request.key].stale_flagged
        and is_stale(request, now)
    ]
    return new, gone, newly_stale


def build_desk_digest(
    client: JsmClient, desk: Desk, tracked: list[TrackedRequest], now: datetime
) -> DeskDigest:
    """Fetch one desk's open requests and describe what changed since the last commit."""
    open_requests = get_open_requests(client, desk.desk_id)
    new, gone, newly_stale = get_request_changes(open_requests, tracked, now)
    return DeskDigest(
        desk_id=desk.desk_id,
        project_key=desk.project_key,
        name=desk.name,
        new=new,
        closed=[get_closed_request(client, request) for request in gone],
        newly_stale=newly_stale,
        updated=get_comment_updates(client, open_requests, tracked),
        open=open_requests,
    )


def load_tracked(cache_dir: Path) -> list[TrackedRequest]:
    """Load tracked.json; an absent file means no baseline has been committed yet."""
    tracked_path = cache_dir / "tracked.json"
    if not tracked_path.exists():
        return []
    return [TrackedRequest(**raw) for raw in json.loads(tracked_path.read_text())["requests"]]


def run_sync(client: JsmClient, cache_dir: Path, now: datetime) -> Digest:
    """Build the digest for every desk and write it to pending.json."""
    tracked = load_tracked(cache_dir)
    desks = get_service_desks(client)
    desk_ids = {desk.desk_id for desk in desks}
    orphaned = sorted({request.desk_id for request in tracked} - desk_ids)
    if orphaned:
        # Dropping these silently would report their tickets as neither open nor closed.
        raise ValueError(
            f"tracked.json has requests on desk id(s) {orphaned} that this account can no "
            "longer see. Check portal access, or delete those entries from tracked.json."
        )
    digest = Digest(
        baseline=not tracked,
        generated_at=now.isoformat(),
        stale_after_days=STALE_AFTER.days,
        desks=[
            build_desk_digest(client, desk, [r for r in tracked if r.desk_id == desk.desk_id], now)
            for desk in desks
        ],
    )
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "pending.json").write_text(json.dumps(asdict(digest), indent=2))
    return digest


def run_commit(cache_dir: Path, now: datetime) -> int:
    """Replace tracked.json with pending.json's open requests and return how many are tracked."""
    pending_path = cache_dir / "pending.json"
    pending = json.loads(pending_path.read_text())
    tracked = [TrackedRequest(**raw) for desk in pending["desks"] for raw in desk["open"]]
    # Every stale request was either reported this run or before, so mark them all.
    for request in tracked:
        request.stale_flagged = is_stale(request, now)
    payload = {"committed_at": now.isoformat(), "requests": [asdict(r) for r in tracked]}
    (cache_dir / "tracked.json").write_text(json.dumps(payload, indent=2))
    pending_path.unlink()
    return len(tracked)


def get_token(token: str | None) -> str:
    """Resolve the API token from the argument, then JIRA_TOKEN, then raise."""
    resolved = token or os.environ.get("JIRA_TOKEN")
    if not resolved:
        raise ValueError(
            "No Atlassian API token. Pass --token or set JIRA_TOKEN "
            "(create one at https://id.atlassian.com/manage-profile/security/api-tokens)."
        )
    return resolved


def main() -> None:
    """Parse arguments and run sync or commit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["sync", "commit"])
    parser.add_argument("--email", default=os.environ.get("JIRA_EMAIL", DEFAULT_EMAIL))
    parser.add_argument("--token")
    parser.add_argument("--cache-dir", type=Path, default=CACHE_DIR)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)

    if args.command == "commit":
        count = run_commit(args.cache_dir, now)
        print(json.dumps({"committed": True, "tracked": count}))
        return

    client = JsmClient(SITE, args.email, get_token(args.token))
    digest = run_sync(client, args.cache_dir, now)
    json.dump(asdict(digest), sys.stdout, indent=2)


if __name__ == "__main__":
    main()
