import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN
from .ibeplug_device import IBEPlugDevice
# from .ibediv_device import IBEDivDevice

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch", "sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    host = entry.data["host"]
    name = entry.data["name"]
    mac = entry.data.get("mac")
    version = entry.data.get("version", "1.0")
    device_type = entry.data["device_type"]

    if device_type == "ibeplug":
        device = IBEPlugDevice(host, name, mac, version)
    #elif device_type == "ibediv":
        # device = IBEDivDevice(host, name, mac, version)
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

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "device": device,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok