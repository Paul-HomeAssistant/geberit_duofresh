# Geberit DuoFresh

Custom Home Assistant integration for Geberit DuoFresh.

This integration allows Home Assistant to monitor a Geberit DuoFresh device and expose its data as Home Assistant sensors.

> [!NOTE]
> This is a custom integration and is not affiliated with, endorsed by, or officially supported by Geberit.

## Features

- Adds Geberit DuoFresh support to Home Assistant
- Configuration through the Home Assistant UI
- Sensor entities for available DuoFresh data
- Uses Home Assistant's DataUpdateCoordinator pattern
- Compatible with HACS as a custom repository

## Installation

### HACS

This integration can be installed through HACS as a custom repository.

1. Open Home Assistant.
2. Go to **HACS**.
3. Go to **Integrations**.
4. Click the three dots in the top-right corner.
5. Select **Custom repositories**.
6. Add this repository URL:

       https://github.com/Paul-HomeAssistant/geberit_duofresh

7. Select category:

       Integration

8. Click **Add**.
9. Search for **Geberit DuoFresh** in HACS.
10. Install the integration.
11. Restart Home Assistant.

### Manual installation

1. Download or clone this repository.
2. Copy the folder:

       custom_components/geberit_duofresh

   to your Home Assistant configuration directory:

       /config/custom_components/geberit_duofresh

3. Restart Home Assistant.

The final folder structure should look like this:

    /config/custom_components/geberit_duofresh/
    ├── __init__.py
    ├── config_flow.py
    ├── const.py
    ├── coordinator.py
    ├── manifest.json
    ├── sensor.py
    ├── strings.json
    └── translations/

## Configuration

After installation and restart:

1. Go to **Settings**.
2. Open **Devices & services**.
3. Click **Add integration**.
4. Search for **Geberit DuoFresh**.
5. Follow the setup flow.

## Requirements

The required Python dependencies are defined in:

    custom_components/geberit_duofresh/manifest.json

Make sure your Home Assistant version is compatible with the minimum version defined in `hacs.json`.

## Updating

When installed through HACS, updates will be shown in HACS when a new version is available.

After updating the integration, restart Home Assistant.

## Troubleshooting

If the integration does not appear in Home Assistant:

- Make sure Home Assistant was restarted after installation.
- Check that the integration is located at:

      /config/custom_components/geberit_duofresh/

- Verify that `manifest.json` contains the correct domain:

      geberit_duofresh

- Check the Home Assistant logs for errors.
- Make sure all required dependencies from `manifest.json` are installed correctly.

If the integration appears but setup fails:

- Verify that the device is reachable from Home Assistant.
- Check the configuration values entered in the setup flow.
- Enable debug logging if needed.

Example debug logging configuration:

    logger:
      default: warning
      logs:
        custom_components.geberit_duofresh: debug

## Repository structure

    custom_components/
    └── geberit_duofresh/
        ├── __init__.py
        ├── config_flow.py
        ├── const.py
        ├── coordinator.py
        ├── manifest.json
        ├── sensor.py
        ├── strings.json
        └── translations/

## Reporting issues

If you experience issues, please open an issue on GitHub:

    https://github.com/Paul-HomeAssistant/geberit_duofresh/issues

When reporting an issue, include:

- Home Assistant version
- Integration version
- Relevant log output
- A clear description of the problem
- Steps to reproduce the issue

## Disclaimer

This project is not affiliated with, endorsed by, or officially supported by Geberit.

Use this integration at your own risk.

## License

See the repository license file.
