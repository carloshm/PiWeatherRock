# Auditoría consolidada de PiWeatherRock

## Alcance

Revisión estática del proyecto PiWeatherRock con foco en:

- Bugs observables en ejecución, especialmente iconos meteorológicos no esperados.
- Riesgos de disponibilidad en Raspberry Pi.
- Evolución funcional para sustituir la pantalla de información rotativa por un modo “marco de fotos” con imágenes a pantalla completa.
- Evolución de configuración para seleccionar qué páginas se muestran y parametrizarlas desde una aplicación de configuración.

## Resumen ejecutivo

El proyecto conserva una arquitectura sencilla basada en `pygame`: `Runner` carga la configuración, crea el objeto `Weather`, instancia los plugins diario, horario e información, y rota entre pantallas mediante contadores de tiempo. La integración meteorológica actual adapta Open-Meteo al modelo histórico de Dark Sky.

Los principales riesgos detectados son:

1. **Iconos no robustos**: hay mapeos hacia ficheros inexistentes y errores tipográficos que pueden provocar fallos en `pygame.image.load()`.
2. **Primer arranque frágil si falla la API**: un error de red inicial puede dejar `self.weather` vacío y aun así continuar la ejecución.
3. **Configuración incoherente**: el ejemplo de configuración no incluye `timezone`, aunque el código lo exige.
4. **Plugins `enabled` ignorados**: la configuración permite habilitar/deshabilitar páginas, pero `Runner` rota siempre entre diario, horario e info.
5. **Disponibilidad en Raspberry Pi mejorable**: no hay timeout efectivo en peticiones HTTP, la inicialización de vídeo no aborta limpiamente si no hay driver, y los errores de renderizado pueden terminar el bucle principal.
6. **Pantalla info poco extensible**: `PluginInfo` está acoplado a una pantalla fija de texto; no existe un sistema genérico de páginas rotativas configurables.

## Bugs identificados

### 1. Iconos con rutas inexistentes

**Zona:** `piweatherrock/plugin_weather_common/__init__.py`, método `icon_mapping()`.

El método devuelve rutas que después se cargan directamente con:

- `pygame.image.load(self.icon_mapping(data.icon, self.icon_size)).convert_alpha()`

Problemas detectados:

- `chainsleet` parece un typo de `chancesleet`.
  - Open-Meteo mapea códigos 56 y 66 a `chainsleet`.
  - `icon_mapping()` busca `icons/{size}/chainsleet.png`.
  - En el repositorio existen `chancesleet.png`, no `chainsleet.png`.
- Algunos iconos se buscan en `icons/alt_icons/{size}/`, pero no existen allí:
  - `chancesnow`
  - `chanceflurries`
  - `flurries`
  - `chancetstorms`
- Si llega cualquier icono inesperado, el `else` sí cae a `icons/{size}/unknown.png`; el problema principal está en iconos “esperados” por el conversor pero mal enrutados.

**Impacto:** fallo de renderizado y posible cierre de la aplicación cuando `pygame` no encuentra el fichero.

**Recomendación:**

- Normalizar nombres de iconos en un diccionario único.
- Validar la existencia del fichero antes de devolverlo.
- Si no existe, registrar warning y usar `unknown.png`.
- Añadir prueba unitaria o script de validación que recorra todos los valores emitidos por `get_darksky_icon()` y confirme que `icon_mapping()` resuelve a un fichero real para tamaños `64` y `256`.

### 2. El fallo inicial de forecast puede dejar la aplicación en estado inválido

**Zona:** `piweatherrock/weather.py`, `Weather.__init__()` y `get_forecast()`.

`Weather.__init__()` llama a `self.get_forecast()` pero no comprueba su resultado. Además, `get_forecast()` asigna `last_update_check = time.time()` antes de completar correctamente la petición y parseo.

Escenario problemático:

1. Arranca la aplicación.
2. Falla la primera llamada a la API.
3. `self.weather` queda como `{}`.
4. `Runner.main()` vuelve a llamar a `get_forecast()`.
5. Como `last_update_check` ya se actualizó, puede devolver `True` sin reintentar.
6. Los plugins acceden a `self.weather.daily`, `self.weather.hourly`, etc., y pueden fallar.

