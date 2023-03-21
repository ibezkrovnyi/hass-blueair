"""Base entity class for Blueair entities."""
from typing import Any, Optional

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator, DataAttribute


class BlueairEntity(CoordinatorEntity[BlueairDataUpdateCoordinator], Entity):
    """A base class for Blueair entities."""

    # _attr_force_update = False
    # _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(
        self,
        entity_type: str,
        name: str,
        coordinator: BlueairDataUpdateCoordinator,
        **kwargs,
    ) -> None:
        """Init Blueair entity."""
        super().__init__(coordinator)
        self._device = coordinator
        # self._attr_name = f"{name}"
        self._attr_unique_id = f"{coordinator.id}_{entity_type}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return a device description for device registry."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.id)},
            "manufacturer": self.coordinator.manufacturer,
            "model": self.coordinator.model,
            "name": self.coordinator.device_name,
        }

    @property
    def available(self) -> Optional[bool]:
        return self.coordinator.data.get(DataAttribute.AVAILABLE, True)

    async def async_update(self):
        """Update Blueair entity."""
        await self.coordinator.async_request_refresh()

    # async def async_added_to_hass(self):
    #     """When entity is added to hass."""
    #     self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
