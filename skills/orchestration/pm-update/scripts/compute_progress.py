#!/usr/bin/env python3
"""Compute the progress figures for a pm-update epic report.

Reads a report input JSON file and writes the derived figures to stdout as JSON:
budget burn, per-deliverable burn, the hours the live board holds, velocity from
worked days, the budget exhaustion date, the trend delta, and the verdict. The
caller writes the prose. The input schema lives in the pm-update SKILL.md.

The model is top-down. The epic carries the hours budget, Clockify carries the
hours consumed, and the board carries only the tickets that are live right now.
Future work is deliberately unticketed, so this script never asks for an
estimate it would have to invent, and never reports missing tickets as a gap.
"""

import argparse
import json
import math
import os
import sys
import typing as t
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

BAR_WIDTH = 20
BAR_FULL = "█"
BAR_EMPTY = "░"

WORK_DAYS_PER_WEEK = 5

STATUS_LABELS = {
    "done": "✅ Done",
    "in_review": "\U0001f50d In review",
    "in_progress": "\U0001f504 In progress",
    "blocked": "⛔ Blocked",
    "not_started": "⬜ Not started",
}

# Order matters: the first state present in a deliverable's tickets wins the rollup.
STATE_PRECEDENCE = ["blocked", "in_progress", "in_review", "not_started", "done"]

# Burn past this fraction of the budget, with work not started, reads as at risk.
BURN_WARNING_FRACTION = 0.8

EXIT_BAD_INPUT = 2
EXIT_NO_DATA = 3


@dataclass
class Budget:
    """The hours the epic is allowed, and where that figure came from."""

    total_hours: t.Optional[float]
    source: str
    by_deliverable: t.Dict[str, float] = field(default_factory=dict)


@dataclass
class Consumed:
    """The hours already spent, from the time tracker."""

    total_hours: float
    source: str
    by_deliverable: t.Dict[str, float] = field(default_factory=dict)


@dataclass
class VelocityInput:
    """The raw worked-day figures that produce a weekly rate."""

    hours: t.Optional[float]
    worked_days: t.Optional[int]
    since: t.Optional[date]
    days_out: int


@dataclass
class Velocity:
    """Hours the team spends on the epic per working week, and its basis."""

    per_week: t.Optional[float]
    source: str


@dataclass
class Ticket:
    """One live ticket on the board."""

    key: str
    summary: str
    deliverable: str
    status: str
    estimate_hours: t.Optional[float]
    remaining_hours: t.Optional[float]
    consumed_hours: t.Optional[float]
    evidence: str


@dataclass
class Deliverable:
    """One named piece of the epic, such as a gear."""

    key: str
    summary: str
    state: str
    note: str
    percent_complete: t.Optional[float]
    percent_complete_basis: str


@dataclass
class Snapshot:
    """The figures carried by the previous report, used for the trend delta."""

    date: date
    budget_hours: t.Optional[float]
    consumed_hours: t.Optional[float]
    burn_percent: t.Optional[float]
    board_remaining_hours: t.Optional[float]


@dataclass
class Verdict:
    """The budget call and the numbers behind it."""

    label: str
    detail: str
    budget_exhausted_on: t.Optional[date]


@dataclass
class ReportInput:
    """Everything the caller gathered from Jira, GitLab and the time tracker."""

    epic_key: str
    epic_summary: str
    as_of: date
    due_date: t.Optional[date]
    budget: Budget
    consumed: Consumed
    velocity_input: VelocityInput
    board: t.List[Ticket]
    deliverables: t.List[Deliverable]
    prior_snapshot: t.Optional[Snapshot]


def get_date(raw: t.Optional[str], field_name: str) -> t.Optional[date]:
    """Parse an ISO date string, or return None when it is absent."""
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"{field_name} must be an ISO date (YYYY-MM-DD), got {raw!r}")


def get_short_date(value: date) -> str:
    """Format a date as 'Sep 8' for use in report prose."""
    return f"{value:%b} {value.day}"


