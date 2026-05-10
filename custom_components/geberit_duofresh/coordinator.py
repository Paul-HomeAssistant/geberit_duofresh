"""DataUpdateCoordinator for Geberit DuoFresh."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
import logging

from bleak import BleakClient
from bleak_retry_connector import establish_connection

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    UUID_FIRMWARE_REVISION,
    UUID_HARDWARE_REVISION,
    UUID_MANUFACTURER_NAME,
    UUID_MODEL_NUMBER,
    UUID_SERIAL_NUMBER,
    UUID_SOFTWARE_REVISION,
)

_LOGGER = logging.getLogger(__name__)

# Polling interval
UPDATE_INTERVAL = timedelta(minutes=5)


@dataclass
class GeberitDeviceStrings:
    """Cached device-info strings (uit GATT)."""
    manufacturer: str | None = None
    model: str | None = None
    serial: str | None = None
    hw_version: str | None = None
    fw_version: str | None = None
    sw_version: str | None = None


class GeberitCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator does periodic RSSI polling and one-time get of device-info."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=UPDATE_INTERVAL,
        )
        self.address: str = entry.data["address"]
        self._device_strings: GeberitDeviceStrings | None = None

    # ------------------------------------------------------------------
    #  Called every 5 minutes by HA
    # ------------------------------------------------------------------
    async def _async_update_data(self) -> dict:
        """Fetch RSSI (altijd) en device-strings (eenmalig via GATT)."""

        # ── 1. RSSI via passive BLE-scan ──────────────────────────
        rssi = self._get_rssi_from_scan()

        # ── 2. Device-strings (One-time get via GATT) ────────
        if self._device_strings is None:
            self._device_strings = await self._fetch_device_strings()

        return {
            "rssi": rssi,
            "device_strings": self._device_strings,
        }

    # ------------------------------------------------------------------
    #  Get RSSI from most recent BLE advertisement (No GATT)
    # ------------------------------------------------------------------
    def _get_rssi_from_scan(self) -> int | None:
        """Haal RSSI op via async_last_service_info – geen connectie nodig."""
        service_info = bluetooth.async_last_service_info(
            self.hass, self.address, connectable=False
        )
        if service_info is not None:
            _LOGGER.debug(
                "RSSI voor %s via scan: %s dBm", self.address, service_info.rssi
            )
            return service_info.rssi

        # Fallback: try via ble_device.rssi
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=False
        )
        if ble_device is not None:
            rssi = getattr(ble_device, "rssi", None)
            _LOGGER.debug(
                "RSSI voor %s via ble_device fallback: %s dBm", self.address, rssi
            )
            return rssi

        _LOGGER.debug("Geen RSSI beschikbaar voor %s", self.address)
        return None

    # ------------------------------------------------------------------
    #  One-time get of Device-strings via GATT-connection
    # ------------------------------------------------------------------
    async def _fetch_device_strings(self) -> GeberitDeviceStrings | None:
        """Maak GATT-verbinding en lees device-info characteristics."""
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if ble_device is None:
            _LOGGER.warning(
                "Kan %s niet vinden voor GATT-verbinding (device-info wordt later opgehaald)",
                self.address,
            )
            return None

        client: BleakClient | None = None
        try:
            client = await establish_connection(
                BleakClient, ble_device, self.address
            )
            _LOGGER.debug("GATT verbonden met %s", self.address)

            strings = GeberitDeviceStrings(
                manufacturer=await self._read_utf8(client, UUID_MANUFACTURER_NAME),
                model=await self._read_utf8(client, UUID_MODEL_NUMBER),
                serial=await self._read_utf8(client, UUID_SERIAL_NUMBER),
                hw_version=await self._read_utf8(client, UUID_HARDWARE_REVISION),
                fw_version=await self._read_utf8(client, UUID_FIRMWARE_REVISION),
                sw_version=await self._read_utf8(client, UUID_SOFTWARE_REVISION),
            )
            _LOGGER.info(
                "Device-info opgehaald voor %s: model=%s, fw=%s",
                self.address,
                strings.model,
                strings.fw_version,
            )
            return strings

        except Exception as err:
            _LOGGER.warning(
                "GATT-verbinding mislukt voor %s (wordt later opnieuw geprobeerd): %s",
                self.address,
                err,
            )
            return None  # Next poll tries again

        finally:
            if client:
                try:
                    await client.disconnect()
                except Exception:
                    pass

    # ------------------------------------------------------------------
    @staticmethod
    async def _read_utf8(client: BleakClient, uuid: str) -> str | None:
        """Lees een GATT-characteristic als UTF-8 string."""
        try:
            raw = await client.read_gatt_char(uuid)
            return (
                raw.decode("utf-8", errors="ignore").replace("\x00", "").strip()
                or None
            )
        except Exception:
            return None
