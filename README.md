
# Ibepower Home Assistant Integration

![Ibepower Logo](https://ibepower.com/wp-content/uploads/2023/09/marca-horizontal_color-300x80.png)

### A custom integration to control and monitor **Ibepower** smart devices in [Home Assistant](https://www.home-assistant.io/). This integration supports multiple device types, including **Ibeplug**, and allows you to control relays, monitor power consumption, and get real-time energy data.

---

## Features

- **Control Relays**: Turn on/off smart plugs and other relays.
- **Monitor Power Consumption**: Get detailed power usage data including total energy, power factor, voltage, and current.
- **Real-Time Updates**: Receive real-time updates based on device response, ensuring fast and accurate state changes.
- **Multiple Device Support**: Supports various devices from Ibepower, starting with the **Ibeplug** smart plug.

---

## Installation

### Manual Installation

1. **Download the integration:**

   Clone the repository or download the ZIP file:

   ```bash
   git clone https://github.com/ibepower/ibepower-homeassistant-integration.git
   ```

2. **Copy files to Home Assistant:**

   - Place the contents of the `ibepower` folder inside the `custom_components` directory of your Home Assistant configuration folder.

     Your directory structure should look like this:

     ```bash
     └── custom_components
         └── ibepower
             ├── __init__.py
             ├── const.py
             ├── sensor.py
             ├── switch.py
             ├── config_flow.py
             ├── ibeplug_device.py
             └── manifest.json
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

## Troubleshooting

- **Devices not being discovered**: Ensure your devices are connected to the same network as Home Assistant and that mDNS is enabled on your router.
- **State changes delayed**: The integration attempts to retrieve real-time state from the devices after sending a command. If delays persist, try lowering the `update_interval` in the integration code.
- **Device errors**: Check the Home Assistant logs for errors related to device communication.

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

![Device Example](screenshot1.png)

---

Made with ❤️ by [Ibepower](https://github.com/Ibepower).
