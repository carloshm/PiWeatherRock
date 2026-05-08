#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local web configuration UI for PiWeatherRock."""

import html
import os
from argparse import ArgumentParser
from urllib.parse import urlencode

import cherrypy

from piweatherrock.config_manager import (
    CONFIG_FORM_FIELDS,
    ConfigError,
    MEDIA_FIT_MODES,
    field_name,
    get_config_value,
    load_config,
    SUPPORTED_LANGUAGES,
    SUPPORTED_TIMEZONES,
    set_config_value,
    validate_config,
    write_config_atomic,
)


TEXT = {
    'en': {
        'changes_applied': 'Changes applied',
        'config_error': 'Configuration error',
        'error': 'Error',
        'legend': 'PiWeatherRock configuration',
        'open_map': 'Open larger map',
        'map_hint': 'Use the map as a visual reference for latitude and longitude.',
        'map_title': 'Location map preview',
        'save': 'Save changes',
        'status_ok': 'OK: valid configuration. The UI will apply changes automatically.',
        'subtitle': 'Adjust weather, display, rotation, and local media options from one guided form.',
        'title': 'PiWeatherRock Config',
        'validate': 'Validate configuration',
        'labels': {
            'lat': 'Latitude',
            'lon': 'Longitude',
            'timezone': 'Timezone',
            'ds_api_key': 'Open-Meteo identifier',
            'units': 'Units',
            'lang': 'Weather language',
            'ui_lang': 'UI language',
            'update_freq': 'Forecast refresh interval (seconds)',
            'fullscreen': 'Fullscreen',
            '12hour_disp': '12-hour format',
            'icon_offset': 'Icon offset',
            'info_pause': 'Pause between full page cycles (seconds)',
            'info_delay': 'Delay before showing info page (seconds)',
            'daily_enabled': 'Daily page enabled',
            'daily_pause': 'Daily page display pause (seconds)',
            'hourly_enabled': 'Hourly page enabled',
            'hourly_pause': 'Hourly page display pause (seconds)',
            'info_enabled': 'Info page enabled',
            'info_pause_plugin': 'Info page display pause (seconds)',
            'media_enabled': 'Local media page enabled',
            'media_pause': 'Pause between local media items (seconds)',
            'media_path': 'Local media folder',
            'media_shuffle': 'Shuffle local media',
            'media_fit': 'Media fit',
            'media_extensions': 'Media extensions',
            'log_level': 'Log level'},
        'sections': {
            'location': 'Location and timezone',
            'weather': 'Weather and language',
            'display': 'Display',
            'rotation': 'Page rotation pauses',
            'media': 'Local media',
            'diagnostics': 'Diagnostics'},
        'help': {
            'location': 'Coordinates and timezone used for forecast, sunrise, and sunset calculations.',
            'weather': 'Open-Meteo request identifier, units, and languages shown in the weather and UI texts.',
            'display': 'Screen presentation options for the Raspberry Pi display.',
            'rotation': 'The global pause controls complete page cycles; each page pause controls how long that section stays visible.',
            'media': 'Local folder, ordering, fit mode, and pause between individual media files.',
            'diagnostics': 'Logging verbosity for troubleshooting.'}},
    'es': {
        'changes_applied': 'Cambios aplicados',
        'config_error': 'Error de configuración',
        'error': 'Error',
        'legend': 'Configuración PiWeatherRock',
        'open_map': 'Abrir mapa grande',
        'map_hint': 'Usa el mapa como referencia visual para latitud y longitud.',
        'map_title': 'Vista previa del mapa de ubicación',
        'save': 'Guardar cambios',
        'status_ok': 'OK: configuración válida. La UI aplicará los cambios automáticamente.',
        'subtitle': 'Ajusta meteorología, pantalla, rotación y medios locales desde un formulario guiado.',
        'title': 'Configuración de PiWeatherRock',
        'validate': 'Validar configuración',
        'labels': {
            'lat': 'Latitud',
            'lon': 'Longitud',
            'timezone': 'Zona horaria',
            'ds_api_key': 'Identificador Open-Meteo',
            'units': 'Unidades',
            'lang': 'Idioma meteorológico',
            'ui_lang': 'Idioma de interfaz',
            'update_freq': 'Intervalo de actualización del pronóstico (segundos)',
            'fullscreen': 'Pantalla completa',
            '12hour_disp': 'Formato de 12 horas',
            'icon_offset': 'Desplazamiento de iconos',
            'info_pause': 'Pausa entre ciclos completos de páginas (segundos)',
            'info_delay': 'Retraso antes de mostrar información (segundos)',
            'daily_enabled': 'Página diaria activada',
            'daily_pause': 'Pausa de visualización de página diaria (segundos)',
            'hourly_enabled': 'Página horaria activada',
            'hourly_pause': 'Pausa de visualización de página horaria (segundos)',
            'info_enabled': 'Página de información activada',
            'info_pause_plugin': 'Pausa de visualización de página de información (segundos)',
            'media_enabled': 'Página de medios locales activada',
            'media_pause': 'Pausa entre archivos de medios locales (segundos)',
            'media_path': 'Carpeta local de medios',
            'media_shuffle': 'Medios locales en orden aleatorio',
            'media_fit': 'Ajuste de medios',
            'media_extensions': 'Extensiones de medios',
            'log_level': 'Nivel de log'},
        'sections': {
            'location': 'Ubicación y zona horaria',
            'weather': 'Meteorología e idioma',
            'display': 'Pantalla',
            'rotation': 'Pausas de rotación de páginas',
            'media': 'Medios locales',
            'diagnostics': 'Diagnóstico'},
        'help': {
            'location': 'Coordenadas y zona horaria usadas para el pronóstico, amanecer y atardecer.',
            'weather': 'Identificador Open-Meteo, unidades e idiomas mostrados en la meteorología y la interfaz.',
            'display': 'Opciones de presentación para la pantalla de la Raspberry Pi.',
            'rotation': 'La pausa global controla ciclos completos de páginas; cada pausa de sección define cuánto tiempo queda visible.',
            'media': 'Carpeta local, orden, modo de ajuste y pausa entre archivos de medios individuales.',
            'diagnostics': 'Nivel de detalle de los registros para solucionar problemas.'}},
    'ca': {
        'changes_applied': 'Canvis aplicats',
        'config_error': 'Error de configuració',
        'error': 'Error',
        'legend': 'Configuració de PiWeatherRock',
        'open_map': 'Obre el mapa gran',
        'map_hint': 'Fes servir el mapa com a referència visual per a latitud i longitud.',
        'map_title': 'Vista prèvia del mapa d’ubicació',
        'save': 'Desa els canvis',
        'status_ok': 'OK: configuració vàlida. La UI aplicarà els canvis automàticament.',
        'subtitle': 'Ajusta meteorologia, pantalla, rotació i mitjans locals des d’un formulari guiat.',
        'title': 'Configuració de PiWeatherRock',
        'validate': 'Valida la configuració',
        'labels': {
            'lat': 'Latitud',
            'lon': 'Longitud',
            'timezone': 'Zona horària',
            'ds_api_key': 'Identificador Open-Meteo',
            'units': 'Unitats',
            'lang': 'Idioma meteorològic',
            'ui_lang': 'Idioma de la interfície',
            'update_freq': 'Interval d’actualització de la previsió (segons)',
            'fullscreen': 'Pantalla completa',
            '12hour_disp': 'Format de 12 hores',
            'icon_offset': 'Desplaçament de les icones',
            'info_pause': 'Pausa entre cicles complets de pàgines (segons)',
            'info_delay': 'Retard abans de mostrar informació (segons)',
            'daily_enabled': 'Pàgina diària activada',
            'daily_pause': 'Pausa de visualització de pàgina diària (segons)',
            'hourly_enabled': 'Pàgina horària activada',
            'hourly_pause': 'Pausa de visualització de pàgina horària (segons)',
            'info_enabled': 'Pàgina d’informació activada',
            'info_pause_plugin': 'Pausa de visualització de pàgina d’informació (segons)',
            'media_enabled': 'Pàgina de mitjans locals activada',
            'media_pause': 'Pausa entre fitxers de mitjans locals (segons)',
            'media_path': 'Carpeta local de mitjans',
            'media_shuffle': 'Mitjans locals en ordre aleatori',
            'media_fit': 'Ajust de mitjans',
            'media_extensions': 'Extensions de mitjans',
            'log_level': 'Nivell de log'},
        'sections': {
            'location': 'Ubicació i zona horària',
            'weather': 'Meteorologia i idioma',
            'display': 'Pantalla',
            'rotation': 'Pauses de rotació de pàgines',
            'media': 'Mitjans locals',
            'diagnostics': 'Diagnòstic'},
        'help': {
            'location': 'Coordenades i zona horària usades per a la previsió, sortida i posta de sol.',
            'weather': 'Identificador Open-Meteo, unitats i idiomes mostrats a la meteorologia i la interfície.',
            'display': 'Opcions de presentació per a la pantalla de la Raspberry Pi.',
            'rotation': 'La pausa global controla cicles complets de pàgines; cada pausa de secció defineix quant temps queda visible.',
            'media': 'Carpeta local, ordre, mode d’ajust i pausa entre fitxers de mitjans individuals.',
            'diagnostics': 'Nivell de detall dels registres per resoldre problemes.'}},
    'gl': {
        'changes_applied': 'Cambios aplicados',
        'config_error': 'Erro de configuración',
        'error': 'Erro',
        'legend': 'Configuración de PiWeatherRock',
        'open_map': 'Abrir mapa grande',
        'map_hint': 'Usa o mapa como referencia visual para latitude e lonxitude.',
        'map_title': 'Vista previa do mapa de localización',
        'save': 'Gardar cambios',
        'status_ok': 'OK: configuración válida. A UI aplicará os cambios automaticamente.',
        'subtitle': 'Axusta meteoroloxía, pantalla, rotación e medios locais desde un formulario guiado.',
        'title': 'Configuración de PiWeatherRock',
        'validate': 'Validar configuración',
        'labels': {
            'lat': 'Latitude',
            'lon': 'Lonxitude',
            'timezone': 'Zona horaria',
            'ds_api_key': 'Identificador Open-Meteo',
            'units': 'Unidades',
            'lang': 'Idioma meteorolóxico',
            'ui_lang': 'Idioma da interface',
            'update_freq': 'Intervalo de actualización da predición (segundos)',
            'fullscreen': 'Pantalla completa',
            '12hour_disp': 'Formato de 12 horas',
            'icon_offset': 'Desprazamento das iconas',
            'info_pause': 'Pausa entre ciclos completos de páxinas (segundos)',
            'info_delay': 'Retardo antes de mostrar información (segundos)',
            'daily_enabled': 'Páxina diaria activada',
            'daily_pause': 'Pausa de visualización da páxina diaria (segundos)',
            'hourly_enabled': 'Páxina horaria activada',
            'hourly_pause': 'Pausa de visualización da páxina horaria (segundos)',
            'info_enabled': 'Páxina de información activada',
            'info_pause_plugin': 'Pausa de visualización da páxina de información (segundos)',
            'media_enabled': 'Páxina de medios locais activada',
            'media_pause': 'Pausa entre ficheiros de medios locais (segundos)',
            'media_path': 'Cartafol local de medios',
            'media_shuffle': 'Medios locais en orde aleatoria',
            'media_fit': 'Axuste de medios',
            'media_extensions': 'Extensións de medios',
            'log_level': 'Nivel de log'},
        'sections': {
            'location': 'Localización e zona horaria',
            'weather': 'Meteoroloxía e idioma',
            'display': 'Pantalla',
            'rotation': 'Pausas de rotación de páxinas',
            'media': 'Medios locais',
            'diagnostics': 'Diagnóstico'},
        'help': {
            'location': 'Coordenadas e zona horaria usadas para a predición, amencer e solpor.',
            'weather': 'Identificador Open-Meteo, unidades e idiomas mostrados na meteoroloxía e na interface.',
            'display': 'Opcións de presentación para a pantalla da Raspberry Pi.',
            'rotation': 'A pausa global controla ciclos completos de páxinas; cada pausa de sección define canto tempo queda visible.',
            'media': 'Cartafol local, orde, modo de axuste e pausa entre ficheiros de medios individuais.',
            'diagnostics': 'Nivel de detalle dos rexistros para resolver problemas.'}},
    'eu': {
        'changes_applied': 'Aldaketak aplikatu dira',
        'config_error': 'Konfigurazio-errorea',
        'error': 'Errorea',
        'legend': 'PiWeatherRock konfigurazioa',
        'open_map': 'Ireki mapa handia',
        'map_hint': 'Erabili mapa latitudearen eta longitudearen erreferentzia bisual gisa.',
        'map_title': 'Kokapen maparen aurrebista',
        'save': 'Gorde aldaketak',
        'status_ok': 'OK: konfigurazioa baliozkoa da. UIak aldaketak automatikoki aplikatuko ditu.',
        'subtitle': 'Eguraldia, pantaila, biraketa eta tokiko multimedia formulario gidatu batetik doitu.',
        'title': 'PiWeatherRock konfigurazioa',
        'validate': 'Balidatu konfigurazioa',
        'labels': {
            'lat': 'Latitudea',
            'lon': 'Longitudea',
            'timezone': 'Ordu-zona',
            'ds_api_key': 'Open-Meteo identifikatzailea',
            'units': 'Unitateak',
            'lang': 'Eguraldiaren hizkuntza',
            'ui_lang': 'Interfazearen hizkuntza',
            'update_freq': 'Iragarpenaren eguneratze-tartea (segundoak)',
            'fullscreen': 'Pantaila osoa',
            '12hour_disp': '12 orduko formatua',
            'icon_offset': 'Ikonoen desplazamendua',
            'info_pause': 'Orrialde-ziklo osoen arteko pausa (segundoak)',
            'info_delay': 'Informazioa erakutsi aurreko atzerapena (segundoak)',
            'daily_enabled': 'Eguneko orria gaituta',
            'daily_pause': 'Eguneko orriaren bistaratze-pausa (segundoak)',
            'hourly_enabled': 'Orduko orria gaituta',
            'hourly_pause': 'Orduko orriaren bistaratze-pausa (segundoak)',
            'info_enabled': 'Informazio-orria gaituta',
            'info_pause_plugin': 'Informazio-orriaren bistaratze-pausa (segundoak)',
            'media_enabled': 'Tokiko multimedia-orria gaituta',
            'media_pause': 'Tokiko multimedia-fitxategien arteko pausa (segundoak)',
            'media_path': 'Tokiko multimedia-karpeta',
            'media_shuffle': 'Tokiko multimedia ausazko ordenan',
            'media_fit': 'Multimedia doitzea',
            'media_extensions': 'Multimedia-luzapenak',
            'log_level': 'Log-maila'},
        'sections': {
            'location': 'Kokapena eta ordu-zona',
            'weather': 'Eguraldia eta hizkuntza',
            'display': 'Pantaila',
            'rotation': 'Orrialde-biraketaren pausak',
            'media': 'Tokiko multimedia',
            'diagnostics': 'Diagnostikoa'},
        'help': {
            'location': 'Iragarpenerako, egunsentirako eta ilunabarrerako erabiltzen diren koordenatuak eta ordu-zona.',
            'weather': 'Open-Meteo identifikatzailea, unitateak eta eguraldian nahiz interfazean erakusten diren hizkuntzak.',
            'display': 'Raspberry Pi pantailarako aurkezpen-aukerak.',
            'rotation': 'Pausa globalak orrialde-ziklo osoak kontrolatzen ditu; sekzio bakoitzeko pausak zenbat denbora ikusiko den zehazten du.',
            'media': 'Tokiko karpeta, ordena, doitze-modua eta banakako multimedia-fitxategien arteko pausa.',
            'diagnostics': 'Arazoak konpontzeko erregistroen xehetasun-maila.'}}
}


