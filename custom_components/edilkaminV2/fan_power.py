"""Platform for fan integration."""
from __future__ import annotations

import logging
import math

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.components.fan import SUPPORT_SET_SPEED, FanEntity, FanEntityFeature
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import DOMAIN
from custom_components.edilkaminv2.api.edilkamin_async_api import EdilkaminAsyncApi
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

POWER_RANGE = (1, 5)  # away is not included in speeds and instead mapped to off


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_api = hass.data[DOMAIN][config_entry.entry_id]

    async_add_devices([EdilkaminPowerLevel(async_api, coordinator)])


class EdilkaminPowerLevel(CoordinatorEntity, FanEntity):
    """Representation of a Fan."""

    def __init__(self, api: EdilkaminAsyncApi, coordinator) -> None:
        """Initialize the fan."""
        super().__init__(coordinator)
        self.api = api
        self._mac_address = self.coordinator.get_mac_address()

        self.current_speed = None
        self.current_state = False
        self._attr_name = "Power"
        self._attr_device_info = {"identifiers": {("edilkaminv2", self._mac_address)}}

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self._mac_address}_power_level_1"


    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if self.current_state is False:
            return None

        if self.current_speed is None:
            return None
        return ranged_value_to_percentage(POWER_RANGE, self.current_speed)

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(POWER_RANGE)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return FanEntityFeature.SET_SPEED

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        self.current_speed = math.ceil(
            percentage_to_ranged_value(POWER_RANGE, percentage)
        )

        await self.api.set_power_level(self.current_speed)
        self.schedule_update_ha_state()

    def _handle_coordinator_update(self) -> None:   
        """Fetch new state data for the sensor."""
        self.current_state = self.coordinator.get_power_status()
        if self.current_state is True:
            self.current_speed = self.coordinator.get_actual_power()

        self.async_write_ha_state() 


    async def async_turn_on(
            self,
            speed: str = None,
            percentage: int = None,
            preset_mode: str = None,
            **kwargs,
    ) -> None:
        """Turn on the entity."""

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the entity."""
