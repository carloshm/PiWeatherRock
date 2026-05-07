# -*- coding: utf-8 -*-
"""Configuration loading, validation, and hot-reload helpers."""

import copy
import json
import os
import shutil
import tempfile
import time


class ConfigError(Exception):
    """Raised when a configuration file cannot be loaded or validated."""


REQUIRED_FIELDS = {
    "ds_api_key": str,
    "lat": (int, float),
    "lon": (int, float),
    "units": str,
    "lang": str,
    "ui_lang": str,
    "timezone": str,
    "fullscreen": bool,
    "12hour_disp": bool,
    "icon_offset": (int, float),
    "update_freq": int,
    "info_pause": int,
    "info_delay": int,
    "plugins": dict,
    "log_level": str,
}

PLUGIN_FIELDS = {
    "enabled": bool,
    "pause": int,
}

WEATHER_RELOAD_PATHS = {
    ("ds_api_key",),
    ("lat",),
    ("lon",),
    ("units",),
    ("lang",),
    ("timezone",),
    ("update_freq",),
}

DISPLAY_RELOAD_PATHS = {
    ("fullscreen",),
}

SUN_TIME_RELOAD_PATHS = {
    ("12hour_disp",),
    ("ui_lang",),
}

LOG_RELOAD_PATHS = {
    ("log_level",),
}

ROTATION_RELOAD_PATHS = {
    ("info_pause",),
    ("info_delay",),
    ("plugins", "daily", "pause"),
    ("plugins", "hourly", "pause"),
    ("plugins", "daily", "enabled"),
    ("plugins", "hourly", "enabled"),
}


CONFIG_FORM_FIELDS = [
    (("lat",), "Latitud", "float"),
    (("lon",), "Longitud", "float"),
    (("timezone",), "Zona horaria", "text"),
    (("ds_api_key",), "Identificador Open-Meteo", "text"),
    (("units",), "Unidades", "text"),
    (("lang",), "Idioma meteorológico", "text"),
    (("ui_lang",), "Idioma de interfaz", "text"),
    (("update_freq",), "Frecuencia forecast (segundos)", "int"),
    (("fullscreen",), "Pantalla completa", "bool"),
    (("12hour_disp",), "Formato 12 horas", "bool"),
    (("icon_offset",), "Offset de iconos", "float"),
    (("info_pause",), "Pausa info (segundos)", "int"),
    (("info_delay",), "Retraso info (segundos)", "int"),
    (("plugins", "daily", "enabled"), "Página diaria activa", "bool"),
    (("plugins", "daily", "pause"), "Pausa diaria (segundos)", "int"),
    (("plugins", "hourly", "enabled"), "Página horaria activa", "bool"),
    (("plugins", "hourly", "pause"), "Pausa horaria (segundos)", "int"),
    (("log_level",), "Nivel de log", "text"),
]


def load_config(config_file):
    """Load and validate a PiWeatherRock JSON configuration."""
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except (IOError, ValueError) as exc:
        raise ConfigError("Could not load config file '{}': {}".format(
            config_file, exc))

    validate_config(config)
    return config


def validate_config(config):
    """Validate required fields and value ranges."""
    errors = []

    if not isinstance(config, dict):
        raise ConfigError("Config must be a JSON object")

    for key, expected_type in REQUIRED_FIELDS.items():
        if key not in config:
            errors.append("Missing required field '{}'".format(key))
        elif not _is_expected_type(config[key], expected_type):
            errors.append("Field '{}' has invalid type".format(key))

    plugins = config.get("plugins")
    if isinstance(plugins, dict):
        for plugin_name in ("daily", "hourly"):
            plugin_config = plugins.get(plugin_name)
            if not isinstance(plugin_config, dict):
                errors.append("Missing plugin '{}' configuration".format(plugin_name))
                continue
            for key, expected_type in PLUGIN_FIELDS.items():
                if key not in plugin_config:
                    errors.append("Missing plugins.{}.{}".format(plugin_name, key))
                elif not _is_expected_type(plugin_config[key], expected_type):
                    errors.append("Field plugins.{}.{} has invalid type".format(
                        plugin_name, key))

    _validate_range(config, "lat", -90, 90, errors)
    _validate_range(config, "lon", -180, 180, errors)
    _validate_positive_int(config, "update_freq", errors)
    _validate_positive_int(config, "info_pause", errors)
    _validate_positive_int(config, "info_delay", errors)

    if isinstance(plugins, dict):
        for plugin_name in ("daily", "hourly"):
            plugin_config = plugins.get(plugin_name)
            if isinstance(plugin_config, dict):
                _validate_positive_int(plugin_config, "pause", errors,
                                       "plugins.{}.pause".format(plugin_name))

    if errors:
        raise ConfigError("Invalid configuration: " + "; ".join(errors))

    return True


