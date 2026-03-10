"""Permit fetcher dispatcher — routes to city-specific fetchers."""

from backend.tools.permits.chicago import fetch_chicago_permits

CITY_FETCHERS = {
    "chicago": fetch_chicago_permits,
}


def fetch_permits(city: str, **kwargs) -> list[dict]:
    """Fetch permits for a given city.

    Args:
        city: City name (e.g. "chicago").
        **kwargs: Passed to the city-specific fetcher.

    Returns:
        List of raw permit dicts.

    Raises:
        ValueError: If no fetcher exists for the city.
    """
    fetcher = CITY_FETCHERS.get(city.lower())
    if not fetcher:
        raise ValueError(
            f"No permit fetcher for city '{city}'. "
            f"Available: {list(CITY_FETCHERS.keys())}"
        )
    return fetcher(**kwargs)


def available_cities() -> list[str]:
    """Return list of cities with available permit fetchers."""
    return list(CITY_FETCHERS.keys())