def get_bar(percent: t.Optional[float]) -> str:
    """Render a fixed-width progress bar, empty when the percentage is unknown."""
    if percent is None:
        return BAR_EMPTY * BAR_WIDTH
    filled = int(round(percent / 100 * BAR_WIDTH))
    filled = max(0, min(BAR_WIDTH, filled))
    return BAR_FULL * filled + BAR_EMPTY * (BAR_WIDTH - filled)


def get_hours_map(raw: t.Optional[dict], field_name: str) -> t.Dict[str, float]:
    """Read a deliverable-keyed hours mapping, rejecting non-numeric values."""
    if not raw:
        return {}
    out = {}
    for key, value in raw.items():
        try:
            out[key] = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field_name}[{key!r}] must be a number, got {value!r}")
    return out


def build_budget(raw: t.Optional[dict]) -> Budget:
    """Build the Budget, which may carry no total at all."""
    raw = raw or {}
    total = raw.get("total_hours")
    return Budget(
        total_hours=float(total) if total is not None else None,
        source=raw.get("source", "report"),
        by_deliverable=get_hours_map(raw.get("by_deliverable"), "budget.by_deliverable"),
    )


def build_consumed(raw: t.Optional[dict]) -> Consumed:
    """Build the Consumed hours, defaulting to zero when nothing was logged."""
    raw = raw or {}
    return Consumed(
        total_hours=float(raw.get("total_hours") or 0.0),
        source=raw.get("source", "unknown"),
        by_deliverable=get_hours_map(raw.get("by_deliverable"), "consumed.by_deliverable"),
    )


def build_velocity_input(raw: t.Optional[dict]) -> VelocityInput:
    """Build the worked-day velocity figures."""
    raw = raw or {}
    worked = raw.get("worked_days")
    hours = raw.get("hours")
    return VelocityInput(
        hours=float(hours) if hours is not None else None,
        worked_days=int(worked) if worked else None,
        since=get_date(raw.get("since"), "velocity.since"),
        days_out=int(raw.get("days_out") or 0),
    )


def build_ticket(raw: dict) -> Ticket:
    """Build one live board Ticket."""
    status = raw.get("status", "not_started")
    if status not in STATUS_LABELS:
        raise ValueError(f"ticket {raw.get('key')} has unknown status {status!r}")

    return Ticket(
        key=raw["key"],
        summary=raw.get("summary", ""),
        deliverable=raw.get("deliverable", ""),
        status=status,
        estimate_hours=get_optional_float(raw.get("estimate_hours")),
        remaining_hours=get_optional_float(raw.get("remaining_hours")),
        consumed_hours=get_optional_float(raw.get("consumed_hours")),
        evidence=raw.get("evidence", ""),
    )


def get_optional_float(value: t.Any) -> t.Optional[float]:
    """Cast a value to float, preserving None for an absent figure."""
    if value is None:
        return None
    return float(value)


def build_deliverable(raw: dict) -> Deliverable:
    """Build one named Deliverable."""
    state = raw.get("state", "not_started")
    if state not in STATUS_LABELS:
        raise ValueError(f"deliverable {raw.get('key')} has unknown state {state!r}")

    percent = get_optional_float(raw.get("percent_complete"))
    if percent is not None and not raw.get("percent_complete_basis"):
        raise ValueError(
            f"deliverable {raw.get('key')} has percent_complete but no "
            "percent_complete_basis. Say what the figure is measured against."
        )

    return Deliverable(
        key=raw["key"],
        summary=raw.get("summary", ""),
        state=state,
        note=raw.get("note", ""),
        percent_complete=percent,
        percent_complete_basis=raw.get("percent_complete_basis", ""),
    )


def build_snapshot(raw: t.Optional[dict]) -> t.Optional[Snapshot]:
    """Build the prior Snapshot, or return None on the first report."""
    if not raw:
        return None
    return Snapshot(
        date=get_date(raw["date"], "prior_snapshot.date"),
        budget_hours=get_optional_float(raw.get("budget_hours")),
        consumed_hours=get_optional_float(raw.get("consumed_hours")),
        burn_percent=get_optional_float(raw.get("burn_percent")),
        board_remaining_hours=get_optional_float(raw.get("board_remaining_hours")),
    )


