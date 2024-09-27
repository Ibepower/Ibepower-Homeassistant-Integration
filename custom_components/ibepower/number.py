import logging
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.number import NumberEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    data = hass.data[DOMAIN][config_entry.entry_id]
    device = data["device"]
    device_type = config_entry.data["device_type"]
    coordinator = data.get("coordinator")

    entities = []

    if device_type == "ibediv":

        div_manual_slider = IBEDivManualSlider(coordinator, device)
        
        entities.append(div_manual_slider)

        _LOGGER.debug("[SLIDER] Slider Name: %s, Slider Unique ID: %s", div_manual_slider._attr_name, div_manual_slider.unique_id)

        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}

        hass.data[DOMAIN][div_manual_slider.unique_id] = div_manual_slider

    async_add_entities(entities)

####################################################################################################
################################### Ibediv Number Entity ###########################################
####################################################################################################

class IBEDivManualSlider(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = self._generate_name()
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"
        self._attr_native_value = self._device.manualControlPercentage

    @property
    def label(self) -> str:
        return "prueba etiqueta"
    
    @property
    def name(self):
        return self._generate_name()

    @property
    def unique_id(self):
        return f"{self._device.mac}_pwm_value_setter"

    @property
    def native_value(self) -> int | None:
        return self._device.manualControlPercentage
    
    @property
    def mode(self) -> str:
        return "auto" # "auto", "slider", "box"

    async def async_set_native_value(self, value: int):
        await self._device.async_set_pwm_value(value)
        self._attr_value = value
        self.async_write_ha_state()

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
        # return f"{self._name} ({self._device.description})"
        return "Manual (%)"