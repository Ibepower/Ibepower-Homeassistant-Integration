import logging
from pathlib import Path
from datetime import timedelta
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN
from .ibeplug_device import IBEPlugDevice
from .ibediv_device import IBEDivDevice
from .ibemeter_device import IBEMeterDevice
from .entity_naming import get_device_slug, get_object_suffix_from_unique_id

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch", "sensor", "select", "number", "button"]
STATIC_URL_PATH = "/ibepower_static"
STATIC_DIR_PATH = Path(__file__).resolve().parent / "www"
STATIC_REGISTERED_KEY = "_static_path_registered"


async def _async_register_static_path(hass: HomeAssistant) -> None:
    """Expose integration bundled assets under /ibepower_static."""
    if not STATIC_DIR_PATH.exists():
        return

    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get(STATIC_REGISTERED_KEY):
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL_PATH, str(STATIC_DIR_PATH), cache_headers=False)]
    )
    domain_data[STATIC_REGISTERED_KEY] = True


async def _async_migrate_entity_ids(hass: HomeAssistant, entry: ConfigEntry):
    """Migrate entity IDs to <domain>.<device_slug>_<entity_suffix> format."""
    mac = entry.data.get("mac")
    if not mac:
        return

    device_slug = get_device_slug(entry.data.get("description"))
    registry = er.async_get(hass)
    registry_entries = er.async_entries_for_config_entry(registry, entry.entry_id)

    for registry_entry in registry_entries:
        suffix = get_object_suffix_from_unique_id(
            unique_id=registry_entry.unique_id,
            mac=mac,
            domain=registry_entry.domain,
        )
        if not suffix:
            continue

        new_entity_id = f"{registry_entry.domain}.{device_slug}_{suffix}"
        if registry_entry.entity_id == new_entity_id:
            continue

        existing_target = registry.async_get(new_entity_id)
        if existing_target and existing_target.id != registry_entry.id:
            _LOGGER.warning(
                "No se puede migrar %s a %s porque ya existe",
                registry_entry.entity_id,
                new_entity_id,
            )
            continue

        try:
            registry.async_update_entity(
                registry_entry.entity_id,
                new_entity_id=new_entity_id,
            )
            _LOGGER.info(
                "Entidad migrada: %s -> %s",
                registry_entry.entity_id,
                new_entity_id,
            )
        except ValueError as err:
            _LOGGER.warning(
                "Error migrando %s -> %s: %s",
                registry_entry.entity_id,
                new_entity_id,
                err,
            )

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    await _async_register_static_path(hass)

    host = entry.data["host"]
    name = entry.data["name"]
    mac = entry.data.get("mac")
    version = entry.data.get("version", "1.0")
    description = entry.data.get("description", "Unknown")
    device_type = entry.data["device_type"]

    if device_type == "Ibeplug":
        device = IBEPlugDevice(hass, host, name, mac, version, description)
    elif device_type == "Ibediv":
        device = IBEDivDevice(hass, host, name, mac, version, description)
    elif device_type == "Ibemeter":
        device = IBEMeterDevice(hass, host, name, mac, version, description)
    else:
        _LOGGER.error("Tipo de dispositivo desconocido: %s", device_type)
        return False

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{device.name} Coordinator",
        update_method=device.async_update_data,
        update_interval=timedelta(seconds=10),
    )

    _LOGGER.debug("[Init] Device Name: %s, Device Mac: %s, Device Version: %s, Device Description: %s, Device Type: %s", device.name, device.mac, device.version, device.description, device_type)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "device": device,
        "coordinator": coordinator,
        "entities": {},
    }

    await _async_migrate_entity_ids(hass, entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        domain_data = hass.data.get(DOMAIN, {})
        entry_data = domain_data.get(entry.entry_id, {})
        device = entry_data.get("device")
        if device and hasattr(device, "async_close_session"):
            await device.async_close_session()
        domain_data.pop(entry.entry_id, None)
        has_active_entries = any(key != STATIC_REGISTERED_KEY for key in domain_data)
        if not has_active_entries:
            hass.data.pop(DOMAIN, None)
    return unload_ok
