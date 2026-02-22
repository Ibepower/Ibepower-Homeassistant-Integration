import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .entity_naming import build_suggested_object_id

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    data = hass.data[DOMAIN][config_entry.entry_id]
    device = data["device"]
    device_type = config_entry.data["device_type"]
    coordinator = data.get("coordinator")
    entry_entities = data.setdefault("entities", {})

    entities = []

    if device_type == "Ibeplug":
        switch_entity = IBEPlugSwitch(coordinator, device)
        entities.append(switch_entity)

        _LOGGER.debug("[SWITCH] Switch Name: %s, Switch Unique ID: %s", switch_entity.name, switch_entity.unique_id)

        entry_entities[switch_entity.unique_id] = switch_entity

    elif device_type == "Ibediv":
        div_entity = IBEDivSwitchOnOff(coordinator, device)
        screen_entity = IBEDivScreenSwitch(coordinator, device)
        entities.extend([div_entity, screen_entity])

        _LOGGER.debug("[SWITCH] Switch Name: %s, Switch Unique ID: %s", div_entity.name, div_entity.unique_id)
        _LOGGER.debug("[SWITCH] Switch Name: %s, Switch Unique ID: %s", screen_entity.name, screen_entity.unique_id)

        entry_entities[div_entity.unique_id] = div_entity
        entry_entities[screen_entity.unique_id] = screen_entity
    
    elif device_type == "Ibemeter":
        screen_entity = IBEMeterScreenSwitch(coordinator, device)
        entities.append(screen_entity)

        _LOGGER.debug("[SWITCH] Switch Name: %s, Switch Unique ID: %s", screen_entity.name, screen_entity.unique_id)

        entry_entities[screen_entity.unique_id] = screen_entity

    async_add_entities(entities)

####################################################################################################
################################## Ibeplug Switch Entity ###########################################
####################################################################################################

class IBEPlugSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = self._generate_name()
        self._attr_suggested_object_id = build_suggested_object_id(device.description, "ibeplug")

    @property
    def name(self):
        return self._attr_name
    
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
        self._attr_name = self._generate_name()
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
        self._attr_name = self._generate_name()
        self._attr_suggested_object_id = build_suggested_object_id(device.description, "ibediv")

    @property
    def name(self):
        return self._attr_name
    
    @property
    def unique_id(self):
        return f"{self._device.mac}_switch_on_off"

    @property
    def is_on(self):
        return self._device.diverter_is_on
    
    @property
    def icon(self):
        if self._device.diverter_is_on:
            return "mdi:power-cycle"
        else:
            return "mdi:power"
    
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
        self._attr_name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        return f"Ibediv ({self._device.description})"

    async def async_turn_on(self):
        previous_state = bool(self._device.diverter_is_on)
        self._device.diverter_is_on = True
        self.async_write_ha_state()
        response = await self._device.async_turn_on_diverter()
        if response is None:
            self._device.diverter_is_on = previous_state
            self.async_write_ha_state()
            return
        if self.coordinator:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        previous_state = bool(self._device.diverter_is_on)
        self._device.diverter_is_on = False
        self.async_write_ha_state()
        response = await self._device.async_turn_off_diverter()
        if response is None:
            self._device.diverter_is_on = previous_state
            self.async_write_ha_state()
            return
        if self.coordinator:
            await self.coordinator.async_request_refresh()

class IBEDivScreenSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = self._generate_name()
        self._attr_suggested_object_id = build_suggested_object_id(device.description, "screen")

    @property
    def name(self):
        return self._attr_name
    
    @property
    def unique_id(self):
        return f"{self._device.mac}_switch_screen"

    @property
    def is_on(self):
        return self._device.screen_is_on
    
    @property
    def icon(self):
        return "mdi:monitor"

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
        self._attr_name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        return f"Screen ({self._device.description})"
    
    async def async_turn_on(self):
        response = await self._device.async_turn_on_screen()
        self._device.screen_is_on = bool(response)
        self.async_write_ha_state()

    async def async_turn_off(self):
        response = await self._device.async_turn_off_screen()
        self._device.screen_is_on = not bool(response)
        self.async_write_ha_state()

####################################################################################################
################################## Ibemeter Switch Entity ##########################################
####################################################################################################

class IBEMeterScreenSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = self._generate_name()
        self._attr_suggested_object_id = build_suggested_object_id(device.description, "screen")

    @property
    def name(self):
        return self._attr_name
    
    @property
    def unique_id(self):
        return f"{self._device.mac}_switch_screen"

    @property
    def is_on(self):
        return self._device.screen_is_on
    
    @property
    def icon(self):
        return "mdi:monitor"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device.mac)},
            "name": self._device.name,
            "manufacturer": "Ibepower Technologies S.L.",
            "model": "Ibemeter",
            "sw_version": self._device.version,
            "connections": {("mac", self._device.mac)},
            "configuration_url": f"http://{self._device._host}:{self._device._port}",
        }
    
    def update_name(self):
        self._attr_name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        return f"Screen ({self._device.description})"
    
    async def async_turn_on(self):
        response = await self._device.async_turn_on_screen()
        self._device.screen_is_on = bool(response)
        self.async_write_ha_state()

    async def async_turn_off(self):
        response = await self._device.async_turn_off_screen()
        self._device.screen_is_on = not bool(response)
        self.async_write_ha_state()
