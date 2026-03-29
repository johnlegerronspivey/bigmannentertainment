"""
Catalog CSV Import Service
===========================
Handles parsing, validating, and bulk-inserting catalog assets from CSV uploads.
"""

import csv
import io
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

from config.database import db

logger = logging.getLogger(__name__)

VALID_TYPES = {"single", "album", "ep", "compilation", "mixtape"}
VALID_STATUSES = {"draft", "pre-release", "released", "taken_down"}

REQUIRED_COLUMNS = {"title"}
OPTIONAL_COLUMNS = {"type", "artist", "isrc", "upc", "release_date", "genre", "status", "platforms", "streams_total"}
ALL_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS

CSV_TEMPLATE_HEADER = ["title", "type", "artist", "isrc", "upc", "release_date", "genre", "status", "platforms", "streams_total"]
CSV_TEMPLATE_EXAMPLE = [
    ["My First Track", "single", "Artist Name", "USRC12345678", "012345678901", "2026-03-15", "Hip-Hop", "draft", "Spotify;Apple Music", "0"],
    ["Summer Album", "album", "Artist Name", "USRC12345679", "012345678902", "2026-06-01", "R&B", "pre-release", "Spotify;Tidal;YouTube Music", "0"],
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"


def generate_csv_template() -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_TEMPLATE_HEADER)
    for row in CSV_TEMPLATE_EXAMPLE:
        writer.writerow(row)
    return output.getvalue()


def _validate_row(row: Dict[str, str], row_num: int) -> tuple:
    """Validate a single CSV row. Returns (asset_dict | None, error_msg | None)."""
    errors = []

    title = row.get("title", "").strip()
    if not title:
        errors.append("title is required")

    asset_type = row.get("type", "single").strip().lower()
    if asset_type and asset_type not in VALID_TYPES:
        errors.append(f"invalid type '{asset_type}' (valid: {', '.join(sorted(VALID_TYPES))})")
        asset_type = "single"

    status = row.get("status", "draft").strip().lower()
    if status and status not in VALID_STATUSES:
        errors.append(f"invalid status '{status}' (valid: {', '.join(sorted(VALID_STATUSES))})")
        status = "draft"

    platforms_raw = row.get("platforms", "").strip()
    platforms = [p.strip() for p in platforms_raw.split(";") if p.strip()] if platforms_raw else []

    streams_raw = row.get("streams_total", "0").strip()
    try:
        streams_total = int(streams_raw) if streams_raw else 0
    except ValueError:
        errors.append(f"streams_total must be a number, got '{streams_raw}'")
        streams_total = 0

    if errors:
        return None, f"Row {row_num}: " + "; ".join(errors)

    asset = {
        "title": title,
        "type": asset_type or "single",
        "artist": row.get("artist", "").strip(),
        "isrc": row.get("isrc", "").strip(),
        "upc": row.get("upc", "").strip(),
        "release_date": row.get("release_date", "").strip(),
        "genre": row.get("genre", "").strip(),
        "status": status or "draft",
        "platforms": platforms,
        "streams_total": streams_total,
    }
    return asset, None


