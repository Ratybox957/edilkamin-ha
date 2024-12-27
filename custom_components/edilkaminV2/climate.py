"""Platform for climate integration."""
from __future__ import annotations

import logging
from homeassistant.components.climate import (
    ClimateEntity,
    HVACMode,
    ClimateEntityFeature,
)
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE

from .const import DOMAIN
from custom_components.edilkaminv2.api.edilkamin_async_api import (
    EdilkaminAsyncApi,
    HttpException,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

CLIMATE_HVAC_MODE_MANAGED = [HVACMode.HEAT, HVACMode.OFF]
FAN_MODES_MANAGED = ["1", "2", "3", "4", "5"]

async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_api = hass.data[DOMAIN][config_entry.entry_id]

    async_add_devices([EdilkaminClimateEntity(async_api, coordinator)])


class EdilkaminClimateEntity(CoordinatorEntity, ClimateEntity):
    """Representation of a Climate."""

    def __init__(self, api: EdilkaminAsyncApi, coordinator) -> None:
        """Initialize the climate."""
        super().__init__(coordinator)
        self._state = None
        self._attr_current_temperature  = None
        self._attr_target_temperature = None
        self._attr_fan1_speed = None
        self._attr_fan1_modes = FAN_MODES_MANAGED
        # self._attr_fan_mode = "1"  # default fan speed
        self._attr_fan2_speed = None
        self._attr_preset_mode = None
        self._attr_hvac_mode = HVACMode.OFF  # default hvac mode
        self.api = api
        self._mac_address = self.coordinator.get_mac_address()
        self._attr_max_temp = 24
        self._attr_min_temp = 14
        
        self._attr_name = "Edilkamin climate"
        self._attr_device_info = {"identifiers": {("edilkaminv2", self._mac_address)}}

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self._mac_address}_climate"

    @property
    def temperature_unit(self):
        """The unit of temperature measurement"""
        return UnitOfTemperature.CELSIUS

    # @property
    # def current_temperature(self):
    #     """The current temperature."""
    #     return self._attr_current_temperature 

    # @property
    # def hvac_mode(self) -> HVACMode :
    #     """The current operation ."""
    #     return self._attr_hvac_mode

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """List of available operation modes."""
        return CLIMATE_HVAC_MODE_MANAGED
    
    @property
    def preset_mode(self):
        """Return preset modes."""
        return self._attr_preset_mode


    @property
    def preset_modes(self):
        """list preset modes."""
        return ["1", "2", "3", "4", "5"]

    @property
    def fan_mode(self):
        """Returns the current fan mode.."""
        return str(self._attr_fan1_speed)

    @property
    def fan_modes(self):
        """List of available fan modes."""
        return ["1", "2", "3", "4", "5"]
    @property
    def fan2_mode(self):
        """Returns the current fan mode.."""
        return self._attr_fan2_speed

    @property
    def fan2_modes(self):
        """List of available fan modes."""
        return ["0", "1", "2", "3", "4", "5"]
    # @property
    # def target_temperature(self):
    #     """The current temperature."""
    #     return self._target_temperature

    @property
    def supported_features(self):
        """Bitmap of supported features"""
        return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE | ClimateEntityFeature.FAN_MODE 

    async def async_set_preset_mode(self, preset_mode):
        """Set the preset mode of the power"""
        
        # self._attr_preset_mode = str(preset_mode)
        
        await self.api.set_power_level(int(preset_mode))
        await self.coordinator.async_refresh()

    async def async_set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        # self._attr_fan1_speed = str(fan_mode)
        
        await self.api.set_fan_1_speed(int(fan_mode))
        await self.coordinator.async_refresh()
    
    async def async_set_fan2_mode(self, fan_mode):
        """Set new target fan mode."""
        await self.api.set_fan_2_speed(int(fan_mode))
        await self.coordinator.async_refresh()

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            target_tmp = kwargs.get(ATTR_TEMPERATURE)
            await self.api.set_temperature(target_tmp)
        await self.coordinator.async_refresh()



    def _handle_coordinator_update(self) -> None:   
        """Fetch new state data for the sensor."""
        self._attr_current_temperature  = self.coordinator.get_temperature()
        self._attr_target_temperature  = self.coordinator.get_target_temperature()
        self._attr_preset_mode = str(self.coordinator.get_power_actual_setpoint())
        self._attr_fan1_speed = str(self.coordinator.get_fan_1_actual_setpoint())
        
        power = self.coordinator.get_power_status()
        if power is True:
            self._attr_hvac_mode = HVACMode.HEAT
        else:
            self._attr_hvac_mode = HVACMode.OFF
        self.async_write_ha_state()  

    # async def async_update(self) -> None:
    #     """Fetch new state data for the sensor."""
    #     try:
    #         self._current_temperature = await self.api.get_temperature()
    #         self._target_temperature = await self.api.get_target_temperature()
    #         self._preset_mode = str(await self.api.get_power_actual_setpoint())
    #         self._fan1_speed = await self.api.get_fan_1_actual_setpoint()
            
    #         power = await self.api.get_power_status()
    #         if power is True:
    #             self._hvac_mode = HVACMode.HEAT
    #         else:
    #             self._hvac_mode = HVACMode.OFF

    #     except HttpException as err:
    #         _LOGGER.error(str(err))
    #         return

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        

        if hvac_mode not in CLIMATE_HVAC_MODE_MANAGED:
            raise ValueError(f"Unsupported HVAC mode: {hvac_mode}")

        if hvac_mode == HVACMode.OFF:
            await self.api.disable_power()

        if hvac_mode == HVACMode.HEAT :
            await self.api.enable_power()

        # _LOGGER.info("Setting operation mode to %s", hvac_mode)
        await self.coordinator.async_refresh()

    async def async_turn_on(self):
        """Turn on."""
        await self.async_set_hvac_mode(HVACMode.HEAT)
    
    async def async_turn_off(self):
        """Turn off."""
        await self.async_set_hvac_mode(HVACMode.OFF)


