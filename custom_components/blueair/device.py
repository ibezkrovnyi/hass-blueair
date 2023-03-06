"""Blueair device object."""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional
from async_timeout import timeout

from . import blueair

API = blueair.BlueAir

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.backports.enum import StrEnum
import homeassistant.util.dt as dt_util

from .const import DOMAIN, LOGGER

class ConfigAttribute(StrEnum):
    """Possible blueair configuration attributes."""
    CHILD_LOCK = "child_lock"
    BRIGHTNESS = "brightness"
    FAN_MODE = "mode"
    FAN_SPEED = "fan_speed"
    FILTER_STATUS = "filter_status"

class DatapointAttribute(StrEnum):
    """Possible blueair datapoint attributes."""
    ALL_POLLUTION = "all_pollution"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    CO2 = "co2"
    VOC = "voc"
    PM1 = "pm1"
    PM25 = "pm25"
    PM10 = "pm10"

BRIGHTNESS_MULTIPLIER = 63.75

class BlueairDataUpdateCoordinator(DataUpdateCoordinator):
    """Blueair device object."""

    def __init__(
        self, hass: HomeAssistant, api_client: API, uuid: str, device_name: str
    ) -> None:
        """Initialize the device."""
        self.hass: HomeAssistant = hass
        self.api_client: API = api_client
        self._uuid: str = uuid
        self._name: str = device_name
        self._manufacturer: str = "BlueAir"
        self._device_information: dict[str, Any] = {}
        self._datapoint: dict[str, Any] = {}
        self._attribute: dict[str, Any] = {}

        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}-{device_name}",
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            async with timeout(10):
                await asyncio.gather(*[self._update_device()])
        except Exception as error:
            raise UpdateFailed(error) from error

    @property
    def id(self) -> str:
        """Return Blueair device id."""
        return self._uuid

    @property
    def device_name(self) -> str:
        """Return device name."""
        return self._device_information.get("nickname", f"{self.name}")

    @property
    def manufacturer(self) -> str:
        """Return manufacturer for device."""
        return self._manufacturer

    @property
    def model(self) -> str:
        """Return model for device, or the UUID if it's not known."""
        return self._device_information.get("compatibility", self.id)

    @property
    def temperature(self) -> Optional[float]:
        """Return the current temperature in degrees C."""
        if DatapointAttribute.TEMPERATURE not in self._datapoint:
            return None
        return self._datapoint[DatapointAttribute.TEMPERATURE]

    @property
    def humidity(self) -> Optional[float]:
        """Return the current relative humidity percentage."""
        if DatapointAttribute.HUMIDITY not in self._datapoint:
            return None
        return self._datapoint[DatapointAttribute.HUMIDITY]

    @property
    def co2(self) -> Optional[float]:
        """Return the current co2."""
        if DatapointAttribute.CO2 not in self._datapoint:
            return None
        return self._datapoint[DatapointAttribute.CO2]

    @property
    def voc(self) -> Optional[float]:
        """Return the current voc."""
        if DatapointAttribute.VOC not in self._datapoint:
            return None
        return self._datapoint[DatapointAttribute.VOC]

    @property
    def pm1(self) -> Optional[float]:
        """Return the current pm1."""
        if DatapointAttribute.PM1 not in self._datapoint:
            return None
        return self._datapoint[DatapointAttribute.PM1]

    @property
    def pm10(self) -> Optional[float]:
        """Return the current pm10."""
        if DatapointAttribute.PM10 not in self._datapoint:
            return None
        return self._datapoint[DatapointAttribute.PM10]

    @property
    def pm25(self) -> Optional[float]:
        """Return the current pm25."""
        if DatapointAttribute.PM25 not in self._datapoint:
            return None
        return self._datapoint[DatapointAttribute.PM25]

    @property
    def all_pollution(self) -> Optional[float]:
        """Return all pollution"""
        if DatapointAttribute.ALL_POLLUTION not in self._datapoint:
            return None
        return self._datapoint[DatapointAttribute.ALL_POLLUTION]

    @property
    def fan_speed(self) -> Optional[int]:
        """Return the current fan speed."""
        if ConfigAttribute.FAN_SPEED not in self._attribute:
            return None
        return int(self._attribute[ConfigAttribute.FAN_SPEED])

    @property
    def is_on(self) -> Optional[bool]:
        """Return the current fan state."""
        if ConfigAttribute.FAN_SPEED not in self._attribute:
            return None
        if self._attribute[ConfigAttribute.FAN_SPEED] == "0":
            return False
        return True

    @property
    def fan_mode(self) -> Optional[str]:
        """Return the current fan mode"""
        if self._attribute[ConfigAttribute.FAN_MODE] == "manual":
            return None
        return self._attribute[ConfigAttribute.FAN_MODE]

    @property
    def fan_mode_supported(self) -> bool:
        """Return if fan mode is supported. This function is used to lock out unsupported
         functionality from the UI if the model doesnt support modes"""
        if ConfigAttribute.FAN_MODE in self._attribute:
            return True
        return False

    @property
    def brightness(self) -> Optional[int]:
        """Return current backlight brightness"""
        if ConfigAttribute.BRIGHTNESS not in self._attribute:
            return None

        return int(round(int(self._attribute[ConfigAttribute.BRIGHTNESS]) * BRIGHTNESS_MULTIPLIER, 0))

    @property
    def brightness_supported(self) -> bool:
        """Return if brightness is supported. This function is used to lock out unsupported
         functionality from the UI if the model doesnt support modes"""
        if ConfigAttribute.BRIGHTNESS in self._attribute:
            return True
        return False

    @property
    def child_lock(self) -> Optional[bool]:
        """Return if child lock is enabled"""
        if ConfigAttribute.BRIGHTNESS not in self._attribute:
            return None
        return bool(int(self._attribute[ConfigAttribute.BRIGHTNESS]))

    @property
    def child_lock_supported(self) -> bool:
        """Return if child lock is supported. This function is used to lock out unsupported
        functionality from the UI if the model doesnt support modes"""
        if ConfigAttribute.CHILD_LOCK in self._attribute:
            return True
        return False

    @property
    def filter_status(self) -> Optional[str]:
        """Return the current filter status."""
        if ConfigAttribute.FILTER_STATUS not in self._attribute:
            return None
        return self._attribute[ConfigAttribute.FILTER_STATUS]

    async def set_fan_speed(self, new_speed) -> None:
        await self.hass.async_add_executor_job(
            lambda: self.api_client.set_attribute(self._uuid, ConfigAttribute.FAN_SPEED, new_speed)
        )
        self._attribute[ConfigAttribute.FAN_SPEED] = new_speed
        await self.async_refresh()

    async def set_fan_mode(self, new_mode) -> None:
        await self.hass.async_add_executor_job(
            lambda: self.api_client.set_attribute(self._uuid, ConfigAttribute.FAN_MODE, new_mode)
        )
        self._attribute[ConfigAttribute.FAN_MODE] = new_mode
        await self.async_refresh()

    async def set_child_lock(self, child_lock: bool) -> None:
        device_child_lock = str(int(child_lock))
        LOGGER.info(f"igor1: child_lock={child_lock}, device_child_lock={device_child_lock}")
        await self.hass.async_add_executor_job(
            lambda: self.api_client.set_attribute(self._uuid, ConfigAttribute.CHILD_LOCK, device_child_lock)
        )
        self._attribute[ConfigAttribute.CHILD_LOCK] = device_child_lock
        await self.async_refresh()

    async def set_brightness(self, next_brightness: int) -> None:
        next_device_brightness = str(int(round(next_brightness / BRIGHTNESS_MULTIPLIER)))
        await self.hass.async_add_executor_job(
            lambda: self.api_client.set_attribute(self._uuid, ConfigAttribute.BRIGHTNESS, next_device_brightness)
        )
        self._attribute[ConfigAttribute.BRIGHTNESS] = next_device_brightness
        await self.async_refresh()

    async def _update_device(self, *_) -> None:
        """Update the device information from the API."""
        LOGGER.info(self._name)
        self._device_information = await self.hass.async_add_executor_job(
            lambda: self.api_client.get_info(self._uuid)
        )
        LOGGER.info(f"_device_information: {self._device_information}")
        try:
            # Classics will not have the expected data here
            self._datapoint = await self.hass.async_add_executor_job(
                lambda: self.api_client.get_current_data_point(self._uuid)
            )
        except Exception:
            pass
        LOGGER.info(f"_datapoint: {self._datapoint}")
        self._attribute = await self.hass.async_add_executor_job(
            lambda: self.api_client.get_attributes(self._uuid)
        )
        LOGGER.info(f"_attribute: {self._attribute}")
