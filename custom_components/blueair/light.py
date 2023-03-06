"""Support for Blueair backlight."""
from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
)

from math import copysign
from typing import Any, Optional

from .const import DOMAIN, LOGGER
from .device import BlueairDataUpdateCoordinator
from .entity import BlueairEntity

BRIGHTNESS_MULTIPLIER = 63.75

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair backlight from config entry."""
    devices: list[BlueairDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]["devices"]
    entities = []
    for device in devices:
        if device.model != 'foobot':
            entities.extend(
                [
                    BlueairLight(f"{device.device_name}_light", device),
                ]
            )
    async_add_entities(entities)


class BlueairLight(BlueairEntity, LightEntity):
    """Controls Backlight."""

    def __init__(self, name, device):
        """Initialize the Light Entity."""
        super().__init__("Light", name, device)

    @property
    def supported_color_modes(self) -> set[ColorMode]:
        color_modes: set(ColorMode) = set()
        
        if self._device.brightness_supported:
            color_modes.add(ColorMode.BRIGHTNESS)

        return color_modes

    @property
    def supported_features(self) -> int:
        # If the fan_mode property is supported, enable support for presets
        if self._device.brightness_supported:
            return SUPPORT_BRIGHTNESS 
        return 0

    @property
    def brightness(self) -> Optional[int]:
        """Return the current backlight brightness."""
        if self._device.brightness is not None:
            return int(round(self._device.brightness * BRIGHTNESS_MULTIPLIER, 0))
        else:
            return None

    @property
    def is_on(self) -> bool:
        return self._device.brightness > 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on or control the light."""
        await self.async_set_brightness(kwargs.get(ATTR_BRIGHTNESS, 255))

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off or control the light."""
        await self.async_set_brightness(kwargs.get(ATTR_BRIGHTNESS, 0))

    async def async_set_brightness(self, next_brightness: int) -> None:
        """Sets backlight brightness."""
        next_device_brightness = int(round(next_brightness / BRIGHTNESS_MULTIPLIER))
        await self._device.set_brightness(next_device_brightness)
