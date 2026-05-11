"""Sensor platform for Geberit DuoFresh."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GeberitCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Geberit DuoFresh sensors."""
    coordinator: GeberitCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        GeberitRssiSensor(coordinator, entry),
        GeberitMacSensor(coordinator, entry),
    ])


class _GeberitSensorBase(CoordinatorEntity[GeberitCoordinator], SensorEntity):
    """Shared base class with device_info."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: GeberitCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._address = entry.data["address"]

    @property
    def device_info(self) -> DeviceInfo:
        """Koppelt deze entiteit aan een specifiek apparaat."""
        data = self.coordinator.data or {}
        strings = data.get("device_strings")
        
        return DeviceInfo(
            identifiers={(DOMAIN, self._address)},
            connections={(CONNECTION_BLUETOOTH, self._address)},
            name=self._entry.title,
            manufacturer="Geberit",
            model=strings.device_type_name if strings else "DuoFresh",
            model_id=strings.model if strings else "DuoFresh",
            sw_version=(strings.fw_version or strings.sw_version) if strings else None,
            hw_version=strings.hw_version if strings else None,
        )


class GeberitRssiSensor(_GeberitSensorBase):
    """Bluetooth RSSI sensor."""

    _attr_translation_key = "bluetooth_signal"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_icon = "mdi:signal-distance-variant"

    def __init__(self, coordinator: GeberitCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        # Unique ID moet uniek zijn over de hele HA installatie
        self._attr_unique_id = f"{self._address}_rssi"

    @property
    def native_value(self) -> int | None:
        """Return RSSI uit coordinator data."""
        if self.coordinator.data:
            return self.coordinator.data.get("rssi")
        return None


class GeberitMacSensor(_GeberitSensorBase):
    """Bluetooth MAC adres sensor."""

    _attr_translation_key = "bluetooth_mac"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:bluetooth"

    def __init__(self, coordinator: GeberitCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self._address}_mac"
        self._attr_native_value = self._address