**Impacto:** errores intermitentes en arranque, especialmente en Raspberry Pi si la red todavía no está lista.

**Recomendación:**

- Actualizar `last_update_check` solo tras una descarga y parseo correctos.
- Si no hay forecast válido inicial, mostrar una pantalla de error/reintento en vez de entrar en la rotación normal.
- Mantener último forecast válido en memoria y, opcionalmente, persistirlo en disco como caché.

### 3. `config.json-sample` no incluye `timezone`

**Zona:** `piweatherrock/config.json-sample` y `piweatherrock/weather.py`.

`Weather.get_forecast()` usa `self.config["timezone"]`, pero el fichero de ejemplo no define esa clave.

**Impacto:** un usuario que parta del ejemplo puede obtener `KeyError: 'timezone'`.

**Recomendación:**

- Añadir `timezone` al ejemplo.
- Validar configuración al inicio con mensajes claros.
- Definir valores por defecto o una migración de configuración.

### 4. La configuración `plugins.*.enabled` no se respeta

**Zona:** `piweatherrock/runner.py`, `config.json-sample`, `piweatherrock/piweatherrock-config.json`.

La configuración declara:

- `plugins.daily.enabled`
- `plugins.hourly.enabled`

Pero `Runner` instancia siempre `PluginWeatherDaily`, `PluginWeatherHourly` y `PluginInfo`, y la rotación alterna siempre entre diario, horario e info.

Además, `piweatherrock/piweatherrock-config.json` marca `daily.enabled=false` y `hourly.enabled=false`, pero la aplicación seguiría intentando mostrarlas.

**Impacto:** la configuración promete una funcionalidad que no existe; dificulta seleccionar páginas visibles.

**Recomendación:**

- Reemplazar la lógica fija `d/h/i` por una lista de páginas configuradas.
- Excluir páginas con `enabled=false`.
- Validar que exista al menos una página habilitada.
- Permitir orden, duración y parámetros por página.

### 5. Riesgo de `IndexError` si Open-Meteo devuelve menos horas de las esperadas

**Zona:** `piweatherrock/climate/openmeteo.py`, `plugin_weather_hourly/__init__.py`.

`openmeteo_to_darksky()` filtra las próximas 4 horas. Luego `PluginWeatherHourly.disp_hourly()` asume que hay al menos 4 elementos (`hourly[0]` y tres futuros).

**Impacto:** si por zona horaria, límite de datos, cambio de día o respuesta incompleta se obtienen menos de 4 registros, la pantalla horaria puede fallar.

**Recomendación:**

- Garantizar relleno mínimo en el adaptador o limitar el renderizado a `min(len(hourly), 4)`.
- Mostrar placeholders si faltan datos.

### 6. Unidades declaradas no siempre coinciden con los datos solicitados

**Zona:** `piweatherrock/climate/forecast.py` y `plugin_weather_common/__init__.py`.

La URL de Open-Meteo solicita siempre:

- `temperature_unit=celsius`
- `windspeed_unit=kmh`

Pero la UI usa `config["units"]` para etiquetar grados y viento como si fueran `us`, `si`, `ca` o `uk2`.

**Impacto:** riesgo de mostrar valores en una unidad y etiquetas en otra.

**Recomendación:**

- Traducir `config["units"]` a parámetros Open-Meteo reales.
- O restringir la configuración a unidades soportadas por la consulta actual.

### 7. Uso de `eval()` en configuración y modelo de datos

**Zonas:**

- `piweatherrock/weather.py`, `get_logger()`.
- `piweatherrock/climate/data.py`, `DataPoint.__setattr__()`.

`get_logger()` usa `eval(f"logging.{self.config['log_level']}")`. Aunque el valor venga de configuración local, no es necesario y puede sustituirse por `getattr(logging, level, logging.INFO)`.

`DataPoint.__setattr__()` usa `eval(name.capitalize())` para `alerts` y `flags`; puede reemplazarse por un diccionario explícito.

**Impacto:** superficie de riesgo innecesaria y errores más difíciles de diagnosticar.

**Recomendación:** eliminar `eval()` en ambos puntos.

## Mejoras de disponibilidad en Raspberry Pi

### Inicialización de vídeo

