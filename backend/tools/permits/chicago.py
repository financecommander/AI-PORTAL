"""Chicago building permit fetcher via Socrata SODA API."""

import logging
from typing import Optional

import requests

from backend.config.settings import settings

logger = logging.getLogger(__name__)

CHICAGO_PERMITS_URL = "https://data.cityofchicago.org/resource/ydr8-5enu.json"


def fetch_chicago_permits(
    limit: int = 100,
    offset: int = 0,
    where: Optional[str] = None,
    order: str = "issue_date DESC",
) -> list[dict]:
    """Fetch building permits from Chicago Data Portal via SODA API.

    Args:
        limit: Max records per request (max 50000).
        offset: Pagination offset.
        where: SoQL WHERE clause, e.g. "issue_date > '2024-01-01'".
        order: SoQL ORDER BY clause.

    Returns:
        List of raw permit dicts from the API.
    """
    params = {
        "$limit": limit,
        "$offset": offset,
        "$order": order,
    }
    if where:
        params["$where"] = where

    headers = {}
    app_token = getattr(settings, "socrata_app_token", "")
    if app_token:
        headers["X-App-Token"] = app_token

    try:
        response = requests.get(
            CHICAGO_PERMITS_URL,
            params=params,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        logger.info("Fetched %d Chicago permits (offset=%d)", len(data), offset)
        return data
    except requests.RequestException as e:
        logger.error("Chicago permits fetch failed: %s", e)
        return []