def build_report_input(raw: dict) -> ReportInput:
    """Build the ReportInput from the parsed input JSON."""
    epic = raw.get("epic") or {}
    if not epic.get("key"):
        raise ValueError("epic.key is required")

    return ReportInput(
        epic_key=epic["key"],
        epic_summary=epic.get("summary", ""),
        as_of=get_date(raw.get("as_of"), "as_of") or date.today(),
        due_date=get_date(epic.get("due_date"), "epic.due_date"),
        budget=build_budget(raw.get("budget")),
        consumed=build_consumed(raw.get("consumed")),
        velocity_input=build_velocity_input(raw.get("velocity")),
        board=[build_ticket(item) for item in raw.get("board", [])],
        deliverables=[build_deliverable(item) for item in raw.get("deliverables", [])],
        prior_snapshot=build_snapshot(raw.get("prior_snapshot")),
    )


def get_burn_percent(budget_hours: t.Optional[float], consumed_hours: float) -> t.Optional[float]:
    """Compute the share of a budget already spent, or None without a budget."""
    if not budget_hours:
        return None
    return consumed_hours / budget_hours * 100


def get_velocity(data: ReportInput) -> Velocity:
    """Compute hours spent per working week from worked days, never calendar days.

    Dividing by calendar days folds PTO, sick days and holidays into the rate and
    understates it. The caller supplies the days actually worked.
    """
    raw = data.velocity_input
    if not raw.hours or not raw.worked_days:
        return Velocity(per_week=None, source="no worked-day hours supplied")

    per_week = raw.hours / raw.worked_days * WORK_DAYS_PER_WEEK
    source = f"{raw.hours:g}h across the {raw.worked_days} days worked"
    if raw.since:
        source += f" since {get_short_date(raw.since)}"
    if raw.days_out:
        source += f", which excludes {raw.days_out} days out"

    return Velocity(per_week=per_week, source=source)


def get_board_remaining_hours(board: t.List[Ticket]) -> t.Optional[float]:
    """Total the remaining hours the live tickets carry, or None when none say."""
    stated = [ticket.remaining_hours for ticket in board if ticket.remaining_hours is not None]
    if not stated:
        return None
    return sum(stated)


def get_budget_remaining(budget_hours: t.Optional[float], consumed_hours: float) -> t.Optional[float]:
    """Compute the hours left in the budget, which may be negative."""
    if budget_hours is None:
        return None
    return budget_hours - consumed_hours


def get_exhaustion_date(
    as_of: date, budget_remaining: t.Optional[float], velocity: Velocity
) -> t.Optional[date]:
    """Compute the date the budget runs out at the current weekly rate."""
    if budget_remaining is None or not velocity.per_week:
        return None
    if budget_remaining <= 0:
        return as_of
    return as_of + timedelta(days=math.ceil(budget_remaining * 7 / velocity.per_week))


def get_unbudgeted_deliverables(data: ReportInput) -> t.List[str]:
    """Name the deliverables that carry no budget of their own."""
    return [d.key for d in data.deliverables if d.key not in data.budget.by_deliverable]


def get_unstarted_deliverables(data: ReportInput) -> t.List[Deliverable]:
    """Collect the deliverables that have not started."""
    return [d for d in data.deliverables if d.state == "not_started"]


