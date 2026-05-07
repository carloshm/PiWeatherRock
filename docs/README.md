# Guía de la aplicación PiWeatherRock

Esta carpeta documenta el uso actual de PiWeatherRock y complementa las instrucciones de instalación del `README.md` principal.

## Qué muestra la aplicación

PiWeatherRock es una interfaz de pantalla completa para Raspberry Pi u otros equipos con pantalla conectada. Consulta Open-Meteo, traduce los datos al formato interno heredado de Dark Sky y alterna entre pantallas de previsión diaria, previsión horaria e información general.

## Instalación actual resumida

La instalación vigente usa el empaquetado definido en `pyproject.toml`:

1. Instalar dependencias del sistema y crear un entorno virtual. En Raspberry Pi/Linux se puede usar:

   ```bash
   ./install.sh Europe/Madrid
   ```

2. Activar el entorno virtual e instalar el paquete:

   ```bash
   source ~/pwr-env/bin/activate
   python3 -m pip install .
   ```

3. Crear la configuración desde la plantilla y editar ubicación, zona horaria, idioma y opciones de pantalla:

   ```bash
   cp piweatherrock/config.json-sample piweatherrock/piweatherrock-config.json
   ```

4. Ejecutar la aplicación con el entry point actual:

   ```bash
   pwr-ui -c ./piweatherrock/piweatherrock-config.json
   ```

También queda disponible `pwr-config-upgrade` para actualizar configuraciones antiguas.

## Pantalla de previsión diaria

La pantalla diaria combina la hora, la temperatura actual, el resumen meteorológico, viento, humedad y aviso de paraguas con la previsión de hoy y los tres próximos días.

![Captura de la previsión diaria](images/pantalla-diaria.svg)

## Pantalla de previsión horaria

La pantalla horaria mantiene el bloque superior de condiciones actuales y sustituye la franja inferior por la previsión de las próximas horas. Se puede alternar manualmente con la tecla `h`.

![Captura de la previsión horaria](images/pantalla-horaria.svg)

## Pantalla de información

La pantalla de información reduce el contenido visual para ayudar a evitar quemados de pantalla. Muestra hora, salida y puesta de sol, duración de la luz diurna y hora de la última actualización. Se puede abrir con la tecla `i`.

![Captura de la pantalla de información](images/pantalla-informacion.svg)

## Controles principales

- `d`: cambia a previsión diaria.
- `h`: cambia a previsión horaria.
- `i`: cambia a información general.
- `s`: guarda una captura como `screenshot.jpeg`.
- `q` o Intro del teclado numérico: cierra la aplicación.

## Configuración relevante

Los valores se editan en `piweatherrock/piweatherrock-config.json`:

- `lat` y `lon`: coordenadas de la ubicación.
- `timezone`: zona horaria, por ejemplo `Europe/Madrid`.
- `lang` y `ui_lang`: idioma de los datos meteorológicos y de la interfaz.
- `units`: sistema de unidades; `si` usa métricas.
- `fullscreen`: ejecuta en pantalla completa si es `true`.
- `update_freq`: frecuencia de actualización de Open-Meteo en segundos.
- `plugins.daily` y `plugins.hourly`: activación y tiempo de permanencia de las pantallas diaria y horaria.