async def parse_and_import_csv(
    label_id: str,
    csv_content: str,
    user_id: str,
    skip_duplicates: bool = True,
) -> Dict[str, Any]:
    """Parse CSV content and bulk-import assets into label_assets collection."""

    # Verify label exists
    label = await db.uln_labels.find_one(
        {"global_id.id": label_id},
        {"_id": 0, "global_id": 1, "metadata_profile.name": 1},
    )
    if not label:
        return {"success": False, "error": "Label not found"}

    label_name = label.get("metadata_profile", {}).get("name", "Unknown")

    # Parse CSV
    try:
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)
    except Exception as e:
        return {"success": False, "error": f"Failed to parse CSV: {str(e)}"}

    if not rows:
        return {"success": False, "error": "CSV file is empty (no data rows found)"}

    # Check headers
    headers = set(reader.fieldnames or [])
    normalized_headers = {h.strip().lower().replace(" ", "_") for h in headers}
    if "title" not in normalized_headers:
        return {"success": False, "error": "CSV must contain a 'title' column header"}

    # Normalize row keys
    normalized_rows = []
    for row in rows:
        normalized = {k.strip().lower().replace(" ", "_"): v for k, v in row.items()}
        normalized_rows.append(normalized)

    # Get existing ISRCs/UPCs for duplicate detection
    existing_isrcs = set()
    existing_upcs = set()
    if skip_duplicates:
        async for doc in db.label_assets.find({"label_id": label_id}, {"_id": 0, "isrc": 1, "upc": 1}):
            if doc.get("isrc"):
                existing_isrcs.add(doc["isrc"].strip().upper())
            if doc.get("upc"):
                existing_upcs.add(doc["upc"].strip())

    now = _now_iso()
    imported = []
    skipped = []
    errors = []

    for idx, row in enumerate(normalized_rows, start=2):  # Row 2 = first data row after header
        asset_data, error = _validate_row(row, idx)
        if error:
            errors.append({"row": idx, "error": error})
            continue

        # Duplicate check
        if skip_duplicates:
            isrc = asset_data.get("isrc", "").strip().upper()
            upc = asset_data.get("upc", "").strip()
            if isrc and isrc in existing_isrcs:
                skipped.append({"row": idx, "title": asset_data["title"], "reason": f"Duplicate ISRC: {isrc}"})
                continue
            if upc and upc in existing_upcs:
                skipped.append({"row": idx, "title": asset_data["title"], "reason": f"Duplicate UPC: {upc}"})
                continue
            # Track for intra-file duplicates
            if isrc:
                existing_isrcs.add(isrc)
            if upc:
                existing_upcs.add(upc)

        asset_id = _gen_id("ASSET")
        asset_doc = {
            "asset_id": asset_id,
            "label_id": label_id,
            **asset_data,
            "created_by": user_id,
            "created_at": now,
            "updated_at": now,
            "import_source": "csv",
        }
        imported.append(asset_doc)

    # Bulk insert
    inserted_count = 0
    if imported:
        result = await db.label_assets.insert_many(imported)
        inserted_count = len(result.inserted_ids)

    # Audit trail
    await db.uln_audit_trail.insert_one({
        "action_type": "catalog_csv_import",
        "actor_id": user_id,
        "resource_type": "label",
        "resource_id": label_id,
        "description": f"CSV import: {inserted_count} assets imported, {len(skipped)} skipped, {len(errors)} errors",
        "changes": {
            "imported_count": inserted_count,
            "skipped_count": len(skipped),
            "error_count": len(errors),
        },
        "timestamp": now,
    })

    # Build safe response (no _id fields)
    imported_summary = [
        {"asset_id": a["asset_id"], "title": a["title"], "type": a["type"], "artist": a["artist"]}
        for a in imported
    ]

    return {
        "success": True,
        "label_id": label_id,
        "label_name": label_name,
        "total_rows": len(normalized_rows),
        "imported_count": inserted_count,
        "skipped_count": len(skipped),
        "error_count": len(errors),
        "imported": imported_summary,
        "skipped": skipped,
        "errors": errors,
    }


async def preview_csv(csv_content: str) -> Dict[str, Any]:
    """Parse and preview CSV content without importing."""
    try:
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)
    except Exception as e:
        return {"success": False, "error": f"Failed to parse CSV: {str(e)}"}

    if not rows:
        return {"success": False, "error": "CSV file is empty"}

    headers = list(reader.fieldnames or [])
    normalized_headers = [h.strip().lower().replace(" ", "_") for h in headers]

    if "title" not in normalized_headers:
        return {"success": False, "error": "CSV must contain a 'title' column header"}

    preview_rows = []
    validation_errors = []
    for idx, row in enumerate(rows[:50], start=2):  # Preview max 50 rows
        normalized = {k.strip().lower().replace(" ", "_"): v for k, v in row.items()}
        asset_data, error = _validate_row(normalized, idx)
        if error:
            validation_errors.append({"row": idx, "error": error})
            preview_rows.append({**normalized, "_has_error": True, "_error": error})
        else:
            preview_rows.append({**asset_data, "_has_error": False})

    return {
        "success": True,
        "headers": normalized_headers,
        "total_rows": len(rows),
        "preview_rows": preview_rows[:50],
        "validation_errors": validation_errors,
        "valid_count": len(rows) - len(validation_errors),
    }
