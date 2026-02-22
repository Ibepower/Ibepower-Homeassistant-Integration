import logging

from homeassistant import config_entries

try:
    # HA Core 2026.2+
    from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
except ImportError:
    # Older HA cores
    from homeassistant.components.zeroconf import ZeroconfServiceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class IbepowerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_abort(
            reason=(
                "Ibepower Integration is configured via Zeroconf. "
                "Please, close this dialog and wait for the device to be discovered."
            )
        )

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo):
        _LOGGER.debug("Dispositivo descubierto via mDNS: %s", discovery_info)

        if discovery_info.type == "_ibeplug._tcp.local.":
            device_type = "Ibeplug"
        elif discovery_info.type == "_ibediv._tcp.local.":
            device_type = "Ibediv"
        elif discovery_info.type == "_ibemeter._tcp.local.":
            device_type = "Ibemeter"
        else:
            _LOGGER.debug("Dispositivo ignorado, tipo de servicio no reconocido.")
            return self.async_abort(reason="not_ibepower_device")

        properties = discovery_info.properties
        host = discovery_info.host
        desc = properties.get("desc", "Unknown")
        version = properties.get("version", "1.0")
        mac = properties.get("mac")

        if mac is None:
            _LOGGER.debug("Dispositivo sin direccion MAC, ignorado.")
            return self.async_abort(reason="no_mac_address")

        name = f"{device_type.capitalize()} ({desc})"
        unique_id = f"{device_type}_{mac}"

        _LOGGER.debug(
            "[ZEROCONF] Dispositivo encontrado: %s (%s) en %s - unique_id: %s",
            name,
            version,
            host,
            unique_id,
        )

        existing_entry = await self.async_set_unique_id(unique_id)
        if existing_entry:
            old_host = existing_entry.data.get("host")
            old_version = existing_entry.data.get("version")
            old_desc = existing_entry.data.get("description")

            any_change = False

            if old_host != host:
                _LOGGER.debug("Cambio de host detectado: %s -> %s", old_host, host)
                any_change = True

            if old_version != version:
                _LOGGER.debug("Cambio de version detectado: %s -> %s", old_version, version)
                any_change = True

            if old_desc != desc:
                _LOGGER.debug("Cambio de descripcion detectado: %s -> %s", old_desc, desc)
                any_change = True

            if any_change:
                self.hass.config_entries.async_update_entry(
                    existing_entry,
                    title=name,
                    data={
                        **existing_entry.data,
                        "description": desc,
                        "name": name,
                        "version": version,
                        "host": host,
                    },
                )

                await self.hass.config_entries.async_reload(existing_entry.entry_id)

                domain_data = self.hass.data.get(DOMAIN, {})
                entry_data = domain_data.get(existing_entry.entry_id)
                _LOGGER.debug("entry_data: %s", entry_data)

                if entry_data and "device" in entry_data:
                    device = entry_data["device"]
                    device.description = desc
                    device.name = name
                    device.version = version
                    device.host = host

                for entity_object in (entry_data or {}).get("entities", {}).values():
                    if hasattr(entity_object, "update_name"):
                        entity_object.update_name()

                _LOGGER.debug("Actualizacion completada a %s", desc)

            return self.async_abort(reason="device_already_configured")

        _LOGGER.debug("[ZEROCONF] Creando nuevo dispositivo %s", name)
        return self.async_create_entry(
            title=name,
            data={
                "host": host,
                "name": name,
                "mac": mac,
                "device_type": device_type,
                "version": version,
                "description": desc,
            },
        )

