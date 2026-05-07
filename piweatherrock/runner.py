# -*- coding: utf-8 -*-
# Copyright (c) 2014 Jim Kemp <kemp.jim@gmail.com>
# Copyright (c) 2017 Gene Liverman <gene@technicalissues.us>
# Distributed under the MIT License (https://opensource.org/licenses/MIT)

import pygame
import sys
import time

# pylint is mad about thise locals regardless of how they are used. with
# that being the case, I decided to have the lint error here instead of
# every place they get used. PR's welcome to make pylint happy about this
# and pygame.quit()
from pygame.locals import QUIT, VIDEORESIZE, KEYDOWN, K_KP_ENTER, K_q, K_d, K_h, K_i, K_s

# local imports
from piweatherrock.config_manager import (
    ConfigError,
    ConfigWatcher,
    ROTATION_RELOAD_PATHS,
    config_changed,
    diff_config,
    load_config,
)
from piweatherrock.weather import Weather
from piweatherrock.plugin_weather_daily import PluginWeatherDaily
from piweatherrock.plugin_weather_hourly import PluginWeatherHourly
from piweatherrock.plugin_info import PluginInfo


LOOPS_PER_SECOND = 10


class Runner:

    def __init__(self):
        self.current_screen = None
        self.d_count = 1
        self.h_count = 0
        self.running = False
        self.seconds = 0
        self.non_weather_timeout = 0
        self.periodic_info_activation = 0
        self.config = None
        self.my_weather_rock = None
        self.daily = None
        self.hourly = None
        self.info = None
        self.config_watcher = None

    def main(self, config_file):
        self.config = load_config(config_file)
        self.config_watcher = ConfigWatcher(config_file)

        pygame.init()
        # Create an instance of the main application class
        self.my_weather_rock = Weather(config_file)

        # Create an instance of each plugin that will be used
        self.daily = PluginWeatherDaily(self.my_weather_rock)
        self.hourly = PluginWeatherHourly(self.my_weather_rock)
        self.info = PluginInfo(self.my_weather_rock)

        # Default to weather mode. Showing daily weather first.
        self.switch_to_default_weather_screen()

        # Stay running while True
        self.running = True

        # Seconds Placeholder to pace display
        self.seconds = 0

        # Display timeout to automatically switch back to weather display.
        self.non_weather_timeout = 0

        # Switch to info periodically to prevent screen burn.
        self.periodic_info_activation = 0

        # Loads data from Open-Meteo API
        if not self.my_weather_rock.get_forecast():
            self.my_weather_rock.log.exception(
                "Error: no data from Open-Meteo API.")
            self.running = False

        ##################################################################
        #                        Main progam loop                        #
        ##################################################################
        while self.running:
            # Look for and process keyboard events to change modes.
            self.process_pygame_events()
            self.check_config_reload()
            self.screen_switcher()

            # Loop timer.
            pygame.time.wait(100)

        # When the main program loop is exited, exit the application
        pygame.quit()

    def process_pygame_events(self):
        """
        pygame events are how we learn about a window being closed or
        resized or a key being pressed. This function looks for the events
        we care about and reacts when needed.
        """

        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == VIDEORESIZE:
                self.my_weather_rock.sizing(event.size)
            elif event.type == KEYDOWN:

                # On 'q' or keypad enter key, quit the program.
                if ((event.key == K_KP_ENTER) or (event.key == K_q)):
                    self.running = False

                # On 'd' key, set mode to 'daily weather'.
                elif event.key == K_d:
                    self.switch_to_weather_screen('d')

                # on 'h' key, set mode to 'hourly weather'
                elif event.key == K_h:
                    self.switch_to_weather_screen('h')

                # On 'i' key, set mode to 'info'.
                elif event.key == K_i:
                    self.current_screen = 'i'
                    self.d_count = 0
                    self.h_count = 0
                    self.non_weather_timeout = 0
                    self.periodic_info_activation = 0

                # On 's' key, save a screen shot.
                elif event.key == K_s:
                    self.my_weather_rock.screen_cap()

    def screen_switcher(self):
        """
        This function takes care of cycling through the different screens
        on a regular basis.
        """
        self.ensure_current_screen_enabled()

        # Automatically switch back to weather display after a couple minutes
        if self.current_screen not in ('d', 'h'):
            self.periodic_info_activation = 0
            self.non_weather_timeout += 1
            self.d_count = 0
            self.h_count = 0

            # Default in config.json.sample: pause for 5 minutes on info screen
            enabled_weather_screens = self.enabled_weather_screens()
            if (enabled_weather_screens
                    and self.non_weather_timeout > (
                        self.config["info_pause"] * LOOPS_PER_SECOND)):
                self.switch_to_default_weather_screen()
                self.my_weather_rock.log.info("Switching to weather mode")
        else:
            self.non_weather_timeout = 0
            self.periodic_info_activation += 1

            # Default is to flip between 2 weather screens
            # for 15 minutes before showing info screen.
            if self.periodic_info_activation > (
                    self.config["info_delay"] * LOOPS_PER_SECOND):
                self.current_screen = 'i'
                self.my_weather_rock.log.info("Switching to info mode")
            elif (self.periodic_info_activation % (
                    ((self.config["plugins"]["daily"]["pause"] * self.d_count)
                        + (self.config["plugins"]["hourly"]["pause"] * self.h_count))
                    * LOOPS_PER_SECOND)) == 0:
                self.switch_to_next_weather_screen()

        # Daily Weather Display Mode
        if self.current_screen == 'd':
            # Update / Refresh the display after each second.
            if self.seconds != time.localtime().tm_sec:
                self.seconds = time.localtime().tm_sec
                try:
                    self.daily.disp_daily(self.my_weather_rock)
                except Exception:
                    self.my_weather_rock.log.exception(
                        "Error rendering daily screen")

            # Once the screen is updated, we have a full second to get the
            # weather. Once per minute, check to see if its time to get a
            # new set of data from the API.
            if self.seconds == 0:
                self.check_forecast()

        # Hourly Weather Display Mode
        elif self.current_screen == 'h':
            # Update / Refresh the display after each second.
            if self.seconds != time.localtime().tm_sec:
                self.seconds = time.localtime().tm_sec
                try:
                    self.hourly.disp_hourly(self.my_weather_rock)
                except Exception:
                    self.my_weather_rock.log.exception(
                        "Error rendering hourly screen")

            # Once the screen is updated, we have a full second to get the
            # weather. Once per minute, check to see if its time to get a
            # new set of data from the API.
            if self.seconds == 0:
                self.check_forecast()

        # Info Screen Display Mode
        elif self.current_screen == 'i':
            # Pace the screen updates to once per second.
            if self.seconds != time.localtime().tm_sec:
                self.seconds = time.localtime().tm_sec

                # Disaplay information about the application along with the
                # time of sunrise and sunset.
                try:
                    self.info.disp_info(self.my_weather_rock)
                except Exception:
                    self.my_weather_rock.log.exception(
                        "Error rendering info screen")

    def check_forecast(self):
        try:
            self.my_weather_rock.get_forecast()
        # includes simplejson.decoder.JSONDecodeError
        except ValueError:
            self.my_weather_rock.log.exception(
                f"Decoding JSON has failed: {sys.exc_info()[0]}")
        except BaseException:
            self.my_weather_rock.log.exception(
                f"Unexpected error: {sys.exc_info()[0]}")

    def check_config_reload(self):
        try:
            changed = self.config_watcher.changed_config()
        except ConfigError as e:
            self.config_watcher.sync_signature()
            self.my_weather_rock.log.warning(
                f"Ignoring invalid config reload: {e}")
            return
        except OSError as e:
            self.my_weather_rock.log.warning(
                f"Could not check config reload: {e}")
            return

        if changed is None:
            return

        signature, new_config = changed
        changed_paths = diff_config(self.config, new_config)
        try:
            self.my_weather_rock.reload_config(new_config, changed_paths)
        except Exception:
            self.my_weather_rock.log.exception(
                "Error applying config reload")
            return

        self.config = new_config
        if config_changed(changed_paths, ROTATION_RELOAD_PATHS):
            self.periodic_info_activation = 0
            self.non_weather_timeout = 0
            self.ensure_current_screen_enabled()

        self.config_watcher.commit(signature)
        self.my_weather_rock.log.info("Configuration reloaded")

    def enabled_weather_screens(self):
        enabled = []
        if self.config["plugins"]["daily"].get("enabled", True):
            enabled.append('d')
        if self.config["plugins"]["hourly"].get("enabled", True):
            enabled.append('h')
        return enabled

    def ensure_current_screen_enabled(self):
        if self.current_screen in ('d', 'h'):
            if self.current_screen not in self.enabled_weather_screens():
                self.switch_to_default_weather_screen()

    def switch_to_default_weather_screen(self):
        enabled = self.enabled_weather_screens()
        if not enabled:
            self.current_screen = 'i'
            self.d_count = 0
            self.h_count = 0
        else:
            self.switch_to_weather_screen(enabled[0])

    def switch_to_weather_screen(self, screen):
        if screen not in self.enabled_weather_screens():
            self.my_weather_rock.log.warning(
                f"Ignoring disabled weather screen: {screen}")
            return

        self.current_screen = screen
        self.d_count = 1 if screen == 'd' else 0
        self.h_count = 1 if screen == 'h' else 0
        self.non_weather_timeout = 0
        self.periodic_info_activation = 0

    def switch_to_next_weather_screen(self):
        enabled = self.enabled_weather_screens()
        if not enabled:
            self.current_screen = 'i'
            self.d_count = 0
            self.h_count = 0
            return

        if self.current_screen == 'd' and 'h' in enabled:
            self.advance_weather_screen('h', "Switching to HOURLY")
        elif self.current_screen == 'h' and 'd' in enabled:
            self.advance_weather_screen('d', "Switching to DAILY")
        elif enabled[0] == 'd':
            self.advance_weather_screen('d', "Staying on DAILY")
        else:
            self.advance_weather_screen('h', "Staying on HOURLY")

    def advance_weather_screen(self, screen, message):
        self.my_weather_rock.log.info(message)
        self.current_screen = screen
        if screen == 'd':
            self.d_count += 1
        else:
            self.h_count += 1
