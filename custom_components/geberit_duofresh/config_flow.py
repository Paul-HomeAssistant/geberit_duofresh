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
    value = value.strip().upper()
    if not BT_ADDRESS_PATTERN.match(value):
        raise vol.Invalid("invalid_bluetooth_address")
    return value

def validate_pairing_code(value: str) -> str:
    if not value: return ""
    value = value.strip()
    if not PAIRING_CODE_PATTERN.match(value):
        raise vol.Invalid("invalid_pin")
    return value

class GeberitDuoFreshConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                # Handmatige validatie ipv USER_SCHEMA om crashes te voorkomen
                address = validate_bluetooth_address(user_input["address"])
                pairing_code = validate_pairing_code(user_input.get("pairing_code", ""))
                
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input["name"],
                    data={**user_input, "address": address, "pairing_code": pairing_code},
                )
            except vol.Invalid as e:
                errors["base"] = str(e)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("address"): str,
                vol.Required("device_type", default=DEVICE_TYPES[0]): vol.In(DEVICE_TYPES),
                vol.Optional("pairing_code"): str,
            }),
            errors=errors,
        )

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak):
        address = discovery_info.address
        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()
        self.context["title_placeholders"] = {"name": address}

        self.context.update({
            "address": address,
            "name": discovery_info.name or f"Geberit DuoFresh ({address})",
        })
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data={
                    "address": self.context["address"],
                    "name": user_input["name"],
                    "pairing_code": user_input.get("pairing_code", "").strip(),
                    "device_type": DEVICE_TYPES[0],
                },
            )

        return self.async_show_form(
            step_id="bluetooth_confirm",
            data_schema=vol.Schema({
                vol.Required("name", default=self.context["name"]): str,
                vol.Optional("pairing_code"): str,
            }),
            description_placeholders={"address": self.context["address"]},
        )
