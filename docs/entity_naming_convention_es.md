# Convencion De Nombres De Entidades (Ibepower)

## Objetivo

Mantener los nombres visibles (`friendly_name`) tal y como estan hoy, y unificar solo `entity_id` para facilitar busqueda por dispositivo.

## Regla De Entity ID

Nuevo formato:

- `<dominio>.<slug_dispositivo>_<sufijo_entidad>`

Ejemplos:

- `sensor.calentador_battery_current`
- `sensor.calentador_output_watts`
- `switch.calentador_ibediv`
- `button.calentador_actualizar_firmware`

## Nombres Visibles

No se cambian por esta normalizacion. Se mantienen como:

- `Battery Current (calentador)`
- `Output Watts (calentador)`
- `Modo de trabajo (calentador)`
- `Reiniciar Dispositivo (calentador)`

## Mapeo Legado -> Nuevo

- `sensor.battery_current_calentador` -> `sensor.calentador_battery_current`
- `sensor.output_watts_calentador` -> `sensor.calentador_output_watts`
- `sensor.output_value_calentador` -> `sensor.calentador_output_value`
- `sensor.last_restart_time_calentador` -> `sensor.calentador_last_restart`
- `switch.ibediv_calentador` -> `switch.calentador_ibediv`
- `switch.screen_calentador` -> `switch.calentador_screen`
- `number.manual_calentador` -> `number.calentador_manual`
- `number.brightness_calentador` -> `number.calentador_brightness`
- `select.modo_de_trabajo_calentador` -> `select.calentador_modo_de_trabajo`
- `button.reiniciar_dispositivo_calentador` -> `button.calentador_reiniciar_dispositivo`
- `button.actualizar_firmware_calentador` -> `button.calentador_actualizar_firmware`

## Historico

Para no perder historico:

1. Se conserva `unique_id` de todas las entidades.
2. La migracion se hace sobre `entity_registry` (renombrado), no recreando entidades.
3. Home Assistant mantiene la continuidad de historial/estadisticas al renombrar via registro.

## Si Una Estadistica Queda Separada

Si algun caso puntual queda partido, fusionar en DB con Home Assistant parado y backup previo:

- `states_meta.entity_id`
- `statistics_meta.statistic_id`
