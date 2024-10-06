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

    if device_type == "Ibeplug":
        switch_entity = IBEPlugSwitch(coordinator, device)
        entities.append(switch_entity)

        _LOGGER.debug("[SWITCH] Switch Name: %s, Switch Unique ID: %s", switch_entity.name, switch_entity.unique_id)

        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}

        hass.data[DOMAIN][switch_entity.unique_id] = switch_entity

    elif device_type == "Ibediv":
        div_entity = IBEDivSwitchOnOff(coordinator, device)
        entities.append(div_entity)

        _LOGGER.debug("[SWITCH] Switch Name: %s, Switch Unique ID: %s", div_entity.name, div_entity.unique_id)

        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}

        hass.data[DOMAIN][div_entity.unique_id] = div_entity

    async_add_entities(entities)

####################################################################################################
################################## Ibeplug Switch Entity ###########################################
####################################################################################################

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
            "connections": {("mac", self._device.mac)},
            "configuration_url": f"http://{self._device._host}:{self._device._port}",
        }
    
    def update_name(self):
        self._device.name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        return f"Ibeplug ({self._device.description})"

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

####################################################################################################
################################### Ibediv Switch Entity ###########################################
####################################################################################################

class IBEDivSwitchOnOff(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device

    @property
    def name(self):
        return self._device.name
    
    @property
    def unique_id(self):
        return f"{self._device.mac}_switch_on_off"

    @property
    def is_on(self):
        return self._device.diverter_is_on
    
    @property
    def icon(self):
        return "mdi:power-standby"
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device.mac)},
            "name": self._device.name,
            "manufacturer": "Ibepower Technologies S.L.",
            "model": "Ibediv",
            "sw_version": self._device.version,
            "connections": {("mac", self._device.mac)},
            "configuration_url": f"http://{self._device._host}:{self._device._port}",
        }
    
    def update_name(self):
        self._device.name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        return f"Ibediv ({self._device.description})"

    async def async_turn_on(self):
        response = await self._device.async_turn_on_diverter()
        if response and response.get("pwm") == "ON":
            self._device.diverter_is_on = True
        else:
            self._device.diverter_is_on = False

        self.async_write_ha_state()

    async def async_turn_off(self):
        response = await self._device.async_turn_off_diverter()
        if response and response.get("pwm") == "OFF":
            self._device.diverter_is_on = False
        else:
            self._device.diverter_is_on = True

        self.async_write_ha_state()