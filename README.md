
# Ibepower Home Assistant Integration

<p align="center">
  <img src="https://raw.githubusercontent.com/Ibepower/Ibepower-Homeassistant-Integration/main/images/Ibepower.png">
</p>

### A custom integration to control and monitor **Ibepower** smart devices in [Home Assistant](https://www.home-assistant.io/). Supports **IBEPlug**, **IBEDiv** and **IBEMeter** with automatic device discovery, custom Lovelace cards, energy flow visualizations and multilingual UI (ES/EN/PT).

---

## Features

- **Three Device Types**: IBEPlug (smart plug), IBEDiv (solar diverter), IBEMeter (grid meter).
- **Control Relays & Diverters**: Turn on/off smart plugs, diverters and screens.
- **Monitor Power & Energy**: Detailed real-time data — voltage, current, power, power factor, solar, grid, battery and load.
- **Energy History**: Today, yesterday, month, year and total counters for import, export, solar and diverter energy.
- **Custom Lovelace Cards**: Built-in cards that appear automatically in the HA card picker — no extra HACS frontend dependencies required.
- **Energy Flow Diagrams**: Animated solar → grid → home (and battery/diverter) flow visualization for IBEDiv and IBEMeter.
- **Automatic Discovery**: Devices are detected via mDNS/Zeroconf on the local network.
- **Multilingual**: Cards and picker descriptions in Spanish, English and Portuguese.
- **Firmware Updates**: One-click firmware check and OTA update from the device page.
- **Disabled Entities**: Many advanced sensors (PV arrays, temperatures, historical energy counters) are created but disabled by default — enable only the ones you need.

---

## Supported Devices

### 1. IBEPlug — Smart Plug

Smart socket with relay control and energy monitoring.

| Entity           | Type     | Description                    |
|------------------|----------|--------------------------------|
| Ibeplug switch   | `switch` | Turn relay on/off              |
| Voltage          | `sensor` | Grid voltage (V)               |
| Current          | `sensor` | Current draw (A)               |
| Power            | `sensor` | Active power (W)               |
| Power Factor     | `sensor` | Efficiency (%)                 |
| Energy Today     | `sensor` | Consumption today (kWh)        |
| Energy Yesterday | `sensor` | Consumption yesterday (kWh)    |
| Energy Total     | `sensor` | Cumulative consumption (kWh)   |
| Reboot           | `button` | Restart device                 |
| Update Firmware  | `button` | Check & apply OTA update       |

### 2. IBEDiv — Solar Diverter

Advanced solar energy diverter with battery support, multi-mode operation and extensive monitoring.

**Visible by default:**

| Entity                                   | Type     | Description                      |
|------------------------------------------|----------|----------------------------------|
| Ibediv switch                            | `switch` | Enable/disable diverter (PWM)    |
| Screen switch                            | `switch` | Toggle device display            |
| Work Mode                                | `select` | AUTO / MANUAL mode               |
| Manual Control                           | `number` | PWM output percentage (0–100 %)  |
| Brightness                               | `number` | Screen brightness (0–100 %)      |
| Solar Watts                              | `sensor` | Current solar generation (W)     |
| Grid Watts                               | `sensor` | Grid import/export (W, signed)   |
| Grid Voltage / Current / Frequency       | `sensor` | Grid parameters                  |
| Battery Voltage / Current / Power / SoC  | `sensor` | Battery status                   |
| Load Watts                               | `sensor` | Home load (W)                    |
| Output Value / Output Watts              | `sensor` | Diverter output                  |
| Reboot / Update Firmware                 | `button` | Device actions                   |

