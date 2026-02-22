import logging
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.number import NumberEntity

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

    if device_type == "Ibediv":

        div_manual_slider = IBEDivManualSlider(coordinator, device)
        div_brightness_slider = IBEDivBrightnessSlider(coordinator, device)
        
        entities.extend([div_manual_slider, div_brightness_slider])

        _LOGGER.debug("[SLIDER] Slider Name: %s, Slider Unique ID: %s", div_manual_slider._attr_name, div_manual_slider.unique_id)
        _LOGGER.debug("[SLIDER] Slider Name: %s, Slider Unique ID: %s", div_brightness_slider._attr_name, div_brightness_slider.unique_id)

        entry_entities[div_manual_slider.unique_id] = div_manual_slider
        entry_entities[div_brightness_slider.unique_id] = div_brightness_slider
    
    elif device_type == "Ibemeter":

        meter_brightness_slider = IBEMeterBrightnessSlider(coordinator, device)
        
        entities.append(meter_brightness_slider)

        _LOGGER.debug("[SLIDER] Slider Name: %s, Slider Unique ID: %s", meter_brightness_slider._attr_name, meter_brightness_slider.unique_id)

        entry_entities[meter_brightness_slider.unique_id] = meter_brightness_slider


    async_add_entities(entities)

####################################################################################################
################################### Ibediv Number Entity ###########################################
####################################################################################################

class IBEDivManualSlider(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = self._generate_name()
        self._attr_suggested_object_id = build_suggested_object_id(device.description, "manual")
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"
        self._attr_native_value = self._device.manualControlPercentage
    
    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return f"{self._device.mac}_pwm_value_setter"

    @property
    def native_value(self) -> int | None:
        return self._attr_native_value
    
    @property
    def mode(self) -> str:
        return "slider" # "auto", "slider", "box"

    async def async_set_native_value(self, value: int):
        value = int(round(value))
        # Optimistic update so the UI reflects the dragged value immediately.
        self._attr_native_value = value
        self._device.manualControlPercentage = value
        self.async_write_ha_state()
        await self._device.async_set_pwm_value(value)

    def _handle_coordinator_update(self) -> None:
        latest = self._device.manualControlPercentage
        if latest is not None:
            self._attr_native_value = int(round(latest))
        super()._handle_coordinator_update()

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
        return f"Manual (%) ({self._device.description})"

class IBEDivBrightnessSlider(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = self._generate_name()
        self._attr_suggested_object_id = build_suggested_object_id(device.description, "brightness")
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"
        self._attr_native_value = self._device.brightnessPercentage
    
    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return f"{self._device.mac}_brightness_value_setter"

    @property
    def native_value(self) -> int | None:
        return self._attr_native_value
    
    @property
    def mode(self) -> str:
        return "slider" # "auto", "slider", "box"

    async def async_set_native_value(self, value: int):
        value = int(round(value))
        self._attr_native_value = value
        self._device.brightnessPercentage = value
        self.async_write_ha_state()
        await self._device.async_set_brightness_value(value)

    def _handle_coordinator_update(self) -> None:
        latest = self._device.brightnessPercentage
        if latest is not None:
            self._attr_native_value = int(round(latest))
        super()._handle_coordinator_update()

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
        return f"Brightness (%) ({self._device.description})"

####################################################################################################
################################## Ibemeter Number Entity ##########################################
####################################################################################################

class IBEMeterBrightnessSlider(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = self._generate_name()
        self._attr_suggested_object_id = build_suggested_object_id(device.description, "brightness")
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"
        self._attr_native_value = self._device.brightnessPercentage
    
    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return f"{self._device.mac}_brightness_value_setter"

    @property
    def native_value(self) -> int | None:
        return self._attr_native_value
    
    @property
    def mode(self) -> str:
        return "slider" # "auto", "slider", "box"

    async def async_set_native_value(self, value: int):
        value = int(round(value))
        self._attr_native_value = value
        self._device.brightnessPercentage = value
        self.async_write_ha_state()
        await self._device.async_set_brightness_value(value)

    def _handle_coordinator_update(self) -> None:
        latest = self._device.brightnessPercentage
        if latest is not None:
            self._attr_native_value = int(round(latest))
        super()._handle_coordinator_update()

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
        return f"Brightness (%) ({self._device.description})"
