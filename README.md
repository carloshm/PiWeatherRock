# PiWeatherRock

![GitHub](https://img.shields.io/github/license/genebean/PiWeatherRock)
![PyPI](https://img.shields.io/pypi/v/piweatherrock)

PiWeatherRock displays local weather on (almost) any screen you connect to a Raspberry Pi. It also works on other platforms, including macOS.

More information about the project and full documentation can be found at https://piweatherrock.technicalissues.us. Be sure to check out the getting started guide under the documentation link there for instruction on how to set everything up.

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

- git clone https://github.com/carloshm/PiWeatherRock.git
- git pull (for any additional external change after a while)
- cd PiWeatherRock
- Make changes
- git add .
- git commit -m "changes description"
- git push origin main

## Run changes

- python3 setup.py install --user
- python3 ./scripts/pwr-ui -c /home/pi/Desktop/piweatherrock-config.json

## Validate Service Data

https://api.open-meteo.com:443 "GET /v1/forecast?latitude=40.299457&longitude=-3.743399&appid=openmeteo-request-piweatherrock&timezone=Europe/Madrid&models=best_match&forecast_days=4&current_weather=true&temperature_unit=celsius&windspeed_unit=kmh&precipitation_unit=mm&timeformat=iso8601&hourly=visibility,weathercode,temperature_2m,relativehumidity_2m,apparent_temperature,surface_pressure,cloudcover,windspeed_80m,precipitation,precipitation_probability,dewpoint_2m,windspeed_10m,windgusts_10m,winddirection_10m,cloudcover_low,direct_radiation&daily=sunrise,sunset,uv_index_max,weathercode,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,precipitation_probability_mean,precipitation_probability_min,windgusts_10m_max,precipitation_probability_max,windspeed_10m_max,winddirection_10m_dominant HTTP/1.1"