**Zona:** `piweatherrock/weather.py`.

El código intenta inicializar drivers SDL (`x11`, `fbcon`, `directfb`, `svgalib`), pero si no encuentra ninguno solo registra una excepción y continúa. Después usa `pygame.display.Info()` y `set_mode()`, lo que puede fallar de forma menos controlada.

**Recomendaciones:**

- Si no hay driver, abortar con mensaje claro y código de salida controlado.
- Permitir configurar `SDL_VIDEODRIVER` desde configuración o entorno documentado.
- Añadir modo `windowed`/diagnóstico para pruebas por SSH o X11.
- Registrar driver elegido y resolución final.

### Red y API

**Zona:** `piweatherrock/climate/forecast.py`, `piweatherrock/weather.py`.

Actualmente se prepara un `request_params` con timeout, pero no se usa en `requests.get(self.url)`. Por tanto, la petición puede bloquear más de lo deseado.

**Recomendaciones:**

- Usar `requests.get(self.url, timeout=...)`.
- Configurar timeout por defecto razonable.
- Añadir reintentos con backoff.
- No invalidar el último forecast correcto si falla una actualización.
- Mostrar pantalla “datos no disponibles” manteniendo la aplicación viva.

### Robustez del bucle principal

**Zona:** `piweatherrock/runner.py`.

El bucle principal no protege cada renderizado. Un error en una pantalla concreta puede terminar toda la aplicación.

**Recomendaciones:**

- Capturar excepciones por página.
- Registrar el error, deshabilitar temporalmente la página problemática y continuar con la siguiente.
- Añadir watchdog externo con `systemd` (`Restart=always`) y logs persistentes.

### Validación de configuración

**Recomendaciones:**

- Validar al inicio:
  - claves obligatorias (`lat`, `lon`, `timezone`, `units`, `ui_lang`, `plugins`);
  - tipos;
  - rangos (`pause > 0`, `update_freq > 0`);
  - al menos una página habilitada;
  - rutas de imágenes existentes.
- Mostrar errores de configuración en pantalla cuando sea posible.

### Caché local

**Recomendación:**

- Guardar el último forecast válido en un JSON local.
- En arranque sin red, cargar caché si no está demasiado caducada.
- Mostrar una marca visual de “datos desactualizados”.

## Sustitución de la pantalla de información por marco de fotos

### Situación actual

`PluginInfo` renderiza una pantalla fija con hora, amanecer, atardecer, horas de luz y última actualización. `Runner` entra en esta pantalla cuando:

- se pulsa `i`;
- se supera `info_delay` mientras se muestran pantallas meteorológicas;
- vuelve al tiempo tras `info_pause`.

### Objetivo funcional

Sustituir o complementar esa pantalla por una página tipo **marco de fotos** que muestre imágenes a pantalla completa mientras no se muestra el tiempo.

### Propuesta de diseño

Crear un nuevo plugin/página, por ejemplo `photo_frame`, con configuración propia:

- `enabled`: activar/desactivar.
- `pause`: duración de cada imagen.
- `path`: directorio de imágenes.
- `shuffle`: orden aleatorio o secuencial.
- `fit`: estrategia de escalado (`contain`, `cover`, `stretch`).
- `background`: color para bandas si se usa `contain`.
- `show_clock`: opcional para superponer hora.
- `extensions`: lista permitida (`jpg`, `jpeg`, `png`, `webp` si pygame lo soporta).

Comportamiento recomendado:

- Escanear el directorio al arrancar y periódicamente.
- Ignorar ficheros corruptos registrando warning.
- Escalar la imagen a resolución completa sin deformar por defecto.
- Precargar la siguiente imagen para evitar parpadeos.
- Si no hay imágenes válidas, mostrar una pantalla de fallback.

### Relación con la pantalla `info`

Opciones:

1. Mantener `info` como página independiente y añadir `photo_frame`.
2. Reemplazar `info` por `photo_frame`.
3. Permitir ambas y que el usuario configure cuáles rotan.

La opción 3 es la más flexible y encaja con la necesidad de seleccionar páginas desde una aplicación de configuración.

## Selección de páginas y configuración desde aplicación de configuración

### Problema actual

La rotación está codificada en `Runner` con estados fijos:

