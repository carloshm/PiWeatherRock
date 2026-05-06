# PiWeatherRock

![GitHub](https://img.shields.io/github/license/genebean/PiWeatherRock)
![PyPI](https://img.shields.io/pypi/v/piweatherrock)

PiWeatherRock displays local weather on (almost) any screen you connect to a Raspberry Pi. It also works on other platforms, including macOS.

More information about the project and full documentation can be found at https://piweatherrock.technicalissues.us. Be sure to check out the getting started guide under the documentation link there for instruction on how to set everything up.

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

## Release process

- edit `version.py` according to the types of changes made
- edit `requirements.txt` if needed
- `python3 setup.py sdist bdist_wheel`
- `tar tzf dist/piweatherrock-*.tar.gz`
- `twine check dist/*`
- [optional] `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
- `twine upload dist/*`
- Create a git tag and push it

## Local Development process

```python
python3 -m venv env_name
source env_name/bin/activate
```

```python
git clone https://github.com/carloshm/PiWeatherRock.git
cd PiWeatherRock  
git pull (for any additional external change after a while)
```

Make changes

```python
git add .
git commit -m "changes description"
git push origin main
```

## Run changes https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html

```python
python3 -m pip install --upgrade setuptools wheel
python3 -m pip install .
python3 ./scripts/pwr-ui -c ./piweatherrock/piweatherrock-config.json
```

## Validate Service Data

You can test the Open-Meteo API directly with a request like this:

```
https://api.open-meteo.com/v1/forecast?latitude=40.299457&longitude=-3.743399&timezone=Europe/Madrid&models=best_match&forecast_days=4&current_weather=true&temperature_unit=celsius&windspeed_unit=kmh&precipitation_unit=mm&timeformat=iso8601&hourly=visibility,weathercode,temperature_2m,relativehumidity_2m,apparent_temperature,surface_pressure,cloudcover,windspeed_80m,precipitation,precipitation_probability,dewpoint_2m,windspeed_10m,windgusts_10m,winddirection_10m,cloudcover_low,direct_radiation&daily=sunrise,sunset,uv_index_max,weathercode,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,precipitation_probability_mean,precipitation_probability_min,windgusts_10m_max,precipitation_probability_max,windspeed_10m_max,winddirection_10m_dominant
```

For more details on available parameters, see the [Open-Meteo API documentation](https://open-meteo.com/en/docs).
