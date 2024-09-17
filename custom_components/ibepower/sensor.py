import logging
from homeassistant.components.sensor import SensorEntity
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
        power_sensor = IBEPlugPowerSensor(coordinator, device)
        voltage_sensor = IBEPlugVoltageSensor(coordinator, device)
        current_sensor = IBEPlugCurrentSensor(coordinator, device)
        today_sensor = IBEPlugTodaySensor(coordinator, device)
        kw_yesterday_sensor = IBEPlugKwYesterdaySensor(coordinator, device)
        kw_total_sensor = IBEPlugKwTotalSensor(coordinator, device)
        factor_sensor = IBEPlugFactorSensor(coordinator, device)

        entities.extend([
            power_sensor,
            voltage_sensor,
            current_sensor,
            today_sensor,
            kw_yesterday_sensor,
            kw_total_sensor,
            factor_sensor,
        ])

        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        
        hass.data[DOMAIN][power_sensor.unique_id] = power_sensor
        hass.data[DOMAIN][voltage_sensor.unique_id] = voltage_sensor
        hass.data[DOMAIN][current_sensor.unique_id] = current_sensor
        hass.data[DOMAIN][today_sensor.unique_id] = today_sensor
        hass.data[DOMAIN][kw_yesterday_sensor.unique_id] = kw_yesterday_sensor
        hass.data[DOMAIN][kw_total_sensor.unique_id] = kw_total_sensor
        hass.data[DOMAIN][factor_sensor.unique_id] = factor_sensor
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
        _LOGGER.debug("Sensor Name: %s, Sensor Unit: %s, Sensor Icon: %s, Sensor Unique ID: %s", name, unit, icon, unique_id)

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
    
    def update_name(self):
        self._name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        raise NotImplementedError("Implementado en la subclase")


class IBEPlugVoltageSensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        self._device = device
        name = self._generate_name()
        unit = "V"
        icon = "mdi:flash"
        unique_id = f"{device.mac}_voltage"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.voltage

    def update_name(self):
        self._name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        return f"Voltage ({self._device.description})"

class IBEPlugTodaySensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        self._device = device
        name = self._generate_name()
        unit = "kWh"
        icon = "mdi:power-plug"
        unique_id = f"{device.mac}_kwtoday"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.consumption

    def update_name(self):
        self._name = self._generate_name()
        self.async_write_ha_state()
    
    def _generate_name(self):
        return f"KwToday ({self._device.description})"

class IBEPlugPowerSensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        self._device = device
        name = self._generate_name()
        unit = "W"
        icon = "mdi:flash-outline"
        unique_id = f"{device.mac}_power"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.power
    
    def update_name(self):
        self._name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        return f"Power ({self._device.description})"

class IBEPlugKwTotalSensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        self._device = device
        name = self._generate_name()
        unit = "kWh"
        icon = "mdi:counter"
        unique_id = f"{device.mac}_kwtotal"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.kw_total
    
    def update_name(self):
        self._name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        return f"KwTotal ({self._device.description})"

class IBEPlugKwYesterdaySensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        self._device = device
        name = self._generate_name()
        unit = "kWh"
        icon = "mdi:calendar-arrow-left"
        unique_id = f"{device.mac}_kwyesterday"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.kw_yesterday
    
    def update_name(self):
        self._name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        return f"KwYesterday ({self._device.description})"

class IBEPlugFactorSensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        self._device = device
        name = self._generate_name()
        unit = "%"
        icon = "mdi:cosine-wave"
        unique_id = f"{device.mac}_factor"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.factor
    
    def update_name(self):
        self._name = self._generate_name()
        self.async_write_ha_state()
    
    def _generate_name(self):
        return f"Power Factor ({self._device.description})"

class IBEPlugCurrentSensor(IBEPlugSensor):

    def __init__(self, coordinator, device):
        self._device = device
        name = self._generate_name()
        unit = "A"
        icon = "mdi:current-ac"
        unique_id = f"{device.mac}_current"
        super().__init__(coordinator, device, name, unit, icon, unique_id)

    @property
    def state(self):
        return self._device.current

    def update_name(self):
        self._name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        return f"Current ({self._device.description})"
