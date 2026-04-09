# Clockify SDK — Utilities

```python
from ClockifySdk import clockify_utils
```

---

## Date / Time Encoding

Clockify's API expects ISO 8601 UTC strings: `"YYYY-MM-DDTHH:MM:SSZ"`

### `encode_clockify_datestr(datetime_obj: datetime) -> str`

Converts a Python `datetime` to the Clockify-expected ISO string.

```python
from datetime import datetime
from ClockifySdk import clockify_utils

dt = datetime(2024, 1, 15, 9, 0, 0)
s = clockify_utils.encode_clockify_datestr(dt)
# → "2024-01-15T09:00:00Z"
```

### `decode_clockify_datestr(datestr: str) -> datetime`

Parses a Clockify ISO string back into a Python `datetime`.

```python
dt = clockify_utils.decode_clockify_datestr("2024-01-15T09:00:00Z")
# → datetime(2024, 1, 15, 9, 0, 0)
```

### `get_todays_date() -> date`

Returns today's `date` object.

```python
today = clockify_utils.get_todays_date()
```

---

## Date Range Checks

### `date_in_range(date, days: int, dir: str | None) -> bool`

Returns `True` if `date` falls within `days` days in the given direction.

- `dir="past"` — checks if date is within the past N days
- `dir="future"` — checks if date is within the next N days
- `dir=None` — checks both directions

```python
from datetime import date

today = date.today()
is_recent = clockify_utils.date_in_range(today, days=7, dir="past")
# → True (today is within the past 7 days)
```

### `date_outof_range(date, days: int, dir: str | None) -> bool`

Inverse of `date_in_range`. Returns `True` if the date is **outside** the range.

```python
old_date = date(2020, 1, 1)
is_stale = clockify_utils.date_outof_range(old_date, days=30, dir="past")
# → True
```

---

## Repeating Event Decoding

### `decode_days(description: str) -> List[int] | None`

Parses a `REP[<days>]` tag from a time entry description. Returns a list of
weekday integers (0=Monday … 4=Friday), or `None` if no `REP` tag is present.

**Day codes:**

| Code | Weekday | Integer |
|------|---------|---------|
| M    | Monday  | 0 |
| T    | Tuesday | 1 |
| W    | Wednesday | 2 |
| R    | Thursday | 3 |
| F    | Friday  | 4 |

```python
clockify_utils.decode_days("Daily standup REP[MTWRF]")
# → [0, 1, 2, 3, 4]

clockify_utils.decode_days("Team sync REP[TR]")
# → [1, 3]

clockify_utils.decode_days("One-off meeting")
# → None
```

**Usage — check if today should have a repeated entry:**

```python
from datetime import date
from ClockifySdk import clockify_utils

today_weekday = date.today().weekday()  # 0=Mon, 6=Sun

repeat_days = clockify_utils.decode_days(entry.description)
if repeat_days and today_weekday in repeat_days:
    # This entry should repeat today
    ...
```
