import logging
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    data = hass.data[DOMAIN][config_entry.entry_id]
    device = data["device"]
    device_type = config_entry.data["device_type"]
    coordinator = data.get("coordinator")

    entities = []

    if device_type == "Ibediv":

        div_entity = IBEDivSelect(coordinator, device)
        
        entities.append(div_entity)

        _LOGGER.debug("[SELECT] Select Name: %s, Select Unique ID: %s", div_entity.name, div_entity.unique_id)

        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}

        hass.data[DOMAIN][div_entity.unique_id] = div_entity

    async_add_entities(entities)

####################################################################################################
################################### Ibediv Select Entity ###########################################
####################################################################################################

class IBEDivSelect(CoordinatorEntity, SelectEntity):

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_options = ["AUTO", "MANUAL"]
        self._attr_current_option = self.get_current_option()
        self._name = self._generate_name()

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"{self._device.mac}_work_mode_select"
    
    @property
    def icon(self):
        return "mdi:transfer"

    @property
    def options(self):
        return self._attr_options
    
    @property
    def current_option(self):
        return self.get_current_option()
    
    def get_current_option(self):
        work_mode = self._device.work_mode
        _LOGGER.debug("get_current_option called. Device work_mode: %s", work_mode)
        if work_mode == "MAN":
            current_option = "MANUAL"
        else:
            current_option = "AUTO"
        _LOGGER.debug("get_current_option returning: %s", current_option)
        return current_option

    
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
        self._name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        return f"Modo de trabajo ({self._device.description})"
        #return "Modo de trabajo"
    
    async def async_select_option(self, option: str):
        _LOGGER.debug("async_select_option called with option: %s", option)
        if option in self._attr_options:
            await self._device.async_select_work_mode(option)
            _LOGGER.debug("Option %s sent to device", option)
            self.async_write_ha_state()
        else:
            _LOGGER.error(
                "Invalid option selected: %s (valid options: %s)", option, self._attr_options
        )