"""Support for Blueair Child lock."""
from homeassistant.components.switch import (
    SwitchDeviceClass, SwitchEntity, SwitchEntityDescription
)

from typing import Any, Optional

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator, DataAttribute
from .entity import BlueairEntity

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair child locks from config entry."""
    coordinators: list[BlueairDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]["devices"]
    entities = []
    for coordinator in coordinators:
        if coordinator.model != 'foobot' and coordinator.child_lock is not None:
            entities.append(BlueairChildLockSwitch(coordinator))
    async_add_entities(entities)

class BlueairChildLockSwitch(BlueairEntity[SwitchEntityDescription], SwitchEntity):
    """Controls Child lock switch."""

    _attr_icon: str = "mdi:account-lock"
    # _attr_should_poll = True

    def __init__(self, device):
        """Initialize the Switch Entity."""
        super().__init__(device, SwitchEntityDescription(
            key=DataAttribute.CHILD_LOCK,
            name="Child lock",
            device_class=SwitchDeviceClass.SWITCH,
        ))

    @property
    def is_on(self) -> Optional[bool]:
        return self.coordinator.child_lock

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.set_child_lock(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.set_child_lock(False)
