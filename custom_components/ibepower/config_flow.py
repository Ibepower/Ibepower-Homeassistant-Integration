import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_registry import async_get
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
            unique_id = f"{device_type}_{host}"
            
            _LOGGER.debug("Host: %s, Name: %s, Device Type: %s, Unique ID: %s", host, name, device_type, unique_id)
            
            await self.async_set_unique_id(unique_id)

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
        
        _LOGGER.debug("Dispositivo encontrado: %s (%s) en %s", name, mac, host)

        # Comprueba si el dispositivo ya está configurado
        existing_entry = await self.async_set_unique_id(unique_id)
        if existing_entry:
            # Comprueba si la descripción del dispositivo ha cambiado
            old_desc = existing_entry.data.get("description")
            if old_desc != desc:
                _LOGGER.debug(f"Detectado cambio en la descripción del dispositivo: {old_desc} -> {desc}")
                # Actualiza la descripción del dispositivo
                self.hass.config_entries.async_update_entry(
                    existing_entry,
                    title = name,
                    data={
                        **existing_entry.data,
                        "description": desc,
                        "name": name,
                    }
                )

                await self.hass.config_entries.async_reload(existing_entry.entry_id)

                # Actualiza la descripción en el diccionario y en las entidades asociadas
                device_info = self.hass.data[DOMAIN].get(existing_entry.entry_id)
                _LOGGER.debug(f"device_info: {device_info}")
                if device_info and 'device' in device_info:
                    device = device_info['device']
                    device.description = desc
                    device.name = name
                    _LOGGER.debug(f"Descripción del dispositivo actualizada a {device.description}")
                    _LOGGER.debug(f"Nombre del dispositivo actualizado a {device.name}")

                entity_registry = async_get(self.hass)
                for entity in entity_registry.entities.values():
                    if entity.config_entry_id == existing_entry.entry_id:
                        entity_object = self.hass.data[DOMAIN].get(entity.unique_id)

                        if entity_object and hasattr(entity_object, 'update_name'):
                            _LOGGER.debug(f"Actualizando descripción de la entidad {entity.unique_id} a {entity_object._generate_name()}")
                            entity_object.update_name()
                        else:
                            _LOGGER.debug(f"entity_object no encontrado para {entity.unique_id}")
                
                _LOGGER.debug(f"Actualización completada a {desc}")

            return self.async_abort(reason="device_already_configured")

        _LOGGER.debug("Creando nuevo dispositivo %s", name)
        return self.async_create_entry(
            title = name,
            data={
                "host": host,
                "name": name,
                "mac": mac,
                "device_type": device_type,
                "version": version,
                "description": desc,
            },
        )
