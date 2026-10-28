"""Read-only tool for retrieving one day's calendar events."""

from datetime import date as Date
import json
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_calendar_day",
        "description": (
            "Read the appointments for one calendar day from the configured "
            "read-only calendar data endpoint. Use this tool to answer questions "
            "about the user's calendar. A no_data result means no calendar file "
            "exists for that date."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Calendar date in YYYY-MM-DD format.",
                    "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
                }
            },
            "required": ["date"],
            "additionalProperties": False,
        },
    },
}


def get_calendar_day(date: str, data_base_url: str) -> dict[str, Any]:
    """Fetch one day's calendar JSON with HTTP GET; never writes to the data source."""
    try:
        normalized_date = Date.fromisoformat(date).isoformat()
    except (TypeError, ValueError) as exc:
        raise ValueError("date must be a real date in YYYY-MM-DD format") from exc
    if normalized_date != date:
        raise ValueError("date must use YYYY-MM-DD format")

    url = f"{data_base_url.rstrip('/')}/calendar/{normalized_date}.json"
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "agentic-interaction-ws2627",
        },
    )
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.load(response)
    except HTTPError as exc:
        if exc.code == 404:
            return {
                "date": normalized_date,
                "events": [],
                "status": "no_data",
            }
        raise

    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise ValueError("calendar endpoint returned an unexpected JSON structure")

    return {
        "date": payload.get("date", normalized_date),
        "events": payload["events"],
        "status": "ok",
    }
