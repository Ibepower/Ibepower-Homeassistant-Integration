import aiohttp
import logging
import json
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)


def _format_error(error: Exception) -> str:
    message = str(error).strip()
    return message or error.__class__.__name__

class IBEDivDevice:
    def __init__(self, hass, host, name, mac, version, description):
        self._hass = hass
        self._host = host
        self._name = name
        self._mac = mac
        self._version = version
        self._description = description
        self._port = 80
        self.device_data = {}
        self._entity_id = None
        self.diverter_is_on = False
        self.screen_is_on = False
        self._latest_version = None
        self.last_restart = None
        
        self.heap_memory = None
        self.pwm_enabled = False
        self.work_mode = None
        self.pwm_value = None
        self.calculated_watts = None
        self.work_mode_name = None
        self.master_mode_name = None
        self.temp_shutdown = None
        self.chip_temperature = None
        self.manualControlPercentage = None
        self.brightnessPercentage = None

        # Energía solar, red, batería
        self.solar_watts = None
        self.grid_watts = None
        self.grid_voltage = None
        self.grid_current = None
        self.grid_frequency = None
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
        
        self._session = None

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
    
    @property
    def host(self):
        return self._host

    @description.setter
    def description(self, value):
        self._description = value
    
    @name.setter
    def name(self, value):
        self._name = value
    
    @version.setter
    def version(self, value):
        self._version = value
    
    @host.setter
    def host(self, value):
        self._host = value
    
    def set_entity_id(self, entity_id):
        self._entity_id = entity_id

    async def async_init_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=REQUEST_TIMEOUT)

    async def async_close_session(self):
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def async_update_data(self):
        await self.async_init_session()
        url = f"http://{self._host}:{self._port}/cmnd?cmnd={{\"command\":\"Status\"}}"
        try:
            async with self._session.get(url, timeout=REQUEST_TIMEOUT) as response:
                if response.status != 200:
                    raise UpdateFailed(
                        f"Error al obtener los datos del dispositivo {self._name}: {response.status}"
                    )
                self.device_data = await response.json()

                self.pwm_enabled = self.device_data.get("pwmE")
                self.diverter_is_on = self.device_data.get("pwmE")
                self.screen_is_on = self.device_data.get("scrE")
                self.manualControlPercentage = self.device_data.get("mCP")
                self.brightnessPercentage = self.device_data.get("bP")
                
                self.heap_memory = self.device_data.get("Heap")
                self.work_mode = self.device_data.get("wM")
                self.pwm_value = self.device_data.get("pwmV")
                self.calculated_watts = self.device_data.get("hW")
                self.work_mode_name = self.device_data.get("wMN")
                self.master_mode_name = self.device_data.get("mMN")
                self.temp_shutdown = self.device_data.get("tSD")
                self.chip_temperature = self.device_data.get("cT")

                # Energía solar, red, batería
                self.solar_watts = self.device_data.get("sW")
                self.grid_watts = self.device_data.get("gW")
                self.grid_voltage = self.device_data.get("gV")
                self.grid_current = self.device_data.get("gC")
                self.grid_frequency = self.device_data.get("gF")
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
                self.last_restart = self.device_data.get("lRST")
                return self.device_data

        except (aiohttp.ClientError, TimeoutError) as error:
            raise UpdateFailed(
                f"Error de conexión al dispositivo {self._name}: {_format_error(error)}"
            ) from error

    async def async_turn_on_diverter(self):
        return await self._send_command("pwm", "1")

    async def async_turn_off_diverter(self):
        return await self._send_command("pwm", "0")

    async def async_turn_on_screen(self):
        return await self._send_command("screenOnOff", "1")
    
    async def async_turn_off_screen(self):
        return await self._send_command("screenOnOff", "0")
    
    async def async_select_work_mode(self, mode):
        if mode == "AUTO":
            payload = "0"
        elif mode == "MANUAL":
            payload = "1"
        else:
            _LOGGER.error("Modo de trabajo no soportado: %s", mode)
            return None
        
        return await self._send_command("pwmman", payload)

    async def async_set_pwm_value(self, value):
        return await self._send_command("setManualControlPercentage", value)
    
    async def async_set_brightness_value(self, value):
        return await self._send_command("brightness", value)

    async def _send_command(self, command, value):
        await self.async_init_session()
        url = f"http://{self._host}:{self._port}/cmnd?cmnd={{\"command\":\"{command}\",\"payload\":\"{value}\"}}"
        try:
            async with self._session.get(url, timeout=REQUEST_TIMEOUT) as response:
                if response.status != 200:
                    _LOGGER.error(f"Error al enviar el comando {command} al dispositivo {self._name}: {response.status}")
                    return None
                data = await response.json()
                _LOGGER.debug(f"Comando {command} enviado con éxito, respuesta: {data}")
                return data
        except (aiohttp.ClientError, TimeoutError) as error:
            _LOGGER.error(
                f"Error de conexión al enviar el comando {command} al dispositivo {self._name}: {_format_error(error)}"
            )
            return None
    
    async def reboot(self):
        return await self._send_command("restart", "1")

    async def update_firmware(self):
        """Comprueba si hay una nueva versión de firmware disponible."""
        update_endpoint = "https://www.ibepower.com/firmware/version_IBEDIV"
        await self.async_init_session()
        try:
            async with self._session.get(update_endpoint, timeout=REQUEST_TIMEOUT) as response:
                if response.status == 200:
                    text = await response.text()
                    data = json.loads(text)
                    self._latest_version = data.get("version")

                    if self._latest_version != self._version:
                        await self._hass.services.async_call(
                            "persistent_notification",
                            "create",
                            {
                                "title": "Actualización de Firmware",
                                "message": f"Se ha detectado una nueva versión de firmware: {self._latest_version}. Iniciando actualización."
                            }
                        )

                        self._hass.bus.async_fire(
                            f"{DOMAIN}_firmware_update",
                            {
                                "message": f"Se ha detectado una nueva versión de firmware: {self._latest_version}. Iniciando actualización.",
                                "entity_id": self._entity_id
                            }
                        )

                        return await self._send_command("otaUpdate", "1")
                    else:
                        await self._hass.services.async_call(
                            "persistent_notification",
                            "create",
                            {
                                "title": "Actualización de Firmware",
                                "message": f"{self._name} ya está en la última versión de firmware. Versión actual: {self._version}"
                            }
                        )

                        self._hass.bus.async_fire(
                            f"{DOMAIN}_firmware_update",
                            {
                                "entity_id": self._entity_id,
                                "message": f"{self._name} ya está en la última versión de firmware. Versión actual: {self._version}",
                            },
                        )
                else:
                    await self._hass.services.async_call(
                        "persistent_notification",
                        "create",
                        {
                            "title": "Actualización de Firmware",
                            "message": f"Error al consultar el endpoint de actualización: {response.status}"
                        }
                    )
                    
                    self._hass.bus.async_fire(
                        f"{DOMAIN}_firmware_update",
                        {
                            "message": f"Error al consultar el endpoint de actualización: {response.status}",
                            "entity_id": self._entity_id
                        }
                    )
                    
        except Exception as e:
            await self._hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Actualización de Firmware",
                    "message": f"Excepción al consultar el endpoint de actualización: {e}"
                }
            )

            self._hass.bus.async_fire(
                f"{DOMAIN}_firmware_update",
                {
                    "message": f"Error al consultar el endpoint de actualización: {e}",
                    "entity_id": self._entity_id
                }
            )
