"""Support for Blueair fans."""
from homeassistant.components.fan import (
    FanEntity,
    SUPPORT_SET_SPEED,
    SUPPORT_PRESET_MODE,
)
from homeassistant.util.percentage import (
    int_states_in_range,
    ranged_value_to_percentage,
    percentage_to_ranged_value,
)
from homeassistant.const import (
    PERCENTAGE,
)

from typing import Any, Optional

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator
from .entity import BlueairEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair fans from config entry."""
    devices: list[BlueairDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]["devices"]
    entities = []
    for device in devices:
        if device.model != 'foobot' and device.fan_speed is not None:
            entities.append(BlueairFan(f"{device.device_name} Fan", device))
    async_add_entities(entities)


class BlueairFan(BlueairEntity, FanEntity):
    """Controls Fan."""

    def __init__(self, name, device):
        """Initialize the temperature sensor."""
        super().__init__("Fan", name, device)
        self._state: Any = None

    @property
    def supported_features(self) -> int:
        # If the fan_mode property is supported, enable support for presets
        if self.coordinator.fan_mode_supported:
            return SUPPORT_SET_SPEED + SUPPORT_PRESET_MODE
        return SUPPORT_SET_SPEED

    @property
    def is_on(self) -> Optional[bool]:
        return self.coordinator.is_on

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        if self.coordinator.fan_speed is not None:
            return int(round(self.coordinator.fan_speed * 33.33, 0))
        else:
            return 0
    
    @property
    def preset_mode(self) -> Optional[str]:
        if self.coordinator.fan_mode_supported:
            return self.coordinator.fan_mode

    @property
    def preset_modes(self) -> Optional[list]:
        if self.coordinator.fan_mode_supported:
            return list([str("auto")])
        
    async def async_set_percentage(self, percentage: int) -> None:
        """Sets fan speed percentage."""
        if percentage == 100:
            new_speed = "3"
        elif percentage > 50:
            new_speed = "2"
        elif percentage > 20:
            new_speed = "1"
        else:
            new_speed = "0"

        await self.coordinator.set_fan_speed(new_speed)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.set_fan_speed("0")

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.set_fan_speed("2")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        await self.coordinator.set_fan_mode(preset_mode)

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return 3
