"""Edilkamin async api."""
##import json
import logging
##import asyncio
##import async_timeout
import typing#
##import aiohttp
##from aiohttp import ClientSession

import edilkamin#
from homeassistant.core import HomeAssistant#

##from custom_components.edilkamin.api.auth import Auth

_LOGGER = logging.getLogger(__name__)


class EdilkaminAsyncApi:
    """
    Class to interact with the Edilkamin API.
    """

    def __init__(self, mac_address, username: str, password:str, hass: HomeAssistant) -> None:#
        """Initialize the class."""
        self._hass = hass
        self._mac_address = mac_address
        self._username = username
        self._password = password


    def get_mac_address(self):
        """Get the mac address."""
        return self._mac_address


    async def authenticate(self) -> bool:#
        try:#
            await self._hass.async_add_executor_job(#
                edilkamin.sign_in, self._username, self._password#
            )#
            return True#
        except Exception:#
            return False#

    async def get_temperature(self):
        """Get the temperature."""
        result = (await self.get_info()).get("status").get("temperatures").get("enviroment")
        return result

    async def set_temperature(self, value):
        """Modify the temperature."""
        await self.execute_command({"name": "enviroment_1_temperature", "value": value})

    async def get_power_status(self):
        """Get the power status."""
        result = (await self.get_info()).get("status").get("commands").get("power")
        return result
    
    async def get_power_actual_setpoint(self):
        """Get power setpoint."""
        _LOGGER.debug("Get power setpoint.")
        return (await self.get_info()).get("nvm").get("user_parameters").get("manual_power")

    async def enable_power(self):
        """Set the power status to on."""
        await self.execute_command({"name": "power", "value": 1})

    async def disable_power(self):
        """Set the power status to off."""#
        await self.execute_command({"name": "power", "value": 0})

    async def get_chrono_mode_status(self):
        """Get the status of the chrono mode."""
        return (await self.get_info()).get("nvm").get("chrono").get("is_active")

    async def enable_chrono_mode(self):
        """Enable the chrono mode."""
        await self.execute_command({"name": "chrono_mode", "value": True})

    async def disable_chrono_mode(self):
        """Disable the chono mode."""
        await self.execute_command({"name": "chrono_mode", "value": False})

    async def get_airkare_status(self):
        """Get status of airekare."""
        return (await self.get_info()).get("status").get("flags").get("is_airkare_active")

    async def enable_airkare(self):
        """Enable airkare."""
        await self.execute_command({"name": "airkare_function", "value": 1})

    async def disable_airkare(self):
        """Disable airkare."""
        await self.execute_command({"name": "airkare_function", "value": 0})

    async def get_relax_status(self):
        """Get the status of relax mode."""
        _LOGGER.debug("Get relax status")
        ##response = await self.execute_get_request()
        ##return response.get("status").get("flags").get("is_relax_active")
        return (await self.get_info()).get("status").get("flags").get("is_relax_active")#

    async def enable_relax(self):
        """Enable relax."""
        _LOGGER.debug("Enable relax")
        ##await self.execute_put_request("relax_mode", True)
        await self.execute_command({"name": "relax_mode", "value": True})#

    async def disable_relax(self):
        """Disable relax."""
        _LOGGER.debug("Disable relax")
        ##await self.execute_put_request("relax_mode", False)
        await self.execute_command({"name": "relax_mode", "value": False})#

    async def get_status_tank(self):
        """Get the status of the tank."""
        _LOGGER.debug("Get tank status")
        return (await self.get_info()).get("status").get("flags").get("is_pellet_in_reserve")
    
    async def get_fan_1_is_active(self):
        """Get fan 1 is active."""
        _LOGGER.debug("Get fan 1 is active")
        return (await self.get_info()).get("status").get("pump").get("flags2").get("fan_1_active")

    async def get_fan_1_actual_setpoint(self):
        """Get fan 1 setpoint."""
        _LOGGER.debug("Get fan 1 setpoint.")
        return (await self.get_info()).get("nvm").get("user_parameters").get("fan_1_ventilation")
    
    async def get_fan_1_speed(self):
        """Get the speed of fan 1."""
        return int(await self.get_info()).get("status").get("fans").get("fan_1_speed")

    async def set_fan_1_speed(self, value):
        """Set the speed of fan 1."""
        await self.execute_command({"name": "fan_1_speed", "value": int(value)})

    async def get_fan_2_is_active(self):
        """Get fan 2 is active."""
        _LOGGER.debug("Get fan 2 is active")
        return (await self.get_info()).get("status").get("pump").get("flags2").get("fan_2_active")

    async def get_fan_2_actual_setpoint(self):
        """Get fan 2 setpoint."""
        _LOGGER.debug("Get fan 2 setpoint.")
        return (await self.get_info()).get("nvm").get("user_parameters").get("fan_2_ventilation")

    async def get_fan_2_speed(self):
        """Get the speed of fan 2."""
        return int(await self.get_info()).get("status").get("fans").get("fan_2_speed")

    async def set_fan_2_speed(self, value):
        """Set the speed of fan 2."""
        _LOGGER.debug("Set speed for fan 2 to %s", value)
        ##await self.execute_put_request("fan_2_speed", int(value))
        await self.execute_command({"name": "fan_2_speed", "value": int(value)})

    async def check(self):
        """Call check config."""
        await self.execute_command({"name": "check", "value": False})

    async def get_target_temperature(self):
        """Get the target temperature."""
        return (await self.get_info()).get("nvm").get("user_parameters").get("enviroment_1_temperature")

    async def get_actual_power(self):
        """Get the power status."""
        return (await self.get_info()).get("status").get("state").get("actual_power")
    
    async def set_power_level(self, value):
        """Set the power level."""
        _LOGGER.debug("Set power level to %s", value)
        await self.execute_command({"name": "power_level", "value": value})#todo verifier

    async def get_alarms(self):
        """Get the target temperature."""
        alarms_info = (await self.get_info()).get("nvm").get("alarms_log")
        index = alarms_info.get("index")
        alarms = []

        for i in range(index):
            alarms.append(alarms_info.get("alarms")[i])

        return alarms

    async def get_nb_alarms(self):
        """Get the target temperature."""
        return (await self.get_info()).get("nvm").get("alarms_log").get("index")

    async def get_token(self):
        return await self._hass.async_add_executor_job(edilkamin.sign_in, self._username, self._password)

    async def get_info(self):
        """
        Get the device information.
        """
        token = await self.get_token()
        return await self._hass.async_add_executor_job(
            edilkamin.device_info,
            token,
            self._mac_address
        )

    async def execute_command(self, payload: typing.Dict) -> str:
        """
        Execute the command.
        """
        token = await self.get_token()
        _LOGGER.debug("Execute command with payload = %s", payload)
        return await self._hass.async_add_executor_job(
            edilkamin.mqtt_command,
            token,
            self._mac_address,
            payload
        )






class HttpException(Exception):
    """HTTP exception class with message text, and status code."""

    def __init__(self, message, text, status_code)-> None:
        """Initialize the class."""
        super().__init__(message)

        self.status_code = status_code
        self.text = text
