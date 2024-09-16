import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class IbepowerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input["host"]
            name = user_input["name"]
            device_type = user_input["device_type"]
            await self.async_set_unique_id(f"{device_type}_{host}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=name, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host"): str,
                    vol.Required("device_type"): vol.In(["ibeplug"]),
										# vol.Required("device_type"): vol.In(["ibeplug", "ibediv", "ibemeter"]),
                    vol.Optional("name", default=""): str,
                }
            ),
            errors=errors,
        )

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo):
        _LOGGER.debug("Dispositivo descubierto via mDNS: %s", discovery_info)

        if discovery_info.type == "_ibeplug._tcp.local.":
            device_type = "ibeplug"
        #elif discovery_info.type == "_ibediv._tcp.local.":
        #    device_type = "ibediv"
        else:
            _LOGGER.debug("Dispositivo ignorado, tipo de servicio no reconocido.")
            return self.async_abort(reason="not_ibepower_device")

        properties = discovery_info.properties
        host = discovery_info.host
        desc = properties.get("desc", "Unknown")
        version = properties.get("version", "1.0")

        mac = properties.get("mac")
        if mac is None:
            _LOGGER.debug("Dispositivo sin dirección MAC, ignorado.")
            return self.async_abort(reason="no_mac_address")

        name = f"{device_type.capitalize()} ({desc})"

        unique_id = f"{device_type}_{mac}"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=name,
            data={
                "host": host,
                "name": name,
                "mac": mac,
                "device_type": device_type,
                "version": version
            },
        )