def merge_defaults(config, default_config):
    """Return a copy of config with missing keys filled from default_config."""
    merged = copy.deepcopy(config)
    for key, value in default_config.items():
        if key not in merged:
            merged[key] = copy.deepcopy(value)
        elif isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_defaults(merged[key], value)
    return merged


def write_config_atomic(config_file, config, backup=True):
    """Validate and write config atomically, preserving the previous file."""
    validate_config(config)

    config_dir = os.path.dirname(os.path.abspath(config_file)) or "."
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)

    if backup and os.path.exists(config_file):
        shutil.copy2(config_file, config_file + ".bak")

    fd, temp_file = tempfile.mkstemp(
        prefix=".{}.".format(os.path.basename(config_file)),
        suffix=".tmp",
        dir=config_dir)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(config, f, indent=4, sort_keys=True)
            f.write("\n")
        os.replace(temp_file, config_file)
    except Exception:
        try:
            os.remove(temp_file)
        except OSError:
            pass
        raise


def diff_config(old_config, new_config):
    """Return leaf paths whose values changed between two config dicts."""
    changed = set()
    _collect_diff((), old_config, new_config, changed)
    return changed


def config_changed(changed_paths, interesting_paths):
    """Return True if any changed path affects one of the interesting paths."""
    for changed_path in changed_paths:
        for interesting_path in interesting_paths:
            if _path_related(changed_path, interesting_path):
                return True
    return False


def get_config_value(config, path):
    value = config
    for part in path:
        value = value[part]
    return value


def set_config_value(config, path, value):
    target = config
    for part in path[:-1]:
        target = target.setdefault(part, {})
    target[path[-1]] = value


def field_name(path):
    return "__".join(path)


class ConfigWatcher:
    """Polls a config file and reports validated changes."""

    def __init__(self, config_file, interval=1.0):
        self.config_file = config_file
        self.interval = interval
        self.last_check = 0
        self.last_signature = file_signature(config_file)

    def changed_config(self):
        now = time.time()
        if now - self.last_check < self.interval:
            return None
        self.last_check = now

        signature = file_signature(self.config_file)
        if signature == self.last_signature:
            return None

        config = load_config(self.config_file)
        return signature, config

    def commit(self, signature):
        self.last_signature = signature

    def sync_signature(self):
        self.last_signature = file_signature(self.config_file)


def file_signature(config_file):
    stat = os.stat(config_file)
    mtime = getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1000000000))
    return mtime, stat.st_size


def _is_expected_type(value, expected_type):
    if expected_type is bool:
        return isinstance(value, bool)
    if expected_type in (int, (int, float)):
        return isinstance(value, expected_type) and not isinstance(value, bool)
    return isinstance(value, expected_type)


def _validate_range(config, key, minimum, maximum, errors):
    value = config.get(key)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < minimum or value > maximum:
            errors.append("Field '{}' must be between {} and {}".format(
                key, minimum, maximum))


def _validate_positive_int(config, key, errors, display_name=None):
    value = config.get(key)
    if isinstance(value, int) and not isinstance(value, bool) and value <= 0:
        errors.append("Field '{}' must be greater than 0".format(
            display_name or key))


def _collect_diff(path, old_value, new_value, changed):
    if isinstance(old_value, dict) and isinstance(new_value, dict):
        keys = set(old_value.keys()) | set(new_value.keys())
        for key in keys:
            _collect_diff(path + (key,), old_value.get(key), new_value.get(key),
                          changed)
    elif old_value != new_value:
        changed.add(path)


def _path_related(changed_path, interesting_path):
    shortest = min(len(changed_path), len(interesting_path))
    return changed_path[:shortest] == interesting_path[:shortest]
