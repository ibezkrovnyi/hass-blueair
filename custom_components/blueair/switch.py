"""Support for Blueair Child lock."""
from homeassistant.components.switch import (
    SwitchEntity,
)

from typing import Any, Optional

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator
from .entity import BlueairEntity

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair child locks from config entry."""
    devices: list[BlueairDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]["devices"]
    entities = []
    for device in devices:
        if device.model != 'foobot' and device.child_lock is not None:
            entities.append(BlueairChildLockSwitch(f"{device.device_name} Child Lock", device))
    async_add_entities(entities)

class BlueairChildLockSwitch(BlueairEntity, SwitchEntity):
    """Controls Child lock switch."""

    _attr_icon: str = "mdi:account-lock"
    _attr_should_poll = True

    def __init__(self, name, device):
        """Initialize the Switch Entity."""
        super().__init__("Child lock", name, device)
        self._state: Any = None

    @property
    def is_on(self) -> Optional[bool]:
        return self._device.child_lock

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._device.set_child_lock(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._device.set_child_lock(False)
