import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

class IBEPlugDevice:
    def __init__(self, host, name, mac, version):
        self._host = host
        self._name = name
        self._mac = mac
        self._version = version
        self._port = 80
        self.is_on = False
        self.voltage = None
        self.consumption = None
        self.power = None
        self.kw_total = None
        self.kw_yesterday = None
        self.factor = None
        self.current = None

    @property
    def name(self):
        return self._name

    @property
    def mac(self):
        return self._mac
    
    @property
    def version(self):
        return self._version

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