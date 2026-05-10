"""Config flow for Geberit DuoFresh integration."""
from __future__ import annotations

import re

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak

from .const import DOMAIN

BT_ADDRESS_PATTERN = re.compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')
PAIRING_CODE_PATTERN = re.compile(r'^\d{4}$')

DEVICE_TYPES = ["Geberit DuoFresh"]


def validate_bluetooth_address(value: str) -> str:
    """Validate and normalize a Bluetooth MAC address."""
    value = value.strip().upper()
    if not BT_ADDRESS_PATTERN.match(value):
        raise vol.Invalid("invalid_bluetooth_address")
    return value


def validate_pairing_code(value: str) -> str:
    """Validate a 4-digit pairing code."""
    value = value.strip()
    if not PAIRING_CODE_PATTERN.match(value):
        raise vol.Invalid("invalid_pin")
    return value


USER_SCHEMA = vol.Schema({
    vol.Required("name"): str,
    vol.Required("address"): vol.All(str, validate_bluetooth_address),
    vol.Required("device_type", default=DEVICE_TYPES[0]): vol.In(DEVICE_TYPES),
    vol.Required("pairing_code"): vol.All(str, validate_pairing_code),
})


class GeberitDuoFreshConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Geberit DuoFresh."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial (manual) step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                validated = USER_SCHEMA(user_input)
            except vol.Invalid as exc:
                field = str(exc.path[0]) if exc.path else "base"
                errors[field] = exc.msg
            else:
                await self.async_set_unique_id(validated["address"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=validated["name"],
                    data=validated,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by Bluetooth discovery."""
        address = validate_bluetooth_address(discovery_info.address)
        name = discovery_info.name or f"Geberit DuoFresh ({address})"

        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        mfr_data = discovery_info.manufacturer_data.get(1538)

        self.context.update({
            "address": address,
            "name": name,
            "manufacturer_data": mfr_data.hex() if mfr_data else None,
            "title_placeholders": {"name": name},
        })

        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        """Confirm a Bluetooth discovery."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Pairing code is optional, but validate when used.
            pairing_code = user_input.get("pairing_code", "").strip()
            if pairing_code:
                try:
                    pairing_code = validate_pairing_code(pairing_code)
                except vol.Invalid as exc:
                    errors["pairing_code"] = exc.msg

            if not errors:
                return self.async_create_entry(
                    title=user_input["name"],
                    data={
                        "address": self.context["address"],
                        "device_type": DEVICE_TYPES[0],
                        "name": user_input["name"],
                        "pairing_code": pairing_code or None,
                        "manufacturer_data": self.context.get("manufacturer_data"),
                    },
                )

        return self.async_show_form(
            step_id="bluetooth_confirm",
            data_schema=vol.Schema({
                vol.Required("name", default=self.context["name"]): str,
                vol.Optional("pairing_code"): str,
            }),
            errors=errors,
            description_placeholders={"address": self.context["address"]},
        )
