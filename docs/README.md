# Guía de la aplicación PiWeatherRock

Esta carpeta documenta el uso actual de PiWeatherRock y complementa las instrucciones de instalación del `README.md` principal.

## Qué muestra la aplicación

PiWeatherRock es una interfaz de pantalla completa para Raspberry Pi u otros equipos con pantalla conectada. Consulta Open-Meteo, traduce los datos al formato interno heredado de Dark Sky y alterna entre pantallas de previsión diaria, previsión horaria e información general.

## Instalación actual resumida

La instalación vigente usa el empaquetado definido en `pyproject.toml`.

En Raspberry Pi/Linux se puede usar el script del repositorio:

```bash
./install.sh Europe/Madrid
```

El script instala dependencias del sistema, crea el entorno virtual `~/pwr-env` e instala el paquete con `pip install .`.

Después, activa el entorno, crea la configuración desde la plantilla y ejecuta el entry point actual:

```bash
source ~/pwr-env/bin/activate
cp piweatherrock/config.json-sample piweatherrock/piweatherrock-config.json
# Edita piweatherrock/piweatherrock-config.json con ubicación, zona horaria, idioma y opciones de pantalla.
pwr-ui -c ./piweatherrock/piweatherrock-config.json
```

Para una instalación manual o de desarrollo:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install .
cp piweatherrock/config.json-sample piweatherrock/piweatherrock-config.json
pwr-ui -c ./piweatherrock/piweatherrock-config.json
```

También queda disponible `pwr-config-upgrade` para actualizar configuraciones antiguas.

## Aplicación web de configuración

PiWeatherRock incluye una aplicación web local para editar el mismo fichero JSON que usa la interfaz principal. Es útil para ajustar ubicación, idioma, zona horaria y rotación de pantallas sin modificar el archivo a mano.

![Vista representativa de la aplicación web de configuración](images/aplicacion-configuracion.svg)

### Arranque rápido

1. Instala el paquete y crea la configuración inicial desde la plantilla.
2. Ejecuta la aplicación de configuración indicando el fichero JSON:

   ```bash
   pwr-config-web -c ./piweatherrock/piweatherrock-config.json
   ```

3. Abre el navegador en `http://127.0.0.1:8888`.
4. Cambia los valores necesarios y pulsa **Guardar cambios**.
5. Si `pwr-ui` está en ejecución, aplicará automáticamente los cambios válidos al detectar la actualización del JSON.

### Qué se puede configurar

La pantalla web expone los campos principales definidos para `piweatherrock/piweatherrock-config.json`:

- **Ubicación:** `lat`, `lon` y `timezone`.
- **Open-Meteo:** `ds_api_key`, mantenido por compatibilidad como identificador heredado.
- **Unidades e idiomas:** `units`, `lang` y `ui_lang`.
- **Actualización meteorológica:** `update_freq`, en segundos.
- **Presentación:** `fullscreen`, `12hour_disp` e `icon_offset`.
- **Pantalla de información:** `info_pause` e `info_delay`.
- **Rotación diaria y horaria:** `plugins.daily.enabled`, `plugins.daily.pause`, `plugins.hourly.enabled` y `plugins.hourly.pause`.
- **Diagnóstico:** `log_level`.

### Validación y guardado

Al guardar, la aplicación carga el JSON actual, convierte los valores del formulario al tipo esperado, valida la configuración y escribe el fichero de forma atómica. Si ya existía un fichero de configuración, se conserva una copia con sufijo `.bak`.

El enlace **Validar configuración** abre `/status` y devuelve:

- `OK: configuración válida...` cuando el JSON cumple los requisitos.
- `ERROR: ...` con código HTTP 400 si falta un campo, hay un tipo incorrecto o algún valor está fuera de rango.

Si el JSON queda inválido mientras `pwr-ui` está funcionando, la interfaz principal mantiene la configuración activa anterior y registra el error en lugar de aplicar el cambio defectuoso.

### Seguridad de red

Por defecto, la aplicación escucha solo en `127.0.0.1:8888`, es decir, únicamente desde la propia máquina:

```bash
pwr-config-web -c ./piweatherrock/piweatherrock-config.json
```

Solo usa `--host` si necesitas acceder desde otro equipo de tu red y entiendes el riesgo de exponer la configuración:

```bash
pwr-config-web -c ./piweatherrock/piweatherrock-config.json --host 0.0.0.0 --port 8888
```

En ese caso, limita el acceso a una red de confianza y cierra la aplicación cuando termines de configurar.

### Flujo visual recomendado

```text
config.json-sample
        │
        ▼
piweatherrock-config.json ──► pwr-config-web ──► Guardar / validar
        │                              │
        └──────────── pwr-ui detecta cambios válidos ────────────┘
```

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