def get_verdict(
    data: ReportInput,
    burn_percent: t.Optional[float],
    budget_remaining: t.Optional[float],
    velocity: Velocity,
    exhausted_on: t.Optional[date],
) -> Verdict:
    """Decide the budget call from the budget, the burn and the work not started."""
    if data.budget.total_hours is None:
        return Verdict(
            label="NO BUDGET",
            detail=(
                f"The epic carries no hours budget, so this report makes no call. "
                f"The team spent {round(data.consumed.total_hours, 1):g}h. "
                f"Set the epic budget to get a verdict."
            ),
            budget_exhausted_on=None,
        )

    if budget_remaining is not None and budget_remaining < 0:
        return Verdict(
            label="OVER BUDGET",
            detail=(
                f"The team spent {round(data.consumed.total_hours, 1):g}h against a "
                f"{data.budget.total_hours:g}h budget, which is {abs(budget_remaining):g}h over."
            ),
            budget_exhausted_on=data.as_of,
        )

    unstarted = get_unstarted_deliverables(data)
    if unstarted and burn_percent is not None and burn_percent >= BURN_WARNING_FRACTION * 100:
        names = ", ".join(d.key for d in unstarted)
        return Verdict(
            label="BUDGET AT RISK",
            detail=(
                f"The team spent {burn_percent:.0f}% of the budget and has not started {names}. "
                f"{round(budget_remaining, 1):g}h remain."
            ),
            budget_exhausted_on=exhausted_on,
        )

    return get_on_budget_verdict(data, budget_remaining, velocity, exhausted_on)


def get_on_budget_verdict(
    data: ReportInput,
    budget_remaining: t.Optional[float],
    velocity: Velocity,
    exhausted_on: t.Optional[date],
) -> Verdict:
    """Build the ON BUDGET verdict, with or without a velocity signal."""
    if not velocity.per_week or not exhausted_on:
        return Verdict(
            label="ON BUDGET",
            detail=(
                f"{round(budget_remaining, 1):g}h of the {data.budget.total_hours:g}h budget remain. "
                f"Velocity is unknown: {velocity.source}."
            ),
            budget_exhausted_on=None,
        )

    return Verdict(
        label="ON BUDGET",
        detail=(
            f"{round(budget_remaining, 1):g}h of the {data.budget.total_hours:g}h budget remain. "
            f"At {velocity.per_week:.1f}h per working week the budget runs out on "
            f"{get_short_date(exhausted_on)}."
        ),
        budget_exhausted_on=exhausted_on,
    )


def get_deliverable_state(deliverable: Deliverable, tickets: t.List[Ticket]) -> str:
    """Pick the deliverable state, letting a live ticket override a stale label."""
    states = {ticket.status for ticket in tickets}
    if not states:
        return deliverable.state
    for candidate in STATE_PRECEDENCE:
        if candidate in states:
            return candidate
    return deliverable.state


def process_deliverables(data: ReportInput) -> t.List[dict]:
    """Compute the burn figures and live tickets for every deliverable."""
    rows = []
    for deliverable in data.deliverables:
        tickets = [t_ for t_ in data.board if t_.deliverable == deliverable.key]
        budget_hours = data.budget.by_deliverable.get(deliverable.key)
        consumed_hours = data.consumed.by_deliverable.get(deliverable.key, 0.0)
        burn = get_burn_percent(budget_hours, consumed_hours)
        state = get_deliverable_state(deliverable, tickets)

        rows.append(
            {
                "key": deliverable.key,
                "summary": deliverable.summary,
                "state": state,
                "state_label": STATUS_LABELS[state],
                "note": deliverable.note,
                "budget_hours": budget_hours,
                "consumed_hours": round(consumed_hours, 1),
                "budget_remaining_hours": (
                    round(budget_hours - consumed_hours, 1) if budget_hours is not None else None
                ),
                "burn_percent": int(round(burn)) if burn is not None else None,
                "bar": get_bar(burn),
                "percent_complete": (
                    int(round(deliverable.percent_complete))
                    if deliverable.percent_complete is not None
                    else None
                ),
                "percent_complete_basis": deliverable.percent_complete_basis,
                "complete_bar": get_bar(deliverable.percent_complete),
                "burn_ahead_of_work": get_burn_gap(burn, deliverable.percent_complete),
                "board_remaining_hours": get_board_remaining_hours(tickets),
                "tickets": [process_ticket(ticket) for ticket in tickets],
            }
        )
    return rows


