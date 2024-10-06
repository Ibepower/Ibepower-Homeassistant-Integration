import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory, DeviceInfo
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    data = hass.data[DOMAIN][config_entry.entry_id]
    device = data["device"]
    device_type = config_entry.data["device_type"]
    coordinator = data.get("coordinator")

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    buttons = [
        RebootDeviceButton(coordinator, device, device_type),
        UpdateFirmwareButton(coordinator, device, device_type),
    ]

    async_add_entities(buttons)

class RebootDeviceButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, device, device_type):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = "Reiniciar Dispositivo"
        self._attr_unique_id = f"{device.mac}_reboot"
        self._attr_icon = "mdi:restart"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = DeviceInfo(
            identifiers = {(DOMAIN, self._device.mac)},
            name = device.name,
            manufacturer = "Ibepower Technologies S.L.",
            model = device_type,
            sw_version = device.version,
        )

    async def async_press(self):
        await self._device.reboot()
        await self.coordinator.async_request_refresh()

class UpdateFirmwareButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, device, device_type):
        super().__init__(coordinator)
        self._device = device
        self._attr_name = "Actualizar Firmware"
        self._attr_unique_id = f"{device.mac}_update_firmware"
        self._attr_icon = "mdi:cloud-upload"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = DeviceInfo(
            identifiers = {(DOMAIN, self._device.mac)},
            name = device.name,
            manufacturer = "Ibepower Technologies S.L.",
            model = device_type,
            sw_version = device.version,
        )

    async def async_added_to_hass(self):
        self._device.set_entity_id(self.entity_id)

    async def async_press(self):
        await self._device.update_firmware()
        await self.coordinator.async_request_refresh()
