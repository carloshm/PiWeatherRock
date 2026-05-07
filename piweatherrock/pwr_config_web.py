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
    field_name,
    get_config_value,
    load_config,
    SUPPORTED_LANGUAGES,
    set_config_value,
    validate_config,
    write_config_atomic,
)


TEXT = {'en': {'changes_applied': 'Changes applied',
        'config_error': 'Configuration error',
        'error': 'Error',
        'legend': 'PiWeatherRock configuration',
        'save': 'Save changes',
        'status_ok': 'OK: valid configuration. The UI will apply changes automatically.',
        'title': 'PiWeatherRock Config',
        'validate': 'Validate configuration',
        'labels': {'lat': 'Latitude',
                   'lon': 'Longitude',
                   'timezone': 'Timezone',
                   'ds_api_key': 'Open-Meteo identifier',
                   'units': 'Units',
                   'lang': 'Weather language',
                   'ui_lang': 'UI language',
                   'update_freq': 'Forecast frequency (seconds)',
                   'fullscreen': 'Fullscreen',
                   '12hour_disp': '12-hour format',
                   'icon_offset': 'Icon offset',
                   'info_pause': 'Info pause (seconds)',
                   'info_delay': 'Info delay (seconds)',
                   'daily_enabled': 'Daily page enabled',
                    'daily_pause': 'Daily pause (seconds)',
                    'hourly_enabled': 'Hourly page enabled',
                    'hourly_pause': 'Hourly pause (seconds)',
                    'info_enabled': 'Info page enabled',
                    'info_pause_plugin': 'Info page pause (seconds)',
                    'media_enabled': 'Local media page enabled',
                    'media_pause': 'Local media pause (seconds)',
                    'media_path': 'Local media folder',
                    'media_shuffle': 'Shuffle local media',
                    'media_fit': 'Media fit (contain, cover, stretch)',
                    'media_extensions': 'Media extensions',
                    'log_level': 'Log level'}},
 'es': {'changes_applied': 'Cambios aplicados',
        'config_error': 'Error de configuración',
        'error': 'Error',
        'legend': 'Configuración PiWeatherRock',
        'save': 'Guardar cambios',
        'status_ok': 'OK: configuración válida. La UI aplicará los cambios automáticamente.',
        'title': 'Configuración de PiWeatherRock',
        'validate': 'Validar configuración',
        'labels': {'lat': 'Latitud',
                   'lon': 'Longitud',
                   'timezone': 'Zona horaria',
                   'ds_api_key': 'Identificador Open-Meteo',
                   'units': 'Unidades',
                   'lang': 'Idioma meteorológico',
                   'ui_lang': 'Idioma de interfaz',
                   'update_freq': 'Frecuencia del pronóstico (segundos)',
                   'fullscreen': 'Pantalla completa',
                   '12hour_disp': 'Formato de 12 horas',
                   'icon_offset': 'Desplazamiento de iconos',
                   'info_pause': 'Pausa de información (segundos)',
                   'info_delay': 'Retraso de información (segundos)',
                   'daily_enabled': 'Página diaria activada',
                    'daily_pause': 'Pausa diaria (segundos)',
                    'hourly_enabled': 'Página horaria activada',
                    'hourly_pause': 'Pausa horaria (segundos)',
                    'info_enabled': 'Página de información activada',
                    'info_pause_plugin': 'Pausa de información (segundos)',
                    'media_enabled': 'Página de medios locales activada',
                    'media_pause': 'Pausa de medios locales (segundos)',
                    'media_path': 'Carpeta local de medios',
                    'media_shuffle': 'Medios locales en orden aleatorio',
                    'media_fit': 'Ajuste de medios (contain, cover, stretch)',
                    'media_extensions': 'Extensiones de medios',
                    'log_level': 'Nivel de log'}},
 'ca': {'changes_applied': 'Canvis aplicats',
        'config_error': 'Error de configuració',
        'error': 'Error',
        'legend': 'Configuració de PiWeatherRock',
        'save': 'Desa els canvis',
        'status_ok': 'OK: configuració vàlida. La UI aplicarà els canvis automàticament.',
        'title': 'Configuració de PiWeatherRock',
        'validate': 'Valida la configuració',
        'labels': {'lat': 'Latitud',
                   'lon': 'Longitud',
                   'timezone': 'Zona horària',
                   'ds_api_key': 'Identificador Open-Meteo',
                   'units': 'Unitats',
                   'lang': 'Idioma meteorològic',
                   'ui_lang': 'Idioma de la interfície',
                   'update_freq': 'Freqüència de la previsió (segons)',
                   'fullscreen': 'Pantalla completa',
                   '12hour_disp': 'Format de 12 hores',
                   'icon_offset': 'Desplaçament de les icones',
                   'info_pause': 'Pausa d’informació (segons)',
                   'info_delay': 'Retard d’informació (segons)',
                   'daily_enabled': 'Pàgina diària activada',
                    'daily_pause': 'Pausa diària (segons)',
                    'hourly_enabled': 'Pàgina horària activada',
                    'hourly_pause': 'Pausa horària (segons)',
                    'info_enabled': 'Pàgina d’informació activada',
                    'info_pause_plugin': 'Pausa d’informació (segons)',
                    'media_enabled': 'Pàgina de mitjans locals activada',
                    'media_pause': 'Pausa de mitjans locals (segons)',
                    'media_path': 'Carpeta local de mitjans',
                    'media_shuffle': 'Mitjans locals en ordre aleatori',
                    'media_fit': 'Ajust de mitjans (contain, cover, stretch)',
                    'media_extensions': 'Extensions de mitjans',
                    'log_level': 'Nivell de log'}},
 'gl': {'changes_applied': 'Cambios aplicados',
        'config_error': 'Erro de configuración',
        'error': 'Erro',
        'legend': 'Configuración de PiWeatherRock',
        'save': 'Gardar cambios',
        'status_ok': 'OK: configuración válida. A UI aplicará os cambios automaticamente.',
        'title': 'Configuración de PiWeatherRock',
        'validate': 'Validar configuración',
        'labels': {'lat': 'Latitude',
                   'lon': 'Lonxitude',
                   'timezone': 'Zona horaria',
                   'ds_api_key': 'Identificador Open-Meteo',
                   'units': 'Unidades',
                   'lang': 'Idioma meteorolóxico',
                   'ui_lang': 'Idioma da interface',
                   'update_freq': 'Frecuencia da predición (segundos)',
                   'fullscreen': 'Pantalla completa',
                   '12hour_disp': 'Formato de 12 horas',
                   'icon_offset': 'Desprazamento das iconas',
                   'info_pause': 'Pausa de información (segundos)',
                   'info_delay': 'Retardo de información (segundos)',
                   'daily_enabled': 'Páxina diaria activada',
                    'daily_pause': 'Pausa diaria (segundos)',
                    'hourly_enabled': 'Páxina horaria activada',
                    'hourly_pause': 'Pausa horaria (segundos)',
                    'info_enabled': 'Páxina de información activada',
                    'info_pause_plugin': 'Pausa de información (segundos)',
                    'media_enabled': 'Páxina de medios locais activada',
                    'media_pause': 'Pausa de medios locais (segundos)',
                    'media_path': 'Cartafol local de medios',
                    'media_shuffle': 'Medios locais en orde aleatoria',
                    'media_fit': 'Axuste de medios (contain, cover, stretch)',
                    'media_extensions': 'Extensións de medios',
                    'log_level': 'Nivel de log'}},
 'eu': {'changes_applied': 'Aldaketak aplikatu dira',
        'config_error': 'Konfigurazio-errorea',
        'error': 'Errorea',
        'legend': 'PiWeatherRock konfigurazioa',
        'save': 'Gorde aldaketak',
        'status_ok': 'OK: konfigurazioa baliozkoa da. UIak aldaketak automatikoki aplikatuko ditu.',
        'title': 'PiWeatherRock konfigurazioa',
        'validate': 'Balidatu konfigurazioa',
        'labels': {'lat': 'Latitudea',
                   'lon': 'Longitudea',
                   'timezone': 'Ordu-zona',
                   'ds_api_key': 'Open-Meteo identifikatzailea',
                   'units': 'Unitateak',
                   'lang': 'Eguraldiaren hizkuntza',
                   'ui_lang': 'Interfazearen hizkuntza',
                   'update_freq': 'Iragarpenaren maiztasuna (segundoak)',
                   'fullscreen': 'Pantaila osoa',
                   '12hour_disp': '12 orduko formatua',
                   'icon_offset': 'Ikonoen desplazamendua',
                   'info_pause': 'Informazio-pausa (segundoak)',
                   'info_delay': 'Informazio-atzerapena (segundoak)',
                   'daily_enabled': 'Eguneko orria gaituta',
                    'daily_pause': 'Eguneko pausa (segundoak)',
                    'hourly_enabled': 'Orduko orria gaituta',
                    'hourly_pause': 'Orduko pausa (segundoak)',
                    'info_enabled': 'Informazio-orria gaituta',
                    'info_pause_plugin': 'Informazio-pausa (segundoak)',
                    'media_enabled': 'Tokiko multimedia-orria gaituta',
                    'media_pause': 'Tokiko multimedia-pausa (segundoak)',
                    'media_path': 'Tokiko multimedia-karpeta',
                    'media_shuffle': 'Tokiko multimedia ausazko ordenan',
                    'media_fit': 'Multimedia doitzea (contain, cover, stretch)',
                    'media_extensions': 'Multimedia-luzapenak',
                    'log_level': 'Log-maila'}}}


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
        rows.append('<fieldset><legend>{}</legend>'.format(
            html.escape(self._text(config, "legend"))))
        for path, label_key, field_type in CONFIG_FORM_FIELDS:
            value = get_config_value(config, path)
            name = field_name(path)
            rows.append('<label for="{name}">{label}</label>'.format(
                name=html.escape(name),
                label=html.escape(self._label(config, label_key))))
            if field_type == "bool":
                checked = " checked" if value else ""
                rows.append('<input type="checkbox" id="{0}" name="{0}" value="true"{1}>'.format(
                    html.escape(name), checked))
            else:
                input_type = "number" if field_type in ("int", "float") else "text"
                step = ' step="any"' if field_type == "float" else ""
                rows.append('<input type="{type}" id="{name}" name="{name}" value="{value}"{step}>'.format(
                    type=input_type,
                    name=html.escape(name),
                    value=html.escape(str(value)),
                    step=step))
        rows.append('</fieldset>')
        rows.append('<button type="submit">{}</button>'.format(
            html.escape(self._text(config, "save"))))
        rows.append('</form>')
        rows.append('<p><a href="/status">{}</a></p>'.format(
            html.escape(self._text(config, "validate"))))
        return self._page(self._text(config, "title"), "\n".join(rows),
                          self._language(config))

    def _page(self, title, body, language="en"):
        return """<!doctype html>
<html lang="{language}">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: sans-serif; margin: 2rem; max-width: 48rem; }}
    label {{ display: block; font-weight: bold; margin-top: 1rem; }}
    input {{ box-sizing: border-box; max-width: 100%; padding: .4rem; width: 24rem; }}
    input[type=checkbox] {{ width: auto; }}
    button {{ margin-top: 1.5rem; padding: .6rem 1rem; }}
    .message {{ background: #eef8ee; border: 1px solid #7bbf7b; padding: .7rem; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  {body}
</body>
</html>""".format(
            language=html.escape(language),
            title=html.escape(title),
            body=body)

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