def process_ticket(ticket: Ticket) -> dict:
    """Render one live ticket for the output payload."""
    return {
        "key": ticket.key,
        "summary": ticket.summary,
        "status": ticket.status,
        "status_label": STATUS_LABELS[ticket.status],
        "estimate_hours": ticket.estimate_hours,
        "remaining_hours": ticket.remaining_hours,
        "consumed_hours": ticket.consumed_hours,
        "evidence": ticket.evidence,
    }


def get_burn_gap(
    burn_percent: t.Optional[float], percent_complete: t.Optional[float]
) -> t.Optional[int]:
    """Compute how far budget burn runs ahead of work done, in percentage points.

    A positive figure means the budget is going faster than the work. That gap is
    the signal burn alone cannot give, so it only exists when the caller supplied
    a completion read.
    """
    if burn_percent is None or percent_complete is None:
        return None
    return int(round(burn_percent - percent_complete))


def get_unattributed_hours(consumed: Consumed) -> float:
    """Compute the consumed hours that no deliverable claims."""
    attributed = sum(consumed.by_deliverable.values())
    return round(consumed.total_hours - attributed, 1)


def get_budget_gap(data: ReportInput) -> t.Optional[float]:
    """Compute the epic budget left unallocated across the deliverables."""
    if data.budget.total_hours is None or not data.budget.by_deliverable:
        return None
    return round(data.budget.total_hours - sum(data.budget.by_deliverable.values()), 1)


def get_trend(data: ReportInput, burn_percent: t.Optional[float]) -> dict:
    """Compare the current figures against the previous report."""
    prior = data.prior_snapshot
    if not prior:
        return {"has_prior": False, "since": None}

    out = {
        "has_prior": True,
        "since": get_short_date(prior.date),
        "since_iso": prior.date.isoformat(),
        "days": (data.as_of - prior.date).days,
    }

    if prior.consumed_hours is not None:
        out["delta_consumed_hours"] = round(data.consumed.total_hours - prior.consumed_hours, 1)
    if prior.burn_percent is not None and burn_percent is not None:
        out["delta_burn_percent"] = int(round(burn_percent - prior.burn_percent))
    if prior.budget_hours is not None and data.budget.total_hours is not None:
        out["delta_budget_hours"] = round(data.budget.total_hours - prior.budget_hours, 1)

    return out


def get_warnings(data: ReportInput, velocity: Velocity) -> t.List[str]:
    """Collect the facts the report must disclose about its own numbers."""
    warnings = []

    if data.budget.total_hours is None:
        warnings.append(
            "The epic carries no hours budget. Burn and the exhaustion date are unavailable."
        )
    elif data.budget.source == "report":
        warnings.append(
            f"The {data.budget.total_hours:g}h budget came from this report, not from Jira."
        )

    unbudgeted = get_unbudgeted_deliverables(data)
    if data.budget.by_deliverable and unbudgeted:
        warnings.append(f"No budget split for: {', '.join(unbudgeted)}.")

    gap = get_budget_gap(data)
    if gap is not None and abs(gap) >= 1:
        direction = "unallocated" if gap > 0 else "over-allocated"
        warnings.append(f"The per-deliverable split leaves {abs(gap):g}h {direction}.")

    unattributed = get_unattributed_hours(data.consumed)
    if unattributed >= 1:
        warnings.append(f"{unattributed:g}h of consumed time maps to no deliverable.")

    if not velocity.per_week:
        warnings.append(f"Velocity is unknown: {velocity.source}.")

    if not data.board:
        warnings.append("No ticket is live on the board. Nothing is in motion.")

    if not data.prior_snapshot:
        warnings.append("This is the first report on the epic. It shows no trend.")

    if data.due_date and data.due_date < data.as_of:
        days = (data.as_of - data.due_date).days
        warnings.append(f"The due date passed {days} days ago and the epic still shows it.")

    return warnings