**Disabled by default** (see [Enabling Hidden Entities](#enabling-hidden-entities)):

| Entity                                                            | Description             |
|-------------------------------------------------------------------|-------------------------|
| PV1 Voltage / Current / Power                                     | First PV array data     |
| PV2 Voltage / Current / Power                                     | Second PV array data    |
| Inverter / Thermo / Ibepower / Custom Temperature                 | Temperature probes      |
| Thermo Sensor Name / Custom Sensor Name                           | Probe labels            |
| Chip Temperature / Heap Memory                                    | Diagnostic data         |
| Work Mode Name / Master Mode Name                                 | Internal mode labels    |
| Temperature Shutdown                                              | Shutdown status         |
| Kw Diverter Today/Yesterday/Month/Last Month/Year/Last Year/Total | Diverter energy history |
| Kw Import Today/Yesterday/Month/Last Month/Year/Last Year/Total   | Import energy history   |
| Kw Export Today/Yesterday/Month/Last Month/Year/Last Year/Total   | Export energy history   |
| Kw Solar Today/Yesterday/Month/Last Month/Year/Last Year/Total    | Solar energy history    |

### 3. IBEMeter — Grid Meter

Dedicated grid metering and solar monitoring device.

**Visible by default:**

| Entity                                      | Type     | Description                 |
|---------------------------------------------|----------|-----------------------------|
| Screen switch                               | `switch` | Toggle device display       |
| Brightness                                  | `number` | Screen brightness (0–100 %) |
| Solar Watts / Solar Current                 | `sensor` | Solar generation            |
| Grid Watts / Voltage / Current / Frequency  | `sensor` | Grid parameters             |
| Reboot / Update Firmware                    | `button` | Device actions              |

**Disabled by default** (see [Enabling Hidden Entities](#enabling-hidden-entities)):

| Entity                                                          | Description           |
|-----------------------------------------------------------------|-----------------------|
| Chip Temperature / Heap Memory                                  | Diagnostic data       |
| Kw Import Today/Yesterday/Month/Last Month/Year/Last Year/Total | Import energy history |
| Kw Export Today/Yesterday/Month/Last Month/Year/Last Year/Total | Export energy history |
| Kw Solar Today/Yesterday/Month/Last Month/Year/Last Year/Total  | Solar energy history  |

---

## Installation

### HACS Installation

1. **Add Custom Repository:**

   - Open HACS in Home Assistant.
   - Go to **Integrations**.
   - Click on the three dots in the top right corner and select **Custom repositories**.
   - Add the repository URL: `https://github.com/Ibepower/Ibepower-Homeassistant-Integration` and select the category **Integration**.

2. **Install the Integration:**

   - Search for **Ibepower Home Assistant Integration** in HACS.
   - Click on **Install** and wait for the installation to complete.

3. **Restart Home Assistant:**

   - After the installation, restart Home Assistant to load the new integration.

### Manual Installation

1. **Download the integration:**

   Clone the repository or download the ZIP file:

   ```bash
   git clone https://github.com/Ibepower/Ibepower-Homeassistant-Integration.git
   ```

2. **Copy files to Home Assistant:**

   - Place the contents of the `ibepower` folder inside the `custom_components` directory of your Home Assistant configuration folder.

     Your directory structure should look like this:

     ```
     └── custom_components
         └── ibepower
             ├── __init__.py
             ├── button.py
             ├── config_flow.py
             ├── const.py
             ├── entity_naming.py
             ├── ibediv_device.py
             ├── ibemeter_device.py
             ├── ibeplug_device.py
             ├── logbook.py
             ├── manifest.json
             ├── number.py
             ├── select.py
             ├── sensor.py
             ├── switch.py
             └── www/
                 └── ibepower-cards.js
     ```

3. **Restart Home Assistant:**

   - After copying the files, restart Home Assistant for the integration to be loaded.

---

## Configuration

### 1. **Automatic Discovery**

   After restarting Home Assistant, the integration automatically discovers compatible Ibepower devices using mDNS/Zeroconf:

   | Service                  | Device   |
   |--------------------------|----------|
   | `_ibeplug._tcp.local.`   | IBEPlug  |
   | `_ibediv._tcp.local.`    | IBEDiv   |
   | `_ibemeter._tcp.local.`  | IBEMeter |

   Found devices appear under **Settings > Devices & Services**. Accept the discovered device to add it.

## Enabling Hidden Entities

Many sensors for IBEDiv and IBEMeter are created **disabled by default** to keep the UI clean. These include PV array data, temperature probes, and historical energy counters (yesterday, month, year, total, etc.).

To enable them so they appear in dashboards and the custom cards:

1. Go to **Settings > Devices & Services > Ibepower**.
2. Click on the device (e.g. your IBEDiv or IBEMeter).
3. At the bottom of the device page, look for the count of disabled entities and click the link (e.g. _"X entities not shown"_).
4. Click on the entity you want to enable.
5. In the entity detail, click the **gear icon** ⚙️ and toggle **Enabled** to **on**.
6. Confirm and wait for the next update cycle (≈10 seconds).

Alternatively, you can enable entities from **Settings > Devices & Services > Entities**, filter by device, and enable them in bulk.

> **Tip:** Only enable the entities you actually need. The custom Lovelace cards automatically display any entity that is available — once you enable a sensor, it will appear in the corresponding card on the next refresh.

---

## Custom Lovelace Cards

The integration ships with built-in Lovelace cards (`ibepower-cards.js`) that appear **automatically in the Home Assistant card picker** — no extra HACS frontend components needed.

On dashboards managed in Home Assistant Storage mode, the integration auto-registers the cards as a Lovelace resource of type `module`.

If your installation manages Lovelace resources in YAML, add this manually:

```yaml
lovelace:
  resources:
    - url: /ibepower_static/ibepower-cards.js
      type: module
```

### Available Cards

| Card                  | Type tag                  | Description                                                                                             |
|-----------------------|---------------------------|---------------------------------------------------------------------------------------------------------|
| **Ibepower Ibeplug**  | `ibepower-ibeplug-card`   | Smart plug with power gauge, ON/OFF toggle, voltage/current/factor metrics and energy tracking          |
| **Ibepower Ibediv**   | `ibepower-ibediv-card`    | Energy diverter with animated solar/grid/battery/diverter flow diagram, manager controls and PWM slider |
| **Ibepower Ibemeter** | `ibepower-ibemeter-card`  | Grid meter with animated solar/grid/home flow diagram and grid metrics                                  |

### How to Add a Card

1. Edit your dashboard and click **Add Card**.
2. Search for **Ibepower** in the card picker.
3. Select the card that matches your device type.
4. In the card editor, choose a specific device from the dropdown or leave on **Auto** to auto-detect:
   - **Auto**: The card discovers all devices of its type and shows a dropdown to switch between them.
   - **Specific device**: Pin the card to one device (the dropdown disappears).
5. Save.

No YAML editing is required. The cards are fully visual and interactive:

- **IBEPlug card**: Click the plug icon to toggle ON/OFF. Click any metric to open its history dialog.
- **IBEDiv card**: Animated flow lines show energy direction between solar, grid, battery, home and diverter nodes. Diverter controls (mode selector, PWM slider) are built into the card.
- **IBEMeter card**: Animated flow lines show energy direction between solar, grid and home.

### Card Features

- **Auto-detection**: Cards find devices automatically by model.
- **Multi-device dropdown**: If you have multiple devices of the same type, switch between them from the card.
- **Multilingual**: Automatically adapts to Spanish, English or Portuguese based on your HA / browser language.
- **Peak power tracking** (IBEPlug): Calculates a representative peak from the last 30 days of history, shown as a progress bar.
- **Responsive layout**: Adapts to narrow columns and mobile screens.
- **Click-to-details**: Click any metric to open the HA more-info dialog with history graphs.
- **Self-healing**: If the card script loads after Lovelace renders, it automatically triggers a rebuild — no manual refresh needed.

### Legacy YAML Cards

Example YAML card files are still available in `examples/lovelace/` for users who prefer manual YAML configuration with `config-template-card`, `button-card` and `apexcharts-card`:

- `ibepower_ibeplug_card.yaml` / `ibepower_ibeplug_card_auto.yaml`
- `ibepower_ibediv_card.yaml` / `ibepower_ibediv_card_auto.yaml`
- `ibepower_ibemeter_card.yaml` / `ibepower_ibemeter_card_auto.yaml`

---

## Troubleshooting

- **Devices not being discovered**: Ensure your devices are connected to the same network as Home Assistant and that mDNS is enabled on your router.
- **State changes delayed**: The integration polls devices every 10 seconds. If delays persist, check network connectivity to the device.
- **Card not appearing in picker**: Restart Home Assistant after installing/updating the integration. In Storage mode the integration auto-registers `/ibepower_static/ibepower-cards.js` as a Lovelace `module` resource. In YAML mode you must declare that resource manually.
- **Entities showing "unavailable"**: The device may be offline or its IP may have changed. Check the device page under **Settings > Devices & Services**.
- **Hidden sensors not in card**: Enable them first (see [Enabling Hidden Entities](#enabling-hidden-entities)). The cards only show entities that exist and are enabled.
- **Device errors**: Check the Home Assistant logs (**Settings > System > Logs**) for errors related to `ibepower`.

---

## Release (VS Code tasks)

Two release tasks are available in VS Code (`Terminal -> Run Task`):

1. `HACS: Build release ZIP`
   - Generates `dist/ibepower_integration.zip` using `hacs.json` filename.
   - Packages the content of `custom_components/ibepower` at ZIP root with Linux-compatible permissions and excludes Python cache artifacts.

2. `HACS: Publish release (auto patch bump)`
   - Automatically bumps `custom_components/ibepower/manifest.json` version (`patch`).
   - Creates commit and tag (`vX.Y.Z`), pushes both to GitHub, creates release, and uploads the ZIP.

3. `HACS: Publish release (auto minor bump)`
   - Same flow as publish task but bumps `minor`.

4. `HACS: Publish release (auto major bump)`
   - Same flow as publish task but bumps `major`.

5. `HACS: Upload ZIP to existing tag`
   - Builds the HACS ZIP and uploads/replaces it in an already existing release tag.
   - Useful when tag exists but the release asset upload failed.

Requirements for publish task:
- `git` installed and authenticated to push.
- One of the following:
   - `gh` (GitHub CLI) installed and authenticated (`gh auth login`), or
   - `GITHUB_TOKEN` (or `GH_TOKEN`) environment variable with repository permissions (release + contents write).
- If `gh` and env token are both missing, the script asks for the token interactively in the terminal.
- The entered token is stored encrypted (Windows user profile, DPAPI) and reused automatically in next executions.
- Clean working tree before running publish.

---

## Contributing

Contributions are welcome! If you have ideas or want to improve this integration, feel free to create a pull request or open an issue in the GitHub repository.

1. Fork the repository.
2. Create a new branch: `git checkout -b my-new-feature`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin my-new-feature`.
5. Submit a pull request.

---

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

## Support

For any issues or questions, feel free to open an issue in the GitHub repository or contact [soporte@ibepower.com](mailto:soporte@ibepower.com).

---

## Screenshots

<p align="center">
  <img src="https://raw.githubusercontent.com/Ibepower/Ibepower-Homeassistant-Integration/main/images/HACS%20Card.png">
</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/Ibepower/Ibepower-Homeassistant-Integration/main/images/HACS%20Integration%20List.png">
</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/Ibepower/Ibepower-Homeassistant-Integration/main/images/HACS%20Integration%20Devices.png">
</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/Ibepower/Ibepower-Homeassistant-Integration/main/images/HACS%20Ibeplug%20Info.png">
</p>

---

Made with ❤️ by [Ibepower](https://github.com/Ibepower).

