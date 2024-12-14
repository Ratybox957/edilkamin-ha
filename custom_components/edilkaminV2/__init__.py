"""The Edilkamin integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
##from homeassistant.helpers.aiohttp_client import async_get_clientsession

##from .const import DOMAIN, MAC_ADDRESS, REFRESH_TOKEN, CLIENT_ID
from .const import DOMAIN, MAC_ADDRESS, PASSWORD, USERNAME#
from custom_components.edilkaminv2.api.edilkamin_async_api import (
    EdilkaminAsyncApi,
)

##_LOGGER = logging.getLogger(__name__)

##PLATFORMS: list[str] = ["sensor", "binary_sensor", "switch", "fan", "climate"]
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH, Platform.FAN, Platform.CLIMATE]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Edilkamin from a config entry."""
    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data[MAC_ADDRESS]

    mac_address = entry.data[MAC_ADDRESS]
    username = entry.data[USERNAME]
    password = entry.data[PASSWORD]
    ##refresh_token = entry.data[REFRESH_TOKEN]
    ##client_id = entry.data[CLIENT_ID]

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = EdilkaminAsyncApi(
        mac_address=mac_address,
        username=username,
        password=password,
        hass=hass
        ##session=async_get_clientsession(hass),
        ##refresh_token=refresh_token,
        ##client_id=client_id,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
