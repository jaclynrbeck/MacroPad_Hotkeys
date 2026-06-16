# SPDX-FileCopyrightText: 2021 Phillip Burgess for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
A macro/hotkey program for Adafruit MACROPAD. Macro setups are stored in the
/macros folder (configurable below), load up just the ones you're likely to
use. Plug into computer's USB port, use dial to select an application macro
set, press MACROPAD keys to send key sequences and other USB protocols.
"""

# pylint: disable=import-error, unused-import, too-few-public-methods

import os
import time
from adafruit_macropad import MacroPad

from autoscreen import AutoOffScreen
from pixels import PixelController
from screen import ScreenController


# CONFIGURABLES ------------------------

MACRO_FOLDER = '/macros'


# CLASSES AND FUNCTIONS ----------------

class Macro:
    def __init__(self, macro):
        self.color, self.name, self.sequence = macro[0:3]
        self.repeat = False
        self.repeat_delay = 0

        # Backward compatibility -- don't require a 4th entry
        if len(macro) > 3 and isinstance(macro[3], dict):
            self.repeat_delay = macro[3].get("repeat", 0)
            self.repeat = self.repeat_delay > 0

class App:
    """ Class representing a host-side application, for which we have a set
        of macro sequences. Project code was originally more complex and
        this was helpful, but maybe it's excessive now?"""
    def __init__(self, appdata):
        self.name = appdata['name']
        self.macros = [Macro(x) for x in appdata['macros']]

    def __len__(self):
        return len(self.macros)

    def activate(self):
        """ Activate application settings; update OLED labels and LED
            colors. """
        screen.setTitle(self.name)
        screen.register(self.macros)
        pixels.register(self.macros)

        macropad.keyboard.release_all()
        macropad.consumer_control.release()
        macropad.mouse.release_all()
        macropad.stop_tone()


# INITIALIZATION -----------------------

macropad = MacroPad()
pixels = PixelController(macropad)
screen = ScreenController(macropad)

# Set up timeout
autoscreen = AutoOffScreen(30)

# Set up the screen display
screen.initialize()

# Load all the macro key setups from .py files in MACRO_FOLDER
apps = []
files = os.listdir(MACRO_FOLDER)
files.sort()
for filename in files:
    if filename.endswith('.py') and not filename.startswith('._'):
        try:
            module = __import__(MACRO_FOLDER + '/' + filename[:-3])
            apps.append(App(module.app))
        except Exception as err:
            print("ERROR in", filename)
            import traceback
            traceback.print_exception(err, err, err.__traceback__)

if not apps:
    screen.setTitle('NO MACRO FILES FOUND')
    while True:
        time.sleep(60.0)

last_position = None
app_index = 0
apps[app_index].activate()

# Added: ability to repeat key press when held down
repeating = False
last_press_time = 0
last_key_number = None
repeat_delay = 1

def lights_on():
    screen.wake()
    pixels.wake()

def lights_off():
    screen.sleep()
    pixels.sleep()

autoscreen.handle_on = lights_on
autoscreen.handle_off = lights_off

def key_press(key_number):
    global repeating, last_key_number, repeat_delay, last_press_time

    current_macro = apps[app_index].macros[key_number]
    sequence = current_macro.sequence

    # 'sequence' is an arbitrary-length list, each item is one of:
    # Positive integer (e.g. Keycode.KEYPAD_MINUS): key pressed
    # Negative integer: (absolute value) key released
    # Float (e.g. 0.25): delay in seconds
    # String (e.g. "Foo"): corresponding keys pressed & released
    # List []: one or more Consumer Control codes (can also do float delay)
    # Dict {}: mouse buttons/motion (might extend in future)
    pixels.pressed(key_number)
    screen.pressed(key_number)

    if current_macro.repeat:
        repeating = True
        last_key_number = key_number
        repeat_delay = current_macro.repeat_delay
        last_press_time = time.monotonic_ns()

    for item in sequence:
        if isinstance(item, int):
            if item >= 0:
                macropad.keyboard.press(item)
            else:
                macropad.keyboard.release(-item)
        elif isinstance(item, float):
            time.sleep(item)
        elif isinstance(item, str):
            macropad.keyboard_layout.write(item)
        elif isinstance(item, list):
            for code in item:
                if isinstance(code, int):
                    macropad.consumer_control.release()
                    macropad.consumer_control.press(code)
                if isinstance(code, float):
                    time.sleep(code)
        elif isinstance(item, dict):
            if 'buttons' in item:
                if item['buttons'] >= 0:
                    macropad.mouse.press(item['buttons'])
                else:
                    macropad.mouse.release(-item['buttons'])
            macropad.mouse.move(item['x'] if 'x' in item else 0,
                                item['y'] if 'y' in item else 0,
                                item['wheel'] if 'wheel' in item else 0)
            if 'tone' in item:
                if item['tone'] > 0:
                    macropad.stop_tone()
                    macropad.start_tone(item['tone'])
                else:
                    macropad.stop_tone()
            elif 'play' in item:
                macropad.play_file(item['play'])

def key_release(key_number):
    global repeating, last_key_number

    current_macro = apps[app_index].macros[key_number]
    sequence = current_macro.sequence

    # Release any still-pressed keys, consumer codes, mouse buttons
    # Keys and mouse buttons are individually released this way (rather
    # than release_all()) because pad supports multi-key rollover, e.g.
    # could have a meta key or right-mouse held down by one macro and
    # press/release keys/buttons with others. Navigate popups, etc.
    for item in sequence:
        if isinstance(item, int):
            if item >= 0:
                macropad.keyboard.release(item)
        elif isinstance(item, dict):
            if 'buttons' in item:
                if item['buttons'] >= 0:
                    macropad.mouse.release(item['buttons'])
            elif 'tone' in item:
                macropad.stop_tone()
    macropad.consumer_control.release()
    repeating = False
    last_key_number = None

    pixels.released(key_number)
    screen.released(key_number)

# MAIN LOOP ----------------------------

while True:
    autoscreen.poll()

    macropad.encoder_switch_debounced.update()
    event = macropad.keys.events.get()

    # Refresh sleep timer for any activity
    if (
        event or repeating or macropad.encoder != last_position or
        macropad.encoder_switch_debounced.pressed or
        macropad.encoder_switch_debounced.released
    ):
        autoscreen.update_active()

    # Read encoder position. If it's changed, switch apps.
    if macropad.encoder != last_position:
        last_position = macropad.encoder
        app_index = last_position % len(apps)
        apps[app_index].activate()

    # Handle encoder button. If state has changed, and if there's a
    # corresponding macro, set up variables to act on this just like
    # the keypad keys, as if it were a 13th key/macro.
    elif macropad.encoder_switch_debounced.pressed:
        key_press(key_number=12)

    elif macropad.encoder_switch_debounced.released:
        key_release(key_number=12)

    # Key event
    elif event and event.pressed:
        key_press(event.key_number)

    elif event and event.released:
        key_release(event.key_number)

    # No new key presses but a key is still held down and is allowed to
    # repeat key strokes
    elif repeating:
        delay = repeat_delay * 1e9  # In nanoseconds

        # Handle wraparound of ns clock with abs()
        now = time.monotonic_ns()
        time_passed = abs(now - last_press_time)

        if time_passed >= delay:
            macropad.keyboard.release_all()
            key_press(last_key_number)
