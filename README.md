# PiWeatherRock

![GitHub](https://img.shields.io/github/license/carloshm/PiWeatherRock)

PiWeatherRock displays local weather on (almost) any screen you connect to a Raspberry Pi. It also works on other platforms, including macOS.

## Weather API

This project uses the [Open-Meteo API](https://open-meteo.com/) to fetch weather data. Open-Meteo is a free, open-source weather API that does not require an API key for non-commercial use.

> **Note:** Previous versions of PiWeatherRock used the [Dark Sky API](https://darksky.net/), which was shut down. The project has been migrated to use Open-Meteo as a drop-in replacement. The internal data format still follows the Dark Sky structure for backward compatibility, with the `openmeteo.py` module handling the translation between APIs.

### Configuration

Weather settings are configured in `piweatherrock/piweatherrock-config.json`:

- `ds_api_key`: Identifier for the Open-Meteo request (no real API key needed). The name is a legacy reference from the Dark Sky era, kept for backward compatibility.
- `lat` / `lon`: Your location coordinates.
- `units`: Unit system (`si` for metric).
- `lang`: Language for weather descriptions.
- `timezone`: Your timezone (e.g., `Europe/Madrid`).
- `update_freq`: How often to refresh weather data (in seconds).

## Installation

PiWeatherRock is packaged with `pyproject.toml` and installs the current
console commands `pwr-ui` and `pwr-config-upgrade`.

### Raspberry Pi / Linux

Use the installation script from the repository root:

```bash
git clone https://github.com/carloshm/PiWeatherRock.git
cd PiWeatherRock
./install.sh Europe/Madrid
```

The optional argument is the system timezone. The script installs the required
system packages, creates a virtual environment at `~/pwr-env`, installs
PiWeatherRock with `pip install .`, and prints the commands needed to run the
application.

Before starting the UI, create and edit your configuration file:

```bash
source ~/pwr-env/bin/activate
cp piweatherrock/config.json-sample piweatherrock/piweatherrock-config.json
# Edit piweatherrock/piweatherrock-config.json with your coordinates, timezone, language, and display options.
pwr-ui -c ./piweatherrock/piweatherrock-config.json
```

### Manual or development installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install .
cp piweatherrock/config.json-sample piweatherrock/piweatherrock-config.json
# Edit piweatherrock/piweatherrock-config.json before running.
pwr-ui -c ./piweatherrock/piweatherrock-config.json
```

See [`docs/`](docs/) for an application walkthrough with screenshots.

## Release process

- Update version in `pyproject.toml` according to the types of changes made
- Update `requirements.txt` if needed
- `python3 -m pip install --upgrade build twine`
- `python3 -m build`
- `tar tzf dist/piweatherrock-*.tar.gz`
- `twine check dist/*`
- [optional] `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
- `twine upload dist/*`
- Create a git tag and push it

## Local Development process

```bash
python3 -m venv env_name
source env_name/bin/activate
```

```bash
git clone https://github.com/carloshm/PiWeatherRock.git
cd PiWeatherRock
git pull  # for any additional external change after a while
```

Make changes

```bash
git add .
git commit -m "changes description"
git push origin main
```

## Run changes

After making code changes in a local checkout, reinstall the package in your
active virtual environment and run the UI with your configuration file:

```bash
python3 -m pip install .
pwr-ui -c ./piweatherrock/piweatherrock-config.json
```

> **Note:** `pwr-ui` and `pwr-config-upgrade` are installed as console entry points via `pyproject.toml`. See [PEP 621](https://peps.python.org/pep-0621/) and [setup.py deprecation](https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html) for background.

## Validate Service Data

You can test the Open-Meteo API directly with a request like this:

```
https://api.open-meteo.com/v1/forecast?latitude=40.299457&longitude=-3.743399&timezone=Europe/Madrid&models=best_match&forecast_days=4&current_weather=true&temperature_unit=celsius&windspeed_unit=kmh&precipitation_unit=mm&timeformat=iso8601&hourly=visibility,weathercode,temperature_2m,relativehumidity_2m,apparent_temperature,surface_pressure,cloudcover,windspeed_80m,precipitation,precipitation_probability,dewpoint_2m,windspeed_10m,windgusts_10m,winddirection_10m,cloudcover_low,direct_radiation&daily=sunrise,sunset,uv_index_max,weathercode,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,precipitation_probability_mean,precipitation_probability_min,windgusts_10m_max,precipitation_probability_max,windspeed_10m_max,winddirection_10m_dominant
```

For more details on available parameters, see the [Open-Meteo API documentation](https://open-meteo.com/en/docs).
