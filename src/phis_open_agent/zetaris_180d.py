"""Bounded Zetaris readback for the fictional six-variable scientific case.

The production path uses ZetarisClient's real REST transport. A test transport
can be injected, but its result is always marked SIMULATED.
"""

from __future__ import annotations

from .scenario_contract_180d import DATASET_ID, ObservationRejected, canonical_digest, normalize_observations
from .zetaris import ZetarisBlocked, ZetarisClient


DATABASE = "PHIS_SYNTHETIC_180D"
TABLE = "observations"
COLUMNS = (
    "schema_version", "dataset_id", "participant_id", "local_date", "variable",
    "value", "unit", "source_type", "source_record_id", "observed", "quality", "synthetic",
)
PAGE_SIZE = 200
MAX_PAGES = 6
EXPECTED_PAGE_SIZES = (200, 200, 200, 200, 200, 80)


def page_sql(offset):
    if type(offset) is not int or offset < 0 or offset % PAGE_SIZE:
        raise ValueError("Invalid bounded page offset")
    return ("SELECT " + ", ".join(COLUMNS) + f" FROM {DATABASE}.{TABLE} "
            f"WHERE dataset_id = '{DATASET_ID}' AND participant_id = 'fictional-opportunity' "
            f"ORDER BY local_date, variable LIMIT {PAGE_SIZE} OFFSET {offset}")


def registration_sql(server_path):
    """Register a server-visible synthetic CSV through documented SQL only."""
    if (not isinstance(server_path, str) or not server_path.startswith("/")
            or any(char in server_path for char in ('"', "'", "\n", "\r", ";", "\\"))):
        raise ValueError("Provide a safe absolute server-visible CSV path")
    return (
        f'CREATE LIGHTNING DATABASE {DATABASE} DESCRIBE BY "Fictional PHIS 180-day case"',
        f'CREATE LIGHTNING FILESTORE TABLE {TABLE} FROM {DATABASE} FORMAT CSV '
        f'OPTIONS (PATH "{server_path}", header "true", inferSchema "true")',
    )


def read_verified_180d(client: ZetarisClient):
    if not isinstance(client, ZetarisClient) or not client._preflight_passed:
        raise ZetarisBlocked("Verified Zetaris preflight required")
    raw_rows = []
    traces = []
    for page in range(MAX_PAGES):
        page_rows, trace = client.query(page_sql(page * PAGE_SIZE), limit=PAGE_SIZE)
        if len(page_rows) != EXPECTED_PAGE_SIZES[page]:
            raise ZetarisBlocked("Zetaris 180-day page size disagrees with the frozen source contract")
        trace = {**trace, "page": page, "offset": page * PAGE_SIZE}
        traces.append(trace)
        for values in page_rows:
            if not isinstance(values, list) or len(values) != len(COLUMNS):
                raise ZetarisBlocked("Zetaris returned a malformed observation row")
            raw_rows.append(dict(zip(COLUMNS, values)))
    if (len({trace["request_id"] for trace in traces}) != MAX_PAGES or
            len({trace["query_id"] for trace in traces}) != MAX_PAGES):
        raise ZetarisBlocked("Zetaris source query IDs are not unique")
    try:
        rows = normalize_observations(raw_rows)
        digest = canonical_digest(rows)
    except ObservationRejected as exc:
        raise ZetarisBlocked("Zetaris 180-day source failed scientific schema verification") from exc
    ids = [row["source_record_id"] for row in rows]
    return {
        "status": "VERIFIED" if client.is_live_transport else "SIMULATED",
        "mode": "LIVE_SYNTHETIC_ZETARIS" if client.is_live_transport else "SYNTHETIC_LOCAL_ONLY",
        "rows": rows, "source_record_ids": ids, "record_digest_sha256": digest,
        "pages": traces, "source_count": len(ids),
        "sponsor_proof": {
            "sponsor": "zetaris", "status": "VERIFIED" if client.is_live_transport else "NOT_CONNECTED",
            "trace_id": traces[0]["request_id"] if client.is_live_transport else None,
            "request_ids": [trace["request_id"] for trace in traces] if client.is_live_transport else [],
            "query_ids": [trace["query_id"] for trace in traces] if client.is_live_transport else [],
        },
    }
