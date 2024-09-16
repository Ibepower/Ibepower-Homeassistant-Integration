import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    data = hass.data[DOMAIN][config_entry.entry_id]
    device = data["device"]
    device_type = config_entry.data["device_type"]
    coordinator = data.get("coordinator")

    entities = []

    if device_type == "ibeplug":
        entities.append(IBEPlugSwitch(coordinator, device))
    # elif device_type == "ibediv":

    async_add_entities(entities)

class IBEPlugSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device

    @property
    def name(self):
        return self._device.name
    
    @property
    def unique_id(self):
        return f"{self._device.mac}_switch"

    @property
    def is_on(self):
        return self._device.is_on
    
    @property
    def icon(self):
        return "mdi:power-socket-eu"
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device.mac)},
            "name": self._device.name,
            "manufacturer": "Ibepower Technologies S.L.",
            "model": "Ibeplug",
            "sw_version": self._device.version,
        }

    async def async_turn_on(self):
        response = await self._device.async_turn_on()
        if response and response.get("POWER") == "ON":
            self._device.is_on = True
        else:
            self._device.is_on = False

        self.async_write_ha_state()

    async def async_turn_off(self):
        response = await self._device.async_turn_off()
        if response and response.get("POWER") == "OFF":
            self._device.is_on = False
        else:
            self._device.is_on = True

        self.async_write_ha_state()
