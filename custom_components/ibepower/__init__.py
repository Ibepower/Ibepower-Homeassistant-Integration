import logging
from pathlib import Path
from datetime import timedelta
from urllib.parse import urlsplit
from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.lovelace.const import (
    CONF_RESOURCE_TYPE_WS,
    LOVELACE_DATA,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID, CONF_TYPE, CONF_URL, EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import HomeAssistant, callback
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
CARD_JS_URL = f"{STATIC_URL_BASE}/{CARD_JS_FILE}"
CARD_RESOURCE_TYPE = "module"
CARD_JS_FALLBACK_KEY = "__card_js_fallback_registered__"


class _IbepowerStaticView(HomeAssistantView):
    """Serve bundled assets with cache-friendly headers."""

    requires_auth = False
    url = STATIC_URL_BASE + "/{path:.+}"
    name = "ibepower_static"

    async def get(self, request, path):
        base = STATIC_DIR_PATH.resolve()
        fpath = (STATIC_DIR_PATH / path).resolve()
        if not fpath.is_relative_to(base) or not fpath.is_file():
            raise web.HTTPNotFound()
        # Always revalidate JS so mobile browsers do not hold on to a stale
        # module between HA restarts or integration upgrades.
        if fpath.suffix == '.js':
            cache = "no-cache, must-revalidate"
        else:
            cache = "public, max-age=86400"
        return web.FileResponse(fpath, headers={"Cache-Control": cache})


def _resource_path(url: str | None) -> str:
    """Return a normalized path for a Lovelace resource URL."""
    if not url:
        return ""
    return urlsplit(str(url)).path.rstrip("/")


def _is_ibepower_card_resource(url: str | None) -> bool:
    """Return True if the URL points to an ibepower cards bundle."""
    path = _resource_path(url)
    return path.endswith(f"/{CARD_JS_FILE}") or path == CARD_JS_FILE


async def _async_register_lovelace_resource(hass: HomeAssistant) -> bool:
    """Register the custom cards JS as a Lovelace resource when possible."""
    lovelace_data = hass.data.get(LOVELACE_DATA)
    if lovelace_data is None:
        _LOGGER.debug("Lovelace data not ready yet; deferring ibepower card resource registration")
        return False

    resource_collection = getattr(lovelace_data, "resources", None)
    if resource_collection is None:
        _LOGGER.debug("Lovelace resource collection not available yet")
        return False

    try:
        await resource_collection.async_get_info()
        items = list(resource_collection.async_items() or [])
        matches = [item for item in items if _is_ibepower_card_resource(item.get(CONF_URL))]

        # YAML-managed resources cannot be modified from the integration. If the
        # user already declared the resource, treat that as success.
        can_manage_resources = all(
            hasattr(resource_collection, attr)
            for attr in ("async_create_item", "async_update_item", "async_delete_item")
        )
        if not can_manage_resources:
            if matches:
                return True
            _LOGGER.debug("Ibepower Lovelace resources are YAML-managed and no entry was found")
            return False

        primary = matches[0] if matches else None
        if primary is None:
            await resource_collection.async_create_item(
                {
                    CONF_URL: CARD_JS_URL,
                    CONF_RESOURCE_TYPE_WS: CARD_RESOURCE_TYPE,
                }
            )
            _LOGGER.info("Registered Lovelace resource for Ibepower cards: %s", CARD_JS_URL)
            return True

        primary_id = primary.get(CONF_ID)
        if not primary_id:
            _LOGGER.warning("Ibepower Lovelace resource is missing its id and could not be normalized")
            return False

        updates = {}
        if primary.get(CONF_URL) != CARD_JS_URL:
            updates[CONF_URL] = CARD_JS_URL
        if primary.get(CONF_TYPE) != CARD_RESOURCE_TYPE:
            updates[CONF_RESOURCE_TYPE_WS] = CARD_RESOURCE_TYPE
        if updates:
            await resource_collection.async_update_item(primary_id, updates)
            _LOGGER.info("Updated Ibepower Lovelace resource to %s", CARD_JS_URL)

        for duplicate in matches[1:]:
            duplicate_id = duplicate.get(CONF_ID)
            if duplicate_id:
                await resource_collection.async_delete_item(duplicate_id)
                _LOGGER.info(
                    "Removed duplicate Ibepower Lovelace resource: %s",
                    duplicate.get(CONF_URL),
                )

        return True
    except Exception as err:
        _LOGGER.warning(
            "Ibepower could not normalize Lovelace resource registration: %s",
            err,
        )
        return False


async def _async_finalize_card_registration(hass: HomeAssistant) -> None:
    """Finish card registration after startup, falling back only if needed."""
    if await _async_register_lovelace_resource(hass):
        return

    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get(CARD_JS_FALLBACK_KEY):
        return

    add_extra_js_url(hass, CARD_JS_URL)
    domain_data[CARD_JS_FALLBACK_KEY] = True
    _LOGGER.warning(
        "Falling back to frontend extra_module_url for %s because Lovelace "
        "resource auto-registration was not possible. For the most reliable "
        "custom-card loading, add it as a Lovelace resource of type 'module'.",
        CARD_JS_URL,
    )


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the ibepower domain (runs once, before any config entry)."""
    hass.data.setdefault(DOMAIN, {})

    # Serve www/ files via a custom view.
    hass.http.register_view(_IbepowerStaticView())

    if not await _async_register_lovelace_resource(hass):
        @callback
        def _register_cards_when_started(_event) -> None:
            hass.async_create_task(_async_finalize_card_registration(hass))

        hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STARTED, _register_cards_when_started
        )

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
