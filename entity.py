"""Base entity class for Blueair entities."""
from typing import TypeVar, Generic, Optional, Any
# from dataclasses import dataclass

from homeassistant.core import callback
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import DeviceInfo, Entity, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER
from .device import BlueairDataUpdateCoordinator, DataAttribute

# @dataclass
# class BlueairEntityDescription(EntityDescription):
    # """Class describing Blueair sensor entities."""
    # attrs: Callable[[dict[str, Any]], dict[str, Any]] = lambda data: {}

# _BlueairEntityT = TypeVar('_BlueairEntityT', bound='Entity')
_BlueairEntityDescriptionT = TypeVar('_BlueairEntityDescriptionT', bound='EntityDescription')

class BlueairEntity(CoordinatorEntity[BlueairDataUpdateCoordinator], Entity, Generic[_BlueairEntityDescriptionT]):
    """A base class for Blueair entities."""

    _attr_has_entity_name = True
    entity_description: _BlueairEntityDescriptionT

    def __init__(
        self,
        coordinator: BlueairDataUpdateCoordinator,
        description: _BlueairEntityDescriptionT,
    ) -> None:
        """Initialize."""
        if description.name is None:
            description.name = description.key.capitalize()
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.id}_{description.key}"

        # self._attr_unique_id = (
        #     f"{coordinator.latitude}-{coordinator.longitude}-{description.key}".lower()
        # )
        self._attr_native_value = coordinator.data[description.key]
        # self._attr_extra_state_attributes = description.attrs(coordinator.data)
        self.entity_description = description
        LOGGER.error(f"igor: blueairentity init: entity_description={self.entity_description}")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        
        self._attr_native_value = self.coordinator.data[self.entity_description.key]
        # self._attr_extra_state_attributes = self.entity_description.attrs(
        #     self.coordinator.data
        # )
        self.async_write_ha_state()

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
