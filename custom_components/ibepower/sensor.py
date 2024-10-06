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

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if device_type == "Ibeplug":

        sensor_definitions_ibeplug = {
            "voltage": {"name": "Voltage", "unit": "V", "icon": "mdi:flash", "field": "voltage"},
            "kwtoday": {"name": "KwToday", "unit": "kWh", "icon": "mdi:power-plug", "field": "consumption"},
            "power": {"name": "Power", "unit": "W", "icon": "mdi:flash-outline", "field": "power"},
            "kwtotal": {"name": "KwTotal", "unit": "kWh", "icon": "mdi:counter", "field": "kw_total"},
            "kwyesterday": {"name": "KwYesterday", "unit": "kWh", "icon": "mdi:calendar-arrow-left", "field": "kw_yesterday"},
            "factor": {"name": "Power Factor", "unit": "%", "icon": "mdi:cosine-wave", "field": "factor"},
            "current": {"name": "Current", "unit": "A", "icon": "mdi:current-ac", "field": "current"},
        }

        for sensor_info in sensor_definitions_ibeplug.values():
            sensor_ibeplug_entity = IBEPlugSensor(
                        coordinator=coordinator,
                        device=device,
                        name=sensor_info["name"],
                        unit=sensor_info["unit"],
                        icon=sensor_info["icon"],
                        field=sensor_info["field"]
                    )

            entities.append(sensor_ibeplug_entity)

            _LOGGER.debug("[SENSOR] Sensor Name: %s, Sensor Unique_ID: %s, Sensor Unit: %s, Sensor Icon: %s, Sensor Field: %s", sensor_ibeplug_entity.name, sensor_ibeplug_entity.unique_id, sensor_ibeplug_entity.unit_of_measurement, sensor_ibeplug_entity.icon, sensor_info["field"])

            hass.data[DOMAIN][sensor_ibeplug_entity.unique_id] = sensor_ibeplug_entity

    elif device_type == "Ibediv":
        _LOGGER.debug("Ibediv Device Type: %s", device_type)

        sensor_definitions_ibediv = {
            # Estado del sistema y configuración
            "Heap": {"name": "Heap Memory", "unit": "bytes", "icon": "mdi:memory", "field": "heap_memory", "visible": False},
            "pwmE": {"name": "Ibediv Enabled", "unit": None, "icon": "mdi:toggle-switch", "field": "pwm_enabled", "visible": True},
            "wM": {"name": "Work Mode", "unit": None, "icon": "mdi:car-cruise-control", "field": "work_mode", "visible": True},
            "pwmV": {"name": "Output Value", "unit": "%", "icon": "mdi:gauge", "field": "pwm_value", "visible": True},
            "hW": {"name": "Output Watts", "unit": "W", "icon": "mdi:water-boiler", "field": "calculated_watts", "visible": True},
            "wMN": {"name": "Work Mode Name", "unit": None, "icon": "mdi:information", "field": "work_mode_name", "visible": False},
            "mMN": {"name": "Master Mode Name", "unit": None, "icon": "mdi:account-supervisor", "field": "master_mode_name", "visible": False},
            "tSD": {"name": "Temperature Shutdown", "unit": None, "icon": "mdi:thermometer-alert", "field": "temp_shutdown", "visible": False},
            "uPT": {"name": "Uptime", "unit": None, "icon": "mdi:timer", "field": "uptime", "visible": False},
            "cT": {"name": "Chip Temperature", "unit": "°C", "icon": "mdi:thermometer", "field": "chip_temperature", "visible": False},

            # Energía solar, red, batería
            "sW": {"name": "Solar Watts", "unit": "W", "icon": "mdi:solar-power-variant-outline", "field": "solar_watts", "visible": True},
            "gW": {"name": "Grid Watts", "unit": "W", "icon": "mdi:transmission-tower", "field": "grid_watts", "visible": True},
            "gV": {"name": "Grid Voltage", "unit": "V", "icon": "mdi:sine-wave", "field": "grid_voltage", "visible": True},
            "bV": {"name": "Battery Voltage", "unit": "V", "icon": "mdi:battery", "field": "battery_voltage", "visible": True},
            "bA": {"name": "Battery Current", "unit": "A", "icon": "mdi:current-dc", "field": "battery_current", "visible": True},
            "bW": {"name": "Battery Power", "unit": "W", "icon": "mdi:battery-charging", "field": "battery_power", "visible": True},
            "SoC": {"name": "Battery SoC", "unit": "%", "icon": "mdi:battery-high", "field": "battery_soc", "visible": True},
            "lW": {"name": "Load Watts", "unit": "W", "icon": "mdi:home-lightning-bolt-outline", "field": "load_watts", "visible": True},
            "tW": {"name": "Today Watts", "unit": "W", "icon": "mdi:calendar-today", "field": "today_watts", "visible": True},

            # Datos de energía solar (PV)
            "p1A": {"name": "PV1 Current", "unit": "A", "icon": "mdi:current-dc", "field": "pv1_current", "visible": False},
            "p1V": {"name": "PV1 Voltage", "unit": "V", "icon": "mdi:flash", "field": "pv1_voltage", "visible": False},
            "p1W": {"name": "PV1 Power", "unit": "W", "icon": "mdi:solar-power", "field": "pv1_power", "visible": False},
            "p2A": {"name": "PV2 Current", "unit": "A", "icon": "mdi:current-dc", "field": "pv2_current", "visible": False},
            "p2V": {"name": "PV2 Voltage", "unit": "V", "icon": "mdi:flash", "field": "pv2_voltage", "visible": False},
            "p2W": {"name": "PV2 Power", "unit": "W", "icon": "mdi:solar-power", "field": "pv2_power", "visible": False},

            # Datos de temperatura
            "iTmp": {"name": "Inverter Temperature", "unit": "°C", "icon": "mdi:sun-thermometer", "field": "internal_temperature", "visible": False},
            "tT": {"name": "Thermo Temperature", "unit": "°C", "icon": "mdi:water-thermometer", "field": "thermo_temperature", "visible": False},
            "tI": {"name": "Ibepower Temperature", "unit": "°C", "icon": "mdi:thermometer", "field": "ibepower_temperature", "visible": False},
            "tC": {"name": "Custom Temperature", "unit": "°C", "icon": "mdi:thermometer", "field": "custom_temperature", "visible": False},
            "tTN": {"name": "Thermo Sensor Name", "unit": None, "icon": "mdi:thermometer", "field": "thermo_sensor_name", "visible": False},
            "tCN": {"name": "Custom Sensor Name", "unit": None, "icon": "mdi:thermometer", "field": "custom_sensor_name", "visible": False},

            # Energía: diverter, importación, exportación
            "KwDT": {"name": "Kw Diverter Today", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_diverter_today", "visible": False},
            "KwDY": {"name": "Kw Diverter Yesterday", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_diverter_yesterday", "visible": False},
            "KwDM": {"name": "Kw Diverter Month", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_diverter_month", "visible": False},
            "KwDLM": {"name": "Kw Diverter Last Month", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_diverter_last_month", "visible": False},
            "KwDYR": {"name": "Kw Diverter Year", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_diverter_year", "visible": False},
            "KwDLYR": {"name": "Kw Diverter Last Year", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_diverter_last_year", "visible": False},
            "KwDTT": {"name": "Kw Diverter Total", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_diverter_total", "visible": False},

            # Energía importada
            "KwT": {"name": "Kw Import Today", "unit": "kWh", "icon": "mdi:transmission-tower-import", "field": "kw_import_today", "visible": False},
            "KwY": {"name": "Kw Import Yesterday", "unit": "kWh", "icon": "mdi:transmission-tower-import", "field": "kw_import_yesterday", "visible": False},
            "KwM": {"name": "Kw Import Month", "unit": "kWh", "icon": "mdi:transmission-tower-import", "field": "kw_import_month", "visible": False},
            "KwLM": {"name": "Kw Import Last Month", "unit": "kWh", "icon": "mdi:transmission-tower-import", "field": "kw_import_last_month", "visible": False},
            "KwYR": {"name": "Kw Import Year", "unit": "kWh", "icon": "mdi:transmission-tower-import", "field": "kw_import_year", "visible": False},
            "KwLYR": {"name": "Kw Import Last Year", "unit": "kWh", "icon": "mdi:transmission-tower-import", "field": "kw_import_last_year", "visible": False},
            "KwTT": {"name": "Kw Import Total", "unit": "kWh", "icon": "mdi:transmission-tower-import", "field": "kw_import_total", "visible": False},

            # Energía exportada
            "KwET": {"name": "Kw Export Today", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_export_today", "visible": False},
            "KwEY": {"name": "Kw Export Yesterday", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_export_yesterday", "visible": False},
            "KwEM": {"name": "Kw Export Month", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_export_month", "visible": False},
            "KwELM": {"name": "Kw Export Last Month", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_export_last_month", "visible": False},
            "KwEYR": {"name": "Kw Export Year", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_export_year", "visible": False},
            "KwELYR": {"name": "Kw Export Last Year", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_export_last_year", "visible": False},
            "KwETT": {"name": "Kw Export Total", "unit": "kWh", "icon": "mdi:transmission-tower-export", "field": "kw_export_total", "visible": False},

            # Energía solar
            "KwST": {"name": "Kw Solar Today", "unit": "kWh", "icon": "mdi:solar-power", "field": "kw_solar_today", "visible": False},
            "KwSY": {"name": "Kw Solar Yesterday", "unit": "kWh", "icon": "mdi:solar-power", "field": "kw_solar_yesterday", "visible": False},
            "KwSM": {"name": "Kw Solar Month", "unit": "kWh", "icon": "mdi:solar-power", "field": "kw_solar_month", "visible": False},
            "KwSLM": {"name": "Kw Solar Last Month", "unit": "kWh", "icon": "mdi:solar-power", "field": "kw_solar_last_month", "visible": False},
            "KwSYR": {"name": "Kw Solar Year", "unit": "kWh", "icon": "mdi:solar-power", "field": "kw_solar_year", "visible": False},
            "KwSLYR": {"name": "Kw Solar Last Year", "unit": "kWh", "icon": "mdi:solar-power", "field": "kw_solar_last_year", "visible": False},
            "KwSTT": {"name": "Kw Solar Total", "unit": "kWh", "icon": "mdi:solar-power", "field": "kw_solar_total", "visible": False},
        }

        for field, sensor_info in sensor_definitions_ibediv.items():
            if field in device.device_data:
                sensor_ibediv_entity = IBEDivSensor(
                        coordinator=coordinator,
                        device = device,
                        name = sensor_info["name"],
                        unit = sensor_info["unit"],
                        icon = sensor_info["icon"],
                        unique_id = f"{device.mac}_{sensor_info['field']}",
                        field = sensor_info["field"],
                        visible = sensor_info["visible"]
                    )
                
                entities.append(sensor_ibediv_entity)

                _LOGGER.debug("[SENSOR] Sensor Name: %s, Sensor Unique_ID: %s, Sensor Unit: %s, Sensor Icon: %s, Sensor Unique ID: %s, Sensor Field: %s, visible: %s", sensor_ibediv_entity.name, sensor_ibediv_entity.unique_id, sensor_ibediv_entity.unit_of_measurement, sensor_info["field"], sensor_info["visible"])

                hass.data[DOMAIN][sensor_ibediv_entity.unique_id] = sensor_ibediv_entity


    async_add_entities(entities)

####################################################################################################
################################### Ibeplug Sensor Entity ##########################################
####################################################################################################

class IBEPlugSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device, name, unit, icon, field):
        super().__init__(coordinator)
        self._device = device
        self._base_name = name
        self._name = self._generate_name()
        self._unit = unit
        self._icon = icon
        self._field = field
        
    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        # return self._unique_id
        return f"{self._device.mac}_{self._field}"

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def icon(self):
        return self._icon
    
    @property
    def state(self):
        return getattr(self._device, self._field, None)

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
        self._name = self._generate_name()
        self.async_write_ha_state()

    def _generate_name(self):
        # return f"{self._name} ({self._device.description})"
        # return f"{self._base_name} ({self._device.description})"
        return f"{self._base_name}"

####################################################################################################
################################### Ibediv Sensor Entity ###########################################
####################################################################################################

class IBEDivSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, device, name, unit, icon, unique_id, field, visible):
        super().__init__(coordinator)
        self._device = device
        self._base_name = name
        self._name = self._generate_name()
        self._unit = unit
        self._icon = icon
        self._unique_id = unique_id
        self._state = None
        self._field = field
        self._visible = visible

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
    def state(self):
        return getattr(self._device, self._field, None)
    
    @property
    def entity_registry_enabled_default(self) -> bool:
        return self._visible

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
        return f"{self._base_name}"

