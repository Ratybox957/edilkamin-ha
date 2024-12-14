"""Platform for fan integration."""
from __future__ import annotations

import logging
import math

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.components.fan import FanEntity, FanEntityFeature 
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import DOMAIN
from custom_components.edilkaminv2.api.edilkamin_async_api import EdilkaminAsyncApi, HttpException

_LOGGER = logging.getLogger(__name__)

POWER_RANGE = (1, 5)  # away is not included in speeds and instead mapped to off
SPEED_RANGE = (1, 5)  # off is not included in speeds and instead mapped to off
SPEED_RANGE_FAN2 = (1, 5)  # off is not included in speeds and instead mapped to off


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    async_api = hass.data[DOMAIN][config_entry.entry_id]

    async_add_devices([EdilkaminPowerLevel(async_api)])
    async_add_devices([EdilkaminFan(async_api)])
    async_add_devices([EdilkaminFan2(async_api)])


class EdilkaminFan(FanEntity):
    """Representation of a Fan."""

    def __init__(self, api: EdilkaminAsyncApi):
        """Initialize the fan."""
        self.api = api
        self.mac_address = api.get_mac_address()

        self.current_speed = None
        self.current_state = False
        
        

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_fan1"


    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if self.current_state is False:
            return None

        if self.current_speed is None:
            return None
        return ranged_value_to_percentage(SPEED_RANGE, self.current_speed)

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(SPEED_RANGE)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return FanEntityFeature.SET_SPEED

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        self.current_speed = math.ceil(
            percentage_to_ranged_value(SPEED_RANGE, percentage)
        )

        await self.api.set_fan_1_speed(self.current_speed)
        self.schedule_update_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            self.current_state = await self.api.get_fan_1_is_active()
            if self.current_state is True:
                self.current_speed = await self.api.get_fan_1_actual_setpoint()
        except HttpException as err:
            _LOGGER.error(str(err))
            return

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


class EdilkaminFan2(FanEntity):
    """Representation of a Fan."""


    def __init__(self, api: EdilkaminAsyncApi):
        """Initialize the fan."""
        self.api = api
        self.mac_address = api.get_mac_address()

        self.current_speed = None
        self.current_state = False
        self.preset_mode = None
        self._percentage = 0
        #self.is_on = False

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_fan2"

    @property
    def preset_modes(self):
        """Return preset modes."""
        return [ "0", "1", "2", "3", "4", "5"]

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        if self.current_state is False:
            return None

        if self.current_speed is None or self.current_speed == 0 :
            return 0
        
        return ranged_value_to_percentage(SPEED_RANGE_FAN2, self.current_speed) #self.current_speed * 100 / 5 

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(SPEED_RANGE_FAN2)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return FanEntityFeature.SET_SPEED|FanEntityFeature.TURN_OFF|FanEntityFeature.PRESET_MODE

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        self.current_speed = math.ceil(
            #percentage * 5 / 100
            percentage_to_ranged_value(SPEED_RANGE_FAN2, percentage)
        )
        if self.current_speed == 0:
            #self.preset_mode = None
            self.preset_mode = "0"
            
        await self.api.set_fan_2_speed(self.current_speed)
        self.schedule_update_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        self.current_speed = int(preset_mode)
        
                
        if preset_mode == "0":
            self.current_state = False
            #self.preset_mode = None
            self.preset_mode = str(preset_mode)
            self.current_speed = 0
            self._percentage = 0
            #self.is_on = False
        else :
            self.preset_mode = str(preset_mode)
            self._percentage = ranged_value_to_percentage(SPEED_RANGE_FAN2, self.current_speed)
        
        
        await self.api.set_fan_2_speed(self.current_speed)
        self.schedule_update_ha_state()
        

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            self.current_state = await self.api.get_fan_2_is_active()
            self.current_speed = await self.api.get_fan_2_actual_setpoint()
            temp_preset_mode = str(self.current_speed)
            
            
            if temp_preset_mode == "0":
                #self.preset_mode = None
                self.preset_mode =  temp_preset_mode

                self._percentage = 0
            else :
                self.preset_mode = temp_preset_mode
                self._percentage = ranged_value_to_percentage(SPEED_RANGE_FAN2, self.current_speed)
                
            if self.current_state is True or self.current_state == "true":
                self.current_state = False
                #self.is_on = True
            else :
                self.current_state = False
                
                #self.is_on = False
        except HttpException as err:
            _LOGGER.error(str(err))
            return

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
        await self.api.set_fan_2_speed(0)
        self.current_state = False
        #self.is_on = False
        self.preset_mode = "0"
        
        self.schedule_update_ha_state()


class EdilkaminPowerLevel(FanEntity):
    """Representation of a Fan."""

    def __init__(self, api: EdilkaminAsyncApi):
        """Initialize the fan."""
        self.api = api
        self.mac_address = api.get_mac_address()

        self.current_speed = None
        self.current_state = False

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_power_level_1"


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

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            self.current_state = await self.api.get_power_status()
            if self.current_state is True:
                self.current_speed = await self.api.get_actual_power()
        except HttpException as err:
            _LOGGER.error(str(err))
            return

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
