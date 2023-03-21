"""Support for Blueair sensors."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass
from collections.abc import Callable

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    DEVICE_CLASS_CO2,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_PM1,
    DEVICE_CLASS_PM10,
    DEVICE_CLASS_PM25,
    DEVICE_CLASS_VOLATILE_ORGANIC_COMPOUNDS,
    DEVICE_CLASS_TIMESTAMP,
    TEMP_CELSIUS,
    PERCENTAGE,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    CONCENTRATION_PARTS_PER_BILLION,
)

from .const import DOMAIN, LOGGER
from .device import BlueairDataUpdateCoordinator, DataAttribute
from .entity import BlueairEntity

NAME_TEMPERATURE = "Temperature"
NAME_HUMIDITY = "Humidity"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair sensors from config entry."""
    coordinators: list[BlueairDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]["devices"]
    
    entities = []
    for coordinator in coordinators:
        # Don't add sensors to classic models
        if (
            coordinator.model.startswith("classic") and not coordinator.model.endswith("i")
        ) or coordinator.model == "foobot":
            pass
        else:
            for description in SENSOR_TYPES:
                # When we use the nearest method, we are not sure which sensors are available
                if coordinator.data.get(description.key):
                    entities.append(BlueairSensor(coordinator, description))

    async_add_entities(entities)

@dataclass
class BlueairSensorEntityDescription(SensorEntityDescription):
    """Class describing Blueair sensor entities."""
    attrs: Callable[[dict[str, Any]], dict[str, Any]] = lambda data: {}

SENSOR_TYPES: tuple[BlueairSensorEntityDescription, ...] = (
    BlueairSensorEntityDescription(
        key=DataAttribute.TEMPERATURE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        # attrs=lambda data: {
        #     ATTR_LEVEL: data[ATTR_API_CAQI_LEVEL],
        #     ATTR_ADVICE: data[ATTR_API_ADVICE],
        #     ATTR_DESCRIPTION: data[ATTR_API_CAQI_DESCRIPTION],
        # },
    ),
    BlueairSensorEntityDescription(
        key=DataAttribute.HUMIDITY,
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
    ),
    BlueairSensorEntityDescription(
        key=DataAttribute.CO2,
        name="Carbon dioxide",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        suggested_display_precision=0,
    ),
    BlueairSensorEntityDescription(
        key=DataAttribute.VOC,
        name="Volatile organic compounds",
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_BILLION,
        suggested_display_precision=0,
    ),
    BlueairSensorEntityDescription(
        key=DataAttribute.ALL_POLLUTION,
        # device_class=SensorDeviceClass.,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        icon="mdi:molecule",
    ),
    BlueairSensorEntityDescription(
        key=DataAttribute.PM1,
        name="PM1.0",
        device_class=SensorDeviceClass.PM1,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        suggested_display_precision=1,
    ),
    BlueairSensorEntityDescription(
        key=DataAttribute.PM25,
        name="PM2.5",
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        suggested_display_precision=1,
    ),
    BlueairSensorEntityDescription(
        key=DataAttribute.PM10,
        name="PM10",
        device_class=SensorDeviceClass.PM10,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        suggested_display_precision=1,
    ),
    BlueairSensorEntityDescription(
        key=DataAttribute.FILTER_STATUS,
        icon="mdi:air-filter",
    ),
    BlueairSensorEntityDescription(
        key=DataAttribute.LAST_SEEN,
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-time-two-outline",
    ),
)

class BlueairSensor(BlueairEntity, SensorEntity):
    """Define a Blueair sensor."""

    _attr_has_entity_name = True
    entity_description: BlueairSensorEntityDescription

    def __init__(
        self,
        coordinator: BlueairDataUpdateCoordinator,
        description: BlueairSensorEntityDescription,
    ) -> None:
        """Initialize."""
        if description.name is None:
            description.name = description.key.capitalize()
        super().__init__(description.key, "", coordinator)

        # self._attr_unique_id = (
        #     f"{coordinator.latitude}-{coordinator.longitude}-{description.key}".lower()
        # )
        self._attr_native_value = coordinator.data[description.key]
        # self._attr_extra_state_attributes = description.attrs(coordinator.data)
        self.entity_description = description
        LOGGER.error(f"igor: sensor init: entity_description={self.entity_description}")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        
        self._attr_native_value = self.coordinator.data[self.entity_description.key]
        # self._attr_extra_state_attributes = self.entity_description.attrs(
        #     self.coordinator.data
        # )
        self.async_write_ha_state()
