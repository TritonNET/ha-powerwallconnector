"""Utility helpers for TritonNET Powerwall Connector."""
from __future__ import annotations
from datetime import timedelta
import re
import voluptuous as vol

from .const import DOMAIN

def sanitize_id(text: str) -> str:
    """Sanitize a string to be safe for use in unique IDs."""
    # 1. Lowercase
    text = text.lower()
    # 2. Replace spaces with underscores
    text = text.replace(" ", "_")
    # 3. Remove non-alphanumeric characters (except underscores)
    text = re.sub(r"[^a-z0-9_]", "", text)
    # 4. Remove duplicate underscores
    text = re.sub(r"_+", "_", text)
    return text.strip("_")

def get_device_identifier(sitename: str) -> str:
    """Generate the unique immutable ID for the device."""
    # Example: "Home Site" -> "pwcon_home_site"
    clean_name = sanitize_id(sitename)
    return f"pwcon_{clean_name}"

def get_device_name(sitename: str) -> str:
    """Generate the human-readable label for the device."""
    # Example: "Home Site" -> "PWCon Home Site"
    # This is what appears in the UI devices list
    return f"Powerwall Connector: {sitename}"

def get_entity_unique_id(sitename: str, suffix: str) -> str:
    """Generate a unique ID for a specific entity."""
    # Example: "home_site_version"
    return f"{sanitize_id(sitename)}_{sanitize_id(suffix)}"

def custom_time_period(value):
    if isinstance(value, int):
        return timedelta(seconds=value)
    value = str(value).lower()
    match = re.match(r"^(\d+)(s|m|h)$", value)
    if not match:
        raise vol.Invalid(f"Invalid format '{value}'.")
    count = int(match.group(1))
    unit = match.group(2)
    if unit == "s": return timedelta(seconds=count)
    if unit == "m": return timedelta(minutes=count)
    if unit == "h": return timedelta(hours=count)
    raise vol.Invalid("Invalid time unit.")