import logging
import json
from pathlib import Path
from datetime import timedelta
from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.frontend import add_extra_js_url
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
STATIC_DIR_PATH = Path(__file__).resolve().parent / "www"
STATIC_URL_BASE = "/ibepower_static"
CARD_JS_FILE = "ibepower-cards.js"


class _IbepowerStaticView(HomeAssistantView):
    """Serve bundled assets with explicit no-cache headers."""

    requires_auth = False
    url = STATIC_URL_BASE + "/{path:.+}"
    name = "ibepower_static"

    async def get(self, request, path):
        base = STATIC_DIR_PATH.resolve()
        fpath = (STATIC_DIR_PATH / path).resolve()
        if not fpath.is_relative_to(base) or not fpath.is_file():
            raise web.HTTPNotFound()
        return web.FileResponse(
            fpath,
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
            },
        )


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the ibepower domain (runs once, before any config entry)."""
    hass.data.setdefault(DOMAIN, {})

    # Serve www/ files via a custom view with no-cache headers
    hass.http.register_view(_IbepowerStaticView())

    # Use file mtime as cache buster so every deploy invalidates the URL
    try:
        mtime = int((STATIC_DIR_PATH / CARD_JS_FILE).stat().st_mtime)
    except Exception:
        mtime = 0
    add_extra_js_url(hass, f"{STATIC_URL_BASE}/{CARD_JS_FILE}?v={mtime}")

    return True


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
        always_update=True,
    )

    _LOGGER.debug("[Init] Device Name: %s, Device Mac: %s, Device Version: %s, Device Description: %s, Device Type: %s", device.name, device.mac, device.version, device.description, device_type)

    await coordinator.async_config_entry_first_refresh()

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
        entry_data = hass.data[DOMAIN].pop(entry.entry_id, None)
        if entry_data:
            device = entry_data.get("device")
            if device and hasattr(device, "async_close_session"):
                await device.async_close_session()
    return unload_ok
