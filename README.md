
# Ibepower Home Assistant Integration

<p align="center">
  <img src="https://raw.githubusercontent.com/Ibepower/Ibepower-Homeassistant-Integration/main/images/Ibepower.png">
</p>

### A custom integration to control and monitor **Ibepower** smart devices in [Home Assistant](https://www.home-assistant.io/). This integration supports multiple device types, including **Ibeplug**, and allows you to control relays, monitor power consumption, and get real-time energy data.

---

## Features

- **Control Relays**: Turn on/off smart plugs and other relays.
- **Monitor Power Consumption**: Get detailed power usage data including total energy, power factor, voltage, and current.
- **Real-Time Updates**: Receive real-time updates based on device response, ensuring fast and accurate state changes.
- **Multiple Device Support**: Supports various devices from Ibepower, starting with the **Ibeplug** smart plug.

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

     ```bash
     └── custom_components
         └── ibepower
             ├── __init__.py
             ├── config_flow.py
             ├── const.py
             ├── ibediv_device.py
             ├── ibeplug_device.py
             ├── manifest.json
             ├── number.py
             ├── select.py
             ├── sensor.py
             └── switch.py
     ```

3. **Restart Home Assistant:**

   - After copying the files, restart Home Assistant for the integration to be loaded.

---

## Configuration

### 1. **Discover Devices Automatically**

   After restarting Home Assistant, the integration will automatically discover compatible Ibepower devices using mDNS. You can find and configure these devices via the Home Assistant interface under **Settings > Devices & Services**.

### 2. **Manual Configuration**

   If you need to configure a device manually, you can go to **Settings > Devices & Services > Add Integration**, and search for **Ibepower**. You will be prompted to enter the device details. (In developement)

---

## Example of Supported Devices

### **1. Ibeplug Smart Plug**
   The integration supports **Ibeplug**, a smart plug with relay control and power monitoring features.

   - **Relay Control**: Turn on/off the plug.
   - **Energy Monitoring**: Monitor voltage, current, power, total energy, and power factor.

---

## Energy Data Collected

| Sensor         | Description                       | Unit   |
|----------------|-----------------------------------|--------|
| Voltage        | The voltage of the device         | V      |
| Current        | Current flowing through the plug  | A      |
| Power          | Active power being consumed       | W      |
| Total Energy   | Total energy consumed             | kWh    |
| Power Factor   | Efficiency of energy usage        | %      |
| Energy Today   | Total energy used today           | kWh    |
| Energy Yesterday| Total energy used yesterday      | kWh    |

---

## Future Features

- Support for additional Ibepower devices (e.g., Ibediv, Ibemeter).
- Enhanced energy tracking and reporting.

---

## Dashboard Cards (Graphs + Animations)

### Single-device cards by device type (recommended, no summary sensors)

Use one file per device type:

- `examples/lovelace/ibepower_ibeplug_device_card.yaml`
- `examples/lovelace/ibepower_ibediv_device_card.yaml`
- `examples/lovelace/ibepower_ibemeter_device_card.yaml`
- `examples/lovelace/ibepower_ibediv_energy_flow_card.yaml`
- `examples/lovelace/ibepower_ibemeter_energy_flow_card.yaml`

Requirements (HACS):

- `config-template-card`
- `button-card`
- `apexcharts-card`

How to use:

1. Open the file that matches your device type.
2. Change only the base variable (`variables: - "'<base_slug>'"`) in the card header.
3. The card resolves entities with your current pattern: `sensor.<base_slug>_<field>`.
4. Paste into your dashboard view (YAML mode).

Optional tuning:

1. In each card, use `variables.hidden_fields` to hide any sensor field without deleting blocks.
2. Keep `base_slug` equal to the device name suffix used in your current entities (example: `calentador`).

---

## Entity Naming Convention And Migration

To keep entity naming coherent across platforms (`sensor`, `switch`, `number`, `select`, `button`) and reduce naming drift between old/new installs, follow the canonical convention and migration guide:

- `docs/entity_naming_convention_es.md`

The guide includes:

- Canonical naming rules
- Legacy-to-canonical entity mapping
- Steps to preserve history
- SQL fallback to recover merged history if needed

---

## Troubleshooting

- **Devices not being discovered**: Ensure your devices are connected to the same network as Home Assistant and that mDNS is enabled on your router.
- **State changes delayed**: The integration attempts to retrieve real-time state from the devices after sending a command. If delays persist, try lowering the `update_interval` in the integration code.
- **Device errors**: Check the Home Assistant logs for errors related to device communication.

---

## Release (VS Code tasks)

Two release tasks are available in VS Code (`Terminal -> Run Task`):

1. `HACS: Build release ZIP`
   - Generates `dist/ibepower_integration.zip` using `hacs.json` filename.
   - Packages `custom_components/` and excludes Python cache artifacts.

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

