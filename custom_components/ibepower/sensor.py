import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    data = hass.data[DOMAIN][config_entry.entry_id]
    device = data["device"]
    device_type = config_entry.data["device_type"]
    coordinator = data.get("coordinator")

    entities = []

    if device_type == "ibeplug":
        entities.extend([
            IBEPlugVoltageSensor(coordinator, device),
            IBEPlugConsumptionSensor(coordinator, device),
            IBEPlugPowerSensor(coordinator, device),
            IBEPlugKwTotalSensor(coordinator, device),
            IBEPlugKwYesterdaySensor(coordinator, device),
            IBEPlugFactorSensor(coordinator, device),
            IBEPlugCurrentSensor(coordinator, device),
        ])
    #elif device_type == "ibediv":

    async_add_entities(entities)

class IBEPlugSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, device, name, unit, icon, unique_id):
        super().__init__(coordinator)
        self._device = device
        self._name = name
        self._unit = unit
        self._icon = icon
        self._unique_id = unique_id

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def icon(self):
        return self._icon

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device.mac)},
            "name": self._device.name,
            "manufacturer": "Ibepower Technologies S.L.",
            "model": "Ibeplug",
            "sw_version": self._device.version,
        }

class IBEPlugVoltageSensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        name = f"{device.name} Voltage"
        unit = "V"
        icon = "mdi:flash"
        unique_id = f"{device.mac}_voltage"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.voltage

class IBEPlugConsumptionSensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        name = f"{device.name} KwToday"
        unit = "kWh"
        icon = "mdi:power-plug"
        unique_id = f"{device.mac}_kwtoday"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.consumption

class IBEPlugPowerSensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        name = f"{device.name} Power"
        unit = "W"
        icon = "mdi:flash-outline"
        unique_id = f"{device.mac}_power"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.power

class IBEPlugKwTotalSensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        name = f"{device.name} KwTotal"
        unit = "kWh"
        icon = "mdi:counter"
        unique_id = f"{device.mac}_kwtotal"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.kw_total

class IBEPlugKwYesterdaySensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        name = f"{device.name} KwYesterday"
        unit = "kWh"
        icon = "mdi:calendar-arrow-left"
        unique_id = f"{device.mac}_kwyesterday"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.kw_yesterday

class IBEPlugFactorSensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        name = f"{device.name} Power Factor"
        unit = "%"
        icon = "mdi:cosine-wave"
        unique_id = f"{device.mac}_factor"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.factor

class IBEPlugCurrentSensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        name = f"{device.name} Current"
        unit = "A"
        icon = "mdi:current-ac"
        unique_id = f"{device.mac}_current"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.current
