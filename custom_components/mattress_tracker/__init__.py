"""The Mattress Tracker integration."""
from __future__ import annotations

import logging
from datetime import date

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_MATTRESS_NAME,
    CONF_SIDE_1_NAME,
    CONF_SIDE_2_NAME,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "button"]

SERVICE_FLIP = "flip"
SERVICE_ROTATE = "rotate"

ATTR_DATE = "date"

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Optional(ATTR_DATE): cv.date,
    }
)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Mattress Tracker component."""
    hass.data.setdefault(DOMAIN, {})

    async def get_entry_id_from_entity(entity_id: str) -> str | None:
        registry = er.async_get(hass)
        entity_entry = registry.async_get(entity_id)
        if entity_entry:
            return entity_entry.config_entry_id
        return None

    async def handle_flip(call: ServiceCall):
        """Handle the flip service call."""
        entity_id = call.data["entity_id"]
        flip_date = call.data.get(ATTR_DATE, date.today()).isoformat()

        entry_id = await get_entry_id_from_entity(entity_id)
        if entry_id and entry_id in hass.data[DOMAIN]:
            entities = hass.data[DOMAIN][entry_id].get("entities", {})
            if "side" in entities and "flipped" in entities:
                entities["side"].toggle_side()
                entities["flipped"].set_date(flip_date)

    async def handle_rotate(call: ServiceCall):
        """Handle the rotate service call."""
        entity_id = call.data["entity_id"]
        rotate_date = call.data.get(ATTR_DATE, date.today()).isoformat()

        entry_id = await get_entry_id_from_entity(entity_id)
        if entry_id and entry_id in hass.data[DOMAIN]:
            entities = hass.data[DOMAIN][entry_id].get("entities", {})
            if "rotation" in entities and "rotated" in entities:
                entities["rotation"].toggle_rotation()
                entities["rotated"].set_date(rotate_date)

    hass.services.async_register(DOMAIN, SERVICE_FLIP, handle_flip, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_ROTATE, handle_rotate, schema=SERVICE_SCHEMA)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mattress Tracker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = {
        "entities": {},
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
