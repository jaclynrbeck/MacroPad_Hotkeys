# SPDX-FileCopyrightText: 2021 Phillip Burgess for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# MACROPAD Hotkeys example: Adobe Photoshop for Mac
# Colors = 0xRRGGBB

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'name' : 'Hotkeys', # Application name
    'macros' : [              # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0xF00030, 'Undo', [Keycode.COMMAND, 'z', {'repeat': 0.2}]),
        (0xF00030, 'Redo', [Keycode.COMMAND, 'y', {'repeat': 0.2}]),
        (0x3000F0, 'Cut', [Keycode.COMMAND, 'x']),
        # 2nd row ----------
        (0xF03000, 'Save', [Keycode.COMMAND, 's']),
        (0xF03000, 'Find', [Keycode.COMMAND, 'f']),
        (0x3000F0, 'Copy', [Keycode.COMMAND, 'c']),
        # 3rd row ----------
        (0x00F030, 'Refresh', [Keycode.COMMAND, 'r']),
        (0x00F030, 'New Tab', [Keycode.COMMAND, 't']),
        (0x3000F0, 'Paste', [Keycode.COMMAND, 'v']),
        # 4th row ----------
        (0x0030F0, 'Ctrl-C', [Keycode.CONTROL, 'c']),
        (0x0030F0, 'Ctrl-X', [Keycode.CONTROL, 'x']),
        (0x606060, '', []),

        # Encoder button ---
        (0x000000, '', [])
    ]
}
