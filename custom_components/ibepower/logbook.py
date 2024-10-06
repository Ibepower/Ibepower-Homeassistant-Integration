from homeassistant.core import callback
from .const import DOMAIN

@callback
def async_describe_events(hass, async_describe_event):
    """Describe eventos para el registro (logbook)."""

    @callback
    def async_describe_firmware_update_event(event):
        """Describe un evento de actualización de firmware."""
        data = event.data
        entity_id = data.get("entity_id")
        message = data.get("message")
        return {
            "name": "Actualización de Firmware",
            "message": message,
            "entity_id": entity_id,
            "domain": DOMAIN,
        }

    async_describe_event(
        DOMAIN,
        f"{DOMAIN}_firmware_update",
        async_describe_firmware_update_event,
    )
