import aiohttp
import logging
import json

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class IBEPlugDevice:
    def __init__(self, hass, host, name, mac, version, description):
        self._hass = hass
        self._host = host
        self._name = name
        self._mac = mac
        self._version = version
        self._description = description
        self._port = 80
        self.is_on = False
        self.voltage = None
        self.consumption = None
        self.power = None
        self.kw_total = None
        self.kw_yesterday = None
        self.factor = None
        self.current = None
        self._entity_id = None
        self._latest_version = None

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

    async def async_update_data(self):
        url = f"http://{self._host}:{self._port}/cm?cmnd=Energy"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Error al obtener los datos del dispositivo {self._name}: {response.status}")
                        return
                    data = await response.json()

                    energy_data = data.get("ENERGY", {})
                    self.voltage = energy_data.get("Voltage")
                    self.consumption = energy_data.get("KwToday")
                    self.power = energy_data.get("Power")
                    self.kw_total = energy_data.get("KwTotal")
                    self.kw_yesterday = energy_data.get("KwYesterday")
                    self.factor = energy_data.get("Factor")
                    self.current = energy_data.get("Current")
                    self.is_on = energy_data.get("Relay") == "ON"

        except aiohttp.ClientError as error:
            _LOGGER.error(f"Error de conexión al dispositivo {self._name}: {error}")

    async def async_turn_on(self):
        return await self._send_command("Power", "1")

    async def async_turn_off(self):
        return await self._send_command("Power", "0")

    async def _send_command(self, command, value):
        url = f"http://{self._host}:{self._port}/cm?cmnd={command}%20{value}"
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
    
    async def reboot(self):
        return await self._send_command("restart", "1")

    async def update_firmware(self):
        """Comprueba si hay una nueva versión de firmware disponible."""
        update_endpoint = "https://www.ibepower.com/firmware/version_IBEPLUG"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(update_endpoint) as response:
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

                            return await self._send_command("doOTA", "1")
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
                                    "message": f"{self._name} ya está en la última versión de firmware. Versión actual: {self._version}",
                                    "entity_id": self._entity_id
                                }
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