def orchestrate_computation(data: ReportInput) -> dict:
    """Run every computation and assemble the output payload."""
    burn_percent = get_burn_percent(data.budget.total_hours, data.consumed.total_hours)
    budget_remaining = get_budget_remaining(data.budget.total_hours, data.consumed.total_hours)
    velocity = get_velocity(data)
    exhausted_on = get_exhaustion_date(data.as_of, budget_remaining, velocity)
    verdict = get_verdict(data, burn_percent, budget_remaining, velocity, exhausted_on)
    board_remaining = get_board_remaining_hours(data.board)
    trend = get_trend(data, burn_percent)

    return {
        "epic": {
            "key": data.epic_key,
            "summary": data.epic_summary,
            "due_date": data.due_date.isoformat() if data.due_date else None,
            "due_date_short": get_short_date(data.due_date) if data.due_date else None,
        },
        "as_of": data.as_of.isoformat(),
        "budget": {
            "total_hours": data.budget.total_hours,
            "source": data.budget.source,
            "consumed_hours": round(data.consumed.total_hours, 1),
            "consumed_source": data.consumed.source,
            "remaining_hours": round(budget_remaining, 1) if budget_remaining is not None else None,
            "burn_percent": int(round(burn_percent)) if burn_percent is not None else None,
            "bar": get_bar(burn_percent),
            "unallocated_hours": get_budget_gap(data),
            "unattributed_consumed_hours": get_unattributed_hours(data.consumed),
        },
        "board": {
            "live_ticket_count": len(data.board),
            "remaining_hours": round(board_remaining, 1) if board_remaining is not None else None,
            "tickets": [process_ticket(ticket) for ticket in data.board],
        },
        "velocity": {
            "per_week": round(velocity.per_week, 1) if velocity.per_week else None,
            "source": velocity.source,
            "worked_days": data.velocity_input.worked_days,
            "days_out": data.velocity_input.days_out,
        },
        "verdict": {
            "label": verdict.label,
            "detail": verdict.detail,
            "budget_exhausted_on": (
                verdict.budget_exhausted_on.isoformat() if verdict.budget_exhausted_on else None
            ),
            "budget_exhausted_on_short": (
                get_short_date(verdict.budget_exhausted_on) if verdict.budget_exhausted_on else None
            ),
        },
        "trend": trend,
        "deliverables": process_deliverables(data),
        "warnings": get_warnings(data, velocity),
        "snapshot": {
            "date": data.as_of.isoformat(),
            "budget_hours": data.budget.total_hours,
            "consumed_hours": round(data.consumed.total_hours, 1),
            "burn_percent": int(round(burn_percent)) if burn_percent is not None else None,
            "board_remaining_hours": (
                round(board_remaining, 1) if board_remaining is not None else None
            ),
        },
    }


def is_reportable(data: ReportInput) -> bool:
    """Check whether enough data exists to justify posting a report."""
    return bool(data.deliverables or data.board or data.consumed.total_hours)


def get_input_payload(path: str) -> dict:
    """Read the input JSON from a file path, or from stdin when the path is '-'."""
    if path == "-":
        return json.load(sys.stdin)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    """Parse arguments, compute the figures, and print them as JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="path to the report input JSON, or '-' for stdin")
    parser.add_argument("--snapshot-out", help="also write the snapshot line to this path")
    args = parser.parse_args()

    try:
        data = build_report_input(get_input_payload(args.input))
    except (ValueError, KeyError, json.JSONDecodeError) as err:
        print(f"bad input: {err}", file=sys.stderr)
        return EXIT_BAD_INPUT

    if not is_reportable(data):
        print(
            f"{data.epic_key} has no deliverables, no live tickets and no consumed hours. "
            "Do not post a report built on no data.",
            file=sys.stderr,
        )
        return EXIT_NO_DATA

    result = orchestrate_computation(data)

    if args.snapshot_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.snapshot_out)), exist_ok=True)
        with open(args.snapshot_out, "w", encoding="utf-8") as handle:
            json.dump(result["snapshot"], handle, separators=(",", ":"))

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
