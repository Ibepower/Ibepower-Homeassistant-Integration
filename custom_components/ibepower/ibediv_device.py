import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

class IBEDivDevice:
    def __init__(self, host, name, mac, version, description):
        self._host = host
        self._name = name
        self._mac = mac
        self._version = version
        self._description = description
        self._port = 80
        self.device_data = {}
        self.diverter_is_on = False
        
        self.heap_memory = None
        self.pwm_enabled = False
        self.work_mode = None
        self.pwm_value = None
        self.calculated_watts = None
        self.work_mode_name = None
        self.master_mode_name = None
        self.temp_shutdown = None
        self.uptime = None
        self.chip_temperature = None
        self.manualControlPercentage = None

        # Energía solar, red, batería
        self.solar_watts = None
        self.grid_watts = None
        self.grid_voltage = None
        self.battery_voltage = None
        self.battery_current = None
        self.battery_power = None
        self.battery_soc = None
        self.load_watts = None
        self.today_watts = None

        # Energía solar (PV)
        self.pv1_current = None
        self.pv1_voltage = None
        self.pv1_power = None
        self.pv2_current = None
        self.pv2_voltage = None
        self.pv2_power = None

        # Temperaturas
        self.inverter_temperature = None
        self.thermo_temperature = None
        self.ibepower_temperature = None
        self.custom_temperature = None
        self.thermo_sensor_name = None
        self.custom_sensor_name = None

        # Datos de energía: diverter, importación, exportación
        self.kw_diverter_today = None
        self.kw_diverter_yesterday = None
        self.kw_diverter_month = None
        self.kw_diverter_last_month = None
        self.kw_diverter_year = None
        self.kw_diverter_last_year = None
        self.kw_diverter_total = None

        # Energía importada
        self.kw_import_today = None
        self.kw_import_yesterday = None
        self.kw_import_month = None
        self.kw_import_last_month = None
        self.kw_import_year = None
        self.kw_import_last_year = None
        self.kw_import_total = None

        # Energía exportada
        self.kw_export_today = None
        self.kw_export_yesterday = None
        self.kw_export_month = None
        self.kw_export_last_month = None
        self.kw_export_year = None
        self.kw_export_last_year = None
        self.kw_export_total = None

        # Energía solar
        self.kw_solar_today = None
        self.kw_solar_yesterday = None
        self.kw_solar_month = None
        self.kw_solar_last_month = None
        self.kw_solar_year = None
        self.kw_solar_last_year = None
        self.kw_solar_total = None
        

    @property
    def name(self):
        return self._name

    @property
    def mac(self):
        return self._mac
    
    @property
    def version(self):
        return self._version
    
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
    
    @name.setter
    def name(self, value):
        self._name = value

    async def async_update_data(self):
        url = f"http://{self._host}:{self._port}/cmnd?cmnd={{\"command\":\"Status\"}}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Error al obtener los datos del dispositivo {self._name}: {response.status}")
                        return
                    self.device_data = await response.json()

                    self.pwm_enabled = self.device_data.get("pwmE")
                    self.diverter_is_on = self.device_data.get("pwmE")
                    self.manualControlPercentage = self.device_data.get("mCP")
                    
                    self.heap_memory = self.device_data.get("Heap")
                    self.work_mode = self.device_data.get("wM")
                    self.pwm_value = self.device_data.get("pwmV")
                    self.calculated_watts = self.device_data.get("hW")
                    self.work_mode_name = self.device_data.get("wMN")
                    self.master_mode_name = self.device_data.get("mMN")
                    self.temp_shutdown = self.device_data.get("tSD")
                    self.uptime = self.device_data.get("uPT")
                    self.chip_temperature = self.device_data.get("cT")

                    # Energía solar, red, batería
                    self.solar_watts = self.device_data.get("sW")
                    self.grid_watts = self.device_data.get("gW")
                    self.grid_voltage = self.device_data.get("gV")
                    self.battery_voltage = self.device_data.get("bV")
                    self.battery_current = self.device_data.get("bA")
                    self.battery_power = self.device_data.get("bW")
                    self.battery_soc = self.device_data.get("SoC")
                    self.load_watts = self.device_data.get("lW")
                    self.today_watts = self.device_data.get("tW")

                    # Energía solar (PV)
                    self.pv1_current = self.device_data.get("p1A")
                    self.pv1_voltage = self.device_data.get("p1V")
                    self.pv1_power = self.device_data.get("p1W")
                    self.pv2_current = self.device_data.get("p2A")
                    self.pv2_voltage = self.device_data.get("p2V")
                    self.pv2_power = self.device_data.get("p2W")

                    # Temperaturas
                    self.inverter_temperature = self.device_data.get("iTmp")
                    self.thermo_temperature = self.device_data.get("tT")
                    self.ibepower_temperature = self.device_data.get("tI")
                    self.custom_temperature = self.device_data.get("tC")
                    self.thermo_sensor_name = self.device_data.get("tTN")
                    self.custom_sensor_name = self.device_data.get("tCN")

                    # Datos de energía: diverter, importación, exportación
                    self.kw_diverter_today = self.device_data.get("KwDT")
                    self.kw_diverter_yesterday = self.device_data.get("KwDY")
                    self.kw_diverter_month = self.device_data.get("KwDM")
                    self.kw_diverter_last_month = self.device_data.get("KwDLM")
                    self.kw_diverter_year = self.device_data.get("KwDYR")
                    self.kw_diverter_last_year = self.device_data.get("KwDLYR")
                    self.kw_diverter_total = self.device_data.get("KwDTT")

                    # Energía importada
                    self.kw_import_today = self.device_data.get("KwT")
                    self.kw_import_yesterday = self.device_data.get("KwY")
                    self.kw_import_month = self.device_data.get("KwM")
                    self.kw_import_last_month = self.device_data.get("KwLM")
                    self.kw_import_year = self.device_data.get("KwYR")
                    self.kw_import_last_year = self.device_data.get("KwLYR")
                    self.kw_import_total = self.device_data.get("KwTT")

                    # Energía exportada
                    self.kw_export_today = self.device_data.get("KwET")
                    self.kw_export_yesterday = self.device_data.get("KwEY")
                    self.kw_export_month = self.device_data.get("KwEM")
                    self.kw_export_last_month = self.device_data.get("KwELM")
                    self.kw_export_year = self.device_data.get("KwEYR")
                    self.kw_export_last_year = self.device_data.get("KwELYR")
                    self.kw_export_total = self.device_data.get("KwETT")

                    # Energía solar
                    self.kw_solar_today = self.device_data.get("KwST")
                    self.kw_solar_yesterday = self.device_data.get("KwSY")
                    self.kw_solar_month = self.device_data.get("KwSM")
                    self.kw_solar_last_month = self.device_data.get("KwSLM")
                    self.kw_solar_year = self.device_data.get("KwSYR")
                    self.kw_solar_last_year = self.device_data.get("KwSLYR")
                    self.kw_solar_total = self.device_data.get("KwSTT")

        except aiohttp.ClientError as error:
            _LOGGER.error(f"Error de conexión al dispositivo {self._name}: {error}")

    async def async_turn_on_diverter(self):
        return await self._send_command("pwm", "1")

    async def async_turn_off_diverter(self):
        return await self._send_command("pwm", "0")
    
    async def async_select_work_mode(self, mode):
        if mode == "AUTO":
            payload = "0"
        elif mode == "MANUAL":
            payload = "1"
        
        return await self._send_command("pwmman", payload)

    async def async_set_pwm_value(self, value):
        return await self._send_command("setManualControlPercentage", value)

    async def _send_command(self, command, value):
        url = f"http://{self._host}:{self._port}/cmnd?cmnd={{\"command\":\"{command}\",\"payload\":\"{value}\"}}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Error al enviar el comando {command} al dispositivo {self._name}: {response.status}")
                        return None
                    data = await response.json()
                    _LOGGER.debug(f"Comando {command} enviado con éxito, respuesta: {data}")
                    return data
        except aiohttp.ClientError as error:
            _LOGGER.error(f"Error de conexión al enviar el comando {command} al dispositivo {self._name}: {error}")
            return None