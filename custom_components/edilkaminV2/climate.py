"""Platform for climate integration."""
from __future__ import annotations

import logging
from homeassistant.components.climate import (
    ClimateEntity,
    HVACMode,
    ClimateEntityFeature,
)

from homeassistant.const import TEMP_CELSIUS, ATTR_TEMPERATURE

from .const import DOMAIN
from custom_components.edilkaminv2.api.edilkamin_async_api import (
    EdilkaminAsyncApi,
    HttpException,
)

_LOGGER = logging.getLogger(__name__)

CLIMATE_HVAC_MODE_MANAGED = [HVACMode.HEAT, HVACMode.OFF]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""

    async_api = hass.data[DOMAIN][config_entry.entry_id]

    async_add_devices([EdilkaminClimateEntity(async_api)])


class EdilkaminClimateEntity(ClimateEntity):
    """Representation of a Climate."""

    def __init__(self, api: EdilkaminAsyncApi):
        """Initialize the climate."""
        self._state = None
        self._current_temperature = None
        self._target_temperature = None
        self._fan1_speed = None
        self._power_level = None
        self._hvac_mode = None
        self._preset_mode = None
        self.api = api
        self.mac_address = api.get_mac_address()
        self._attr_max_temp = 24
        self._attr_min_temp = 14

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_climate"

    @property
    def temperature_unit(self):
        """The unit of temperature measurement"""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """The current temperature."""
        return self._current_temperature

    @property
    def hvac_mode(self) -> HVACMode :
        """The current operation ."""
        return self._hvac_mode

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """List of available operation modes."""
        return CLIMATE_HVAC_MODE_MANAGED

    @property
    def fan_mode(self):
        """Returns the current fan mode.."""
        return self._fan1_speed

    @property
    def fan_modes(self):
        """List of available fan modes."""
        return ["1", "2", "3", "4", "5"]

    @property
    def preset_mode(self) :
        """The current operation ."""
        return self._preset_mode

    @property
    def preset_modes(self) :
        """list of power level."""
        return ["1", "2", "3", "4", "5"]

    @property
    def target_temperature(self):
        """The current temperature."""
        return self._target_temperature

    @property
    def supported_features(self):
        """Bitmap of supported features"""
        return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE | ClimateEntityFeature.PRESET_MODE

    async def async_set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        try:
            await self.api.set_fan_1_speed(int(fan_mode))
        except HttpException as err:
            _LOGGER.error(str(err))
            return
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            target_tmp = kwargs.get(ATTR_TEMPERATURE)
            await self.api.set_temperature(target_tmp)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            self._current_temperature = await self.api.get_temperature()
            self._target_temperature = await self.api.get_target_temperature()
            self._fan1_speed = str(await self.api.get_fan_1_speed_settings())
            self._power_level = await self.api.get_power_level_settings()
            self._preset_mode = str(self._power_level)
        
            power = await self.api.get_power_status()
            if power is True:
                self._hvac_mode = HVACMode.HEAT
            else:
                self._hvac_mode = HVACMode.OFF
        except HttpException as err:
            _LOGGER.error(str(err))
            return

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        
        _LOGGER.info("Setting operation mode to %s", hvac_mode)
        
        if hvac_mode not in CLIMATE_HVAC_MODE_MANAGED:
            raise ValueError(f"Unsupported HVAC mode: {hvac_mode}")

        if hvac_mode == HVACMode.OFF:
            return await self.async_turn_off()
        if hvac_mode == HVACMode.HEAT :
            return await self.async_turn_on()
        _LOGGER.error(hvac_mode)
        self.async_write_ha_state()

 
    async def async_set_preset_mode(self, preset_mode):
        """Set new preset mode."""
        if preset_mode not in ["1", "2", "3", "4", "5"]:
            raise ValueError(f"Unsupported preset mode: {preset_mode}")
        
        try:
            await self.async_set_power(preset_mode)
        except HttpException as err:
            _LOGGER.error(str(err))
            return
        
        self.async_write_ha_state()
        
    async def async_turn_on(self):
        """Turn on."""
        _LOGGER.debug("Turning %s on", self.unique_id)
        
        try:
            await self.api.enable_power()
        except HttpException as err:
            _LOGGER.error(str(err))
            return


    async def async_turn_off(self):
        """Turn off."""
        _LOGGER.debug("Turning %s off", self.unique_id)
        try:
            await self.api.disable_power()
        except HttpException as err:
            _LOGGER.error(str(err))
            return
        
        self.async_write_ha_state()


    async def async_set_power(self, power_level):
        """Turn off."""
        _LOGGER.debug("set power level %s", power_level)
        try:
            await self.api.set_power_level(int(power_level))
        except HttpException as err:
            _LOGGER.error(str(err))
            return
        
