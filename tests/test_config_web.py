import sys
import types
import unittest


if "cherrypy" not in sys.modules:
    cherrypy = types.ModuleType("cherrypy")
    cherrypy.expose = lambda function: function
    sys.modules["cherrypy"] = cherrypy

from piweatherrock.pwr_config_web import ConfigWebApp


VALID_CONFIG = {
    "ds_api_key": "openmeteo-request-piweatherrock",
    "lat": 40.299457,
    "lon": -3.743399,
    "units": "si",
    "lang": "es",
    "ui_lang": "es",
    "timezone": "Europe/Madrid",
    "fullscreen": True,
    "12hour_disp": False,
    "icon_offset": -23.5,
    "update_freq": 900,
    "info_pause": 60,
    "info_delay": 900,
    "plugins": {
        "daily": {"pause": 60, "enabled": True},
        "hourly": {"pause": 60, "enabled": True},
        "info": {"pause": 300, "enabled": True},
        "media": {
            "pause": 20,
            "enabled": False,
            "path": "",
            "shuffle": False,
            "fit": "contain",
            "extensions": "jpg,jpeg,png,gif,bmp,mp4,mov,m4v,avi,webm",
        },
    },
    "log_level": "INFO",
}


class ConfigWebTest(unittest.TestCase):
    def test_form_groups_fields_with_help_and_map(self):
        html = ConfigWebApp("config.json")._render_form(VALID_CONFIG)

        self.assertIn('<section class="card" aria-labelledby="location-title">', html)
        self.assertIn('title="Coordenadas y zona horaria', html)
        self.assertIn('id="location-map"', html)
        self.assertIn('openstreetmap.org/export/embed.html', html)

    def test_form_uses_selects_for_constrained_values(self):
        html = ConfigWebApp("config.json")._render_form(VALID_CONFIG)

        self.assertIn('<select id="timezone" name="timezone">', html)
        self.assertIn('<option value="Europe/Madrid" selected>Europe/Madrid</option>', html)
        self.assertIn('<select id="lang" name="lang">', html)
        self.assertIn('<select id="plugins__media__fit" name="plugins__media__fit">', html)

    def test_pause_labels_distinguish_global_and_media_pauses(self):
        html = ConfigWebApp("config.json")._render_form(VALID_CONFIG)

        self.assertIn('Pausa entre ciclos completos de páginas', html)
        self.assertIn('Pausa entre archivos de medios locales', html)


if __name__ == "__main__":
    unittest.main()
