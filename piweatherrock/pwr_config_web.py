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
    set_config_value,
    validate_config,
    write_config_atomic,
)


TEXT = {
    "en": {
        "changes_applied": "Changes applied",
        "config_error": "Configuration error",
        "error": "Error",
        "legend": "PiWeatherRock configuration",
        "save": "Save changes",
        "status_ok": "OK: valid configuration. The UI will apply changes automatically.",
        "title": "PiWeatherRock Config",
        "validate": "Validate configuration",
    },
    "es": {
        "changes_applied": "Cambios aplicados",
        "config_error": "Error de configuración",
        "error": "Error",
        "legend": "Configuración PiWeatherRock",
        "save": "Guardar cambios",
        "status_ok": "OK: configuración válida. La UI aplicará los cambios automáticamente.",
        "title": "PiWeatherRock Config",
        "validate": "Validar configuración",
    },
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
            for path, label, field_type in CONFIG_FORM_FIELDS:
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
        for path, label, field_type in CONFIG_FORM_FIELDS:
            value = get_config_value(config, path)
            name = field_name(path)
            rows.append('<label for="{name}">{label}</label>'.format(
                name=html.escape(name), label=html.escape(label)))
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
        return self._page(self._text(config, "title"), "\n".join(rows))

    def _page(self, title, body):
        return """<!doctype html>
<html lang="es">
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
</html>""".format(title=html.escape(title), body=body)

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
        language = config.get("ui_lang", "en")
        if language not in TEXT:
            language = language.split("_")[0].split("-")[0]
        return TEXT.get(language, TEXT["en"])[key]


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