- `d`: diario.
- `h`: horario.
- `i`: info.

Esto impide añadir nuevas páginas o respetar completamente `enabled`.

### Modelo de configuración propuesto

Evolucionar a una configuración basada en lista ordenada de páginas:

```json
{
  "pages": [
    {
      "id": "daily",
      "enabled": true,
      "pause": 60
    },
    {
      "id": "hourly",
      "enabled": true,
      "pause": 60
    },
    {
      "id": "photo_frame",
      "enabled": true,
      "pause": 20,
      "path": "/home/pi/Pictures",
      "shuffle": true,
      "fit": "cover"
    },
    {
      "id": "info",
      "enabled": false,
      "pause": 60
    }
  ]
}
```

Por compatibilidad, se puede migrar desde `plugins.daily/hourly` a `pages`.

### Cambios recomendados en arquitectura

- Crear una interfaz común de página/plugin:
  - `id`
  - `render(weather_rock)`
  - `on_enter()` opcional
  - `on_exit()` opcional
  - `requires_weather`
- Convertir `daily`, `hourly`, `info` y `photo_frame` a páginas registrables.
- Sustituir `d_count`, `h_count`, `current_screen` e `info_delay` por un planificador genérico.
- Añadir teclas para avanzar/retroceder página y no depender solo de `d`, `h`, `i`.

### Aplicación de configuración

El repositorio ya depende de `piweatherrock-webconfig==1.5.0`, por lo que conviene integrar la configuración de páginas en esa aplicación o evolucionarla.

Campos mínimos que debería exponer:

- Activar/desactivar páginas.
- Orden de páginas.
- Duración por página.
- Parámetros específicos de cada página.
- Validación de directorio de imágenes.
- Test de resolución y modo fullscreen.
- Validación de zona horaria, latitud, longitud e idioma.
- Botón para probar carga de iconos y forecast.

## Priorización recomendada

### Prioridad alta

1. Corregir mapeos de iconos y fallback a `unknown.png`.
2. Arreglar reintento inicial de forecast y no actualizar `last_update_check` en fallo.
3. Añadir `timezone` a `config.json-sample`.
4. Usar timeout real en `requests.get()`.
5. Respetar `enabled` o eliminarlo hasta implementarlo correctamente.

### Prioridad media

1. Validación formal de configuración.
2. Caché local del último forecast válido.
3. Manejo de excepciones por página.
4. Alinear unidades Open-Meteo con `config["units"]`.
5. Eliminar `eval()`.

### Prioridad baja / evolutiva

1. Nuevo sistema genérico de páginas.
2. Plugin `photo_frame`.
3. Configuración visual de páginas en `piweatherrock-webconfig`.
4. Previsualización de páginas desde la aplicación de configuración.

## Plan incremental sugerido

1. **Estabilización**
   - Corregir iconos.
   - Añadir fallback seguro.
   - Añadir timeout y reintento básico.
   - Validar configuración mínima.

2. **Configurabilidad real**
   - Respetar `enabled`.
   - Migrar rotación fija a lista de páginas.
   - Mantener compatibilidad con configuración existente.

3. **Marco de fotos**
   - Crear página `photo_frame`.
   - Añadir carga segura de imágenes.
   - Añadir opciones de escalado y orden.

4. **Aplicación de configuración**
   - Exponer selección y orden de páginas.
   - Exponer parámetros de `photo_frame`.
   - Añadir validación y pruebas desde UI.

5. **Disponibilidad Raspberry Pi**
   - Documentar servicio `systemd`.
   - Añadir caché de forecast.
   - Añadir modo diagnóstico de vídeo/red.

## Validaciones recomendadas

- Test automático de que todos los iconos emitidos por `get_darksky_icon()` existen para `64` y `256`.
- Test de arranque con forecast fallido.
- Test de configuración sin `timezone`.
- Test con `daily.enabled=false` y/o `hourly.enabled=false`.
- Test con menos de 4 horas disponibles.
- Test manual en Raspberry Pi:
  - arranque sin red;
  - arranque con red lenta;
  - pantalla HDMI conectada tarde;
  - ejecución como servicio `systemd`;
  - directorio de fotos vacío, inexistente y con imágenes corruptas.