FORM_SECTIONS = [
    ('location', (('lat',), ('lon',), ('timezone',))),
    ('weather', (('ds_api_key',), ('units',), ('lang',), ('ui_lang',), ('update_freq',))),
    ('display', (('fullscreen',), ('12hour_disp',), ('icon_offset',))),
    ('rotation', (
        ('info_pause',), ('info_delay',),
        ('plugins', 'daily', 'enabled'), ('plugins', 'daily', 'pause'),
        ('plugins', 'hourly', 'enabled'), ('plugins', 'hourly', 'pause'),
        ('plugins', 'info', 'enabled'), ('plugins', 'info', 'pause'))),
    ('media', (
        ('plugins', 'media', 'enabled'), ('plugins', 'media', 'pause'),
        ('plugins', 'media', 'path'), ('plugins', 'media', 'shuffle'),
        ('plugins', 'media', 'fit'), ('plugins', 'media', 'extensions'))),
    ('diagnostics', (('log_level',),)),
]

SELECT_OPTIONS = {
    ('timezone',): [(timezone, timezone) for timezone in SUPPORTED_TIMEZONES],
    ('units',): [('si', 'Metric (SI)'), ('us', 'US'), ('ca', 'Canada'),
                 ('uk2', 'UK'), ('auto', 'Auto')],
    ('lang',): [(language, language.upper()) for language in SUPPORTED_LANGUAGES],
    ('ui_lang',): [(language, language.upper()) for language in SUPPORTED_LANGUAGES],
    ('plugins', 'media', 'fit'): [(mode, mode.title()) for mode in MEDIA_FIT_MODES],
    ('log_level',): [(level, level) for level in
                     ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')],
}



class ConfigWebApp:
    def __init__(self, config_file):
        self.config_file = config_file

    @cherrypy.expose
    def index(self, message=""):
        try:
            config = load_config(self.config_file)
            body = self._render_form(config, message)
        except ConfigError as exc:
            body = self._page(TEXT["en"]["config_error"],
                              "<p>{}</p>".format(html.escape(str(exc))))
        return body

    @cherrypy.expose
    def save(self, **params):
        try:
            config = load_config(self.config_file)
            for path, label_key, field_type in CONFIG_FORM_FIELDS:
                name = field_name(path)
                value = self._coerce_value(params.get(name), field_type)
                set_config_value(config, path, value)
            validate_config(config)
            write_config_atomic(self.config_file, config)
            raise cherrypy.HTTPRedirect("/?" + urlencode({
                "message": self._text(config, "changes_applied")}))
        except (ConfigError, ValueError) as exc:
            try:
                config = load_config(self.config_file)
                return self._render_form(config, "Error: {}".format(exc))
            except ConfigError:
                return self._page(TEXT["en"]["error"], "<p>{}</p>".format(
                    html.escape(str(exc))))

    @cherrypy.expose
    def status(self):
        try:
            config = load_config(self.config_file)
            return self._text(config, "status_ok")
        except ConfigError as exc:
            cherrypy.response.status = 400
            return "ERROR: {}".format(exc)

    def _render_form(self, config, message=""):
        rows = []
        if message:
            rows.append('<p class="message">{}</p>'.format(html.escape(message)))
        rows.append('<form method="post" action="/save">')
        rows.append('<div class="sections">')
        for section_key, paths in FORM_SECTIONS:
            rows.append('<section class="card" aria-labelledby="{0}-title">'.format(
                html.escape(section_key)))
            rows.append('<div class="section-heading">')
            rows.append('<h2 id="{id}-title">{title}</h2>'.format(
                id=html.escape(section_key),
                title=html.escape(self._section_title(config, section_key))))
            rows.append('<span class="help-icon" tabindex="0" role="button" '
                        'aria-label="{help}" title="{help}">?</span>'.format(
                            help=html.escape(
                                self._section_help(config, section_key),
                                quote=True)))
            rows.append('</div>')
            rows.append('<p class="section-help">{}</p>'.format(html.escape(
                self._section_help(config, section_key))))
            rows.append('<div class="field-grid">')
            for path in paths:
                rows.append(self._render_field(config, path))
            rows.append('</div>')
            if section_key == 'location':
                rows.append(self._render_location_map(config))
            rows.append('</section>')
        rows.append('</div>')
        rows.append('<div class="actions"><button type="submit">{}</button>'.format(
            html.escape(self._text(config, "save"))))
        rows.append('<a class="status-link" href="/status">{}</a></div>'.format(
            html.escape(self._text(config, "validate"))))
        rows.append('</form>')
        return self._page(self._text(config, "title"), "\n".join(rows),
                          self._language(config))

    def _render_field(self, config, path):
        label_key, field_type = self._field_definition(path)
        value = get_config_value(config, path)
        name = field_name(path)
        escaped_name = html.escape(name)
        label = html.escape(self._label(config, label_key))
        control = ''
        if field_type == "bool":
            checked = " checked" if value else ""
            control = ('<label class="toggle"><input type="checkbox" '
                       'id="{name}" name="{name}" value="true"{checked}>'
                       '<span>{label}</span></label>').format(
                           name=escaped_name, checked=checked, label=label)
            return '<div class="field field-checkbox">{}</div>'.format(control)
        if path in SELECT_OPTIONS:
            control = self._render_select(path, value)
        else:
            input_type = "number" if field_type in ("int", "float") else "text"
            step = ' step="any"' if field_type == "float" else ""
            control = ('<input type="{type}" id="{name}" name="{name}" '
                       'value="{value}"{step}>').format(
                           type=input_type,
                           name=escaped_name,
                           value=html.escape(str(value), quote=True),
                           step=step)
        return ('<div class="field"><label for="{name}">{label}</label>'
                '{control}</div>').format(
                    name=escaped_name, label=label, control=control)

    def _render_select(self, path, value):
        name = field_name(path)
        options = list(SELECT_OPTIONS[path])
        option_values = [option_value for option_value, _ in options]
        if value not in option_values:
            options.insert(0, (value, "{} (current value)".format(value)))
        option_html = []
        for option_value, option_label in options:
            selected = " selected" if option_value == value else ""
            option_html.append(
                '<option value="{value}"{selected}>{label}</option>'.format(
                    value=html.escape(str(option_value), quote=True),
                    selected=selected,
                    label=html.escape(str(option_label))))
        return '<select id="{0}" name="{0}">{1}</select>'.format(
            html.escape(name), "".join(option_html))

    def _render_location_map(self, config):
        lat = float(get_config_value(config, ("lat",)))
        lon = float(get_config_value(config, ("lon",)))
        map_url = self._map_url(lat, lon)
        open_url = 'https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=12/{lat}/{lon}'.format(
            lat=lat, lon=lon)
        return """<div class="map-panel">
  <div class="map-copy">
    <strong>{title}</strong>
    <span>{hint}</span>
    <a id="open-map-link" href="{open_url}" target="_blank" rel="noopener">{open_map}</a>
  </div>
  <iframe id="location-map" title="{title}" src="{map_url}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
</div>""".format(
            title=html.escape(self._text(config, "map_title"), quote=True),
            hint=html.escape(self._text(config, "map_hint")),
            open_map=html.escape(self._text(config, "open_map")),
            open_url=html.escape(open_url, quote=True),
            map_url=html.escape(map_url, quote=True))

    def _page(self, title, body, language="en"):
        return """<!doctype html>
<html lang="{language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f3f6fb;
      --card: #ffffff;
      --text: #162033;
      --muted: #5d6b82;
      --brand: #2563eb;
      --brand-dark: #1d4ed8;
      --border: #dbe3ef;
      --shadow: 0 18px 45px rgba(22, 32, 51, .10);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      background: linear-gradient(135deg, #eaf2ff 0%, var(--bg) 42%, #f8fbff 100%);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      min-height: 100vh;
    }}
    main {{ margin: 0 auto; max-width: 74rem; padding: 2rem; }}
    .hero {{
      background: linear-gradient(135deg, #1e3a8a, #2563eb);
      border-radius: 1.4rem;
      box-shadow: var(--shadow);
      color: white;
      margin-bottom: 1.5rem;
      padding: 2rem;
    }}
    h1 {{ font-size: clamp(2rem, 4vw, 3.2rem); line-height: 1; margin: 0 0 .65rem; }}
    .subtitle {{ color: rgba(255,255,255,.84); font-size: 1.05rem; margin: 0; max-width: 48rem; }}
    .sections {{ display: grid; gap: 1.1rem; }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 1rem;
      box-shadow: 0 10px 30px rgba(22, 32, 51, .06);
      padding: 1.25rem;
    }}
    .section-heading {{ align-items: center; display: flex; gap: .65rem; justify-content: space-between; }}
    h2 {{ font-size: 1.15rem; margin: 0; }}
    .help-icon {{
      align-items: center;
      background: #eef4ff;
      border: 1px solid #bfdbfe;
      border-radius: 999px;
      color: var(--brand);
      display: inline-flex;
      font-weight: 800;
      height: 1.65rem;
      justify-content: center;
      width: 1.65rem;
    }}
    .section-help {{ color: var(--muted); margin: .45rem 0 1rem; }}
    .field-grid {{ display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); }}
    label {{ color: #26364d; display: block; font-size: .92rem; font-weight: 700; margin-bottom: .35rem; }}
    input, select {{
      background: #fbfdff;
      border: 1px solid #cbd5e1;
      border-radius: .7rem;
      color: var(--text);
      font: inherit;
      padding: .72rem .85rem;
      transition: border-color .15s, box-shadow .15s;
      width: 100%;
    }}
    input:focus, select:focus {{
      border-color: var(--brand);
      box-shadow: 0 0 0 .22rem rgba(37, 99, 235, .16);
      outline: none;
    }}
    .field-checkbox {{ align-items: end; display: flex; min-height: 4.4rem; }}
    .toggle {{
      align-items: center;
      background: #f8fbff;
      border: 1px solid var(--border);
      border-radius: .8rem;
      cursor: pointer;
      display: flex;
      gap: .7rem;
      margin: 0;
      padding: .75rem .85rem;
      width: 100%;
    }}
    .toggle input {{ accent-color: var(--brand); height: 1.1rem; width: 1.1rem; }}
    .map-panel {{
      border: 1px solid var(--border);
      border-radius: .9rem;
      display: grid;
      gap: 1rem;
      grid-template-columns: minmax(12rem, 18rem) 1fr;
      margin-top: 1rem;
      overflow: hidden;
    }}
    .map-copy {{ background: #f8fbff; display: flex; flex-direction: column; gap: .5rem; padding: 1rem; }}
    .map-copy span {{ color: var(--muted); }}
    .map-copy a, .status-link {{ color: var(--brand); font-weight: 700; text-decoration: none; }}
    iframe {{ border: 0; min-height: 16rem; width: 100%; }}
    .actions {{ align-items: center; display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1.5rem; }}
    button {{
      background: var(--brand);
      border: 0;
      border-radius: .8rem;
      color: white;
      cursor: pointer;
      font: inherit;
      font-weight: 800;
      padding: .85rem 1.2rem;
    }}
    button:hover {{ background: var(--brand-dark); }}
    .message {{
      background: #ecfdf5;
      border: 1px solid #86efac;
      border-radius: .8rem;
      color: #14532d;
      padding: .9rem 1rem;
    }}
    @media (max-width: 720px) {{
      main {{ padding: 1rem; }}
      .hero {{ padding: 1.4rem; }}
      .map-panel {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <header class="hero">
      <h1>{title}</h1>
      <p class="subtitle">{subtitle}</p>
    </header>
    {body}
  </main>
  <script>
    (function () {{
      var lat = document.getElementById('lat');
      var lon = document.getElementById('lon');
      var frame = document.getElementById('location-map');
      var link = document.getElementById('open-map-link');
      function mapUrl(latitude, longitude) {{
        var delta = 0.03;
        var left = longitude - delta;
        var right = longitude + delta;
        var top = latitude + delta;
        var bottom = latitude - delta;
        return 'https://www.openstreetmap.org/export/embed.html?bbox=' +
          encodeURIComponent(left + ',' + bottom + ',' + right + ',' + top) +
          '&layer=mapnik&marker=' +
          encodeURIComponent(latitude + ',' + longitude);
      }}
      function updateMap() {{
        var latitude = parseFloat(lat.value);
        var longitude = parseFloat(lon.value);
        if (isNaN(latitude) || isNaN(longitude) || !frame || !link) {{
          return;
        }}
        frame.src = mapUrl(latitude, longitude);
        link.href = 'https://www.openstreetmap.org/?mlat=' + encodeURIComponent(latitude) +
          '&mlon=' + encodeURIComponent(longitude) + '#map=12/' +
          encodeURIComponent(latitude) + '/' + encodeURIComponent(longitude);
      }}
      if (lat && lon && frame && link) {{
        lat.addEventListener('change', updateMap);
        lon.addEventListener('change', updateMap);
      }}
    }}());
  </script>
</body>
</html>""".format(
            language=html.escape(language),
            title=html.escape(title),
            subtitle=html.escape(TEXT.get(language, TEXT["en"])["subtitle"]),
            body=body)

    def _section_title(self, config, key):
        language = self._language(config)
        return TEXT.get(language, TEXT["en"])["sections"][key]

    def _section_help(self, config, key):
        language = self._language(config)
        return TEXT.get(language, TEXT["en"])["help"][key]

    def _map_url(self, lat, lon):
        delta = 0.03
        bbox = "{},{},{},{}".format(lon - delta, lat - delta, lon + delta, lat + delta)
        return "https://www.openstreetmap.org/export/embed.html?" + urlencode({
            "bbox": bbox,
            "layer": "mapnik",
            "marker": "{},{}".format(lat, lon),
        })

    def _coerce_value(self, raw_value, field_type):
        if field_type == "bool":
            return raw_value == "true"
        if raw_value is None:
            raw_value = ""
        if field_type == "int":
            return int(raw_value)
        if field_type == "float":
            return float(raw_value)
        return raw_value.strip()

    def _field_definition(self, path):
        for field_path, label_key, field_type in CONFIG_FORM_FIELDS:
            if field_path == path:
                return label_key, field_type
        raise KeyError(path)

    def _text(self, config, key):
        language = self._language(config)
        return TEXT.get(language, TEXT["en"])[key]

    def _label(self, config, key):
        language = self._language(config)
        labels = TEXT.get(language, TEXT["en"])["labels"]
        return labels.get(key, TEXT["en"]["labels"][key])

    def _language(self, config):
        language = config.get("ui_lang", "en")
        if language not in SUPPORTED_LANGUAGES:
            language = language.split("_")[0].split("-")[0]
        if language not in TEXT:
            language = "en"
        return language


def main():
    parser = ArgumentParser("Runs the local PiWeatherRock config UI")
    parser.add_argument('-c', '--config', required=True,
                        help='Path to your config file')
    parser.add_argument('--host', default='127.0.0.1',
                        help='Host to bind to; defaults to localhost')
    parser.add_argument('--port', default=8888, type=int,
                        help='Port to bind to')
    args = parser.parse_args()

    config_file = os.path.abspath(args.config)
    cherrypy.config.update({
        'server.socket_host': args.host,
        'server.socket_port': args.port,
    })
    print("PiWeatherRock config UI: http://{}:{}".format(
        args.host, args.port))
    cherrypy.quickstart(ConfigWebApp(config_file))


if __name__ == '__main__':
    main()
