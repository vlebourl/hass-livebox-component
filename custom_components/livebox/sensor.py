"""Sensor for Livebox router."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COORDINATOR, DOMAIN, LIVEBOX_ID, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensors."""
    datas = hass.data[DOMAIN][config_entry.entry_id]
    box_id = datas[LIVEBOX_ID]
    coordinator = datas[COORDINATOR]
    nmc = coordinator.data["nmc"]
    entities = [
        FlowSensor(
            coordinator,
            box_id,
            description,
        )
        for description in SENSOR_TYPES
    ]
    if nmc.get("WanMode") is not None and "ETHERNET" not in nmc["WanMode"].upper():
        async_add_entities(entities, True)


class FlowSensor(CoordinatorEntity, SensorEntity):
    """Representation of a livebox sensor."""

    def __init__(self, coordinator, box_id, description):
        """Initialize the sensor."""
        self.box_id = box_id
        self.coordinator = coordinator
        self._attributs = description.attr
        self._current = description.current_rate
        self.entity_description = description

    @property
    def unique_id(self):
        """Return unique_id."""
        cr = self._current
        return f"{self.box_id}_{cr}"

    @property
    def native_value(self):
        """Return the native value of the device."""
        if self.coordinator.data["dsl_status"].get(self._current):
            return round(
                self.coordinator.data["dsl_status"][self._current] / 1000,
                2,
            )
        return None

    @property
    def device_info(self):
        """Return the device info."""
        return {"identifiers": {(DOMAIN, self.box_id)}}

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        return {
            key: self.coordinator.data["dsl_status"].get(value)
            for key, value in self._attributs.items()
        }
