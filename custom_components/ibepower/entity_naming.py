from homeassistant.util import slugify


STATIC_SUFFIX_BY_UNIQUE_SUFFIX = {
    "switch": "ibeplug",
    "switch_on_off": "ibediv",
    "switch_screen": "screen",
    "pwm_value_setter": "manual",
    "brightness_value_setter": "brightness",
    "work_mode_select": "modo_de_trabajo",
    "reboot": "reiniciar_dispositivo",
    "update_firmware": "actualizar_firmware",
}


def get_device_slug(device_description):
    slug = slugify(device_description or "")
    return slug or "dispositivo"


def build_suggested_object_id(device_description, suffix):
    return f"{get_device_slug(device_description)}_{suffix}"


def get_object_suffix_from_unique_id(unique_id, mac, domain):
    if not mac or not unique_id:
        return None

    prefix = f"{mac}_"
    if not unique_id.startswith(prefix):
        return None

    unique_suffix = unique_id[len(prefix) :]

    if domain == "sensor":
        return unique_suffix

    return STATIC_SUFFIX_BY_UNIQUE_SUFFIX.get(unique_suffix)
