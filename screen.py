import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect

class ScreenController:
    MAX_LABELS = 12

    def __init__(self, macropad):
        self.macropad = macropad
        self.display = macropad.display
        self.display.auto_refresh = False

    def __del__(self):
        self.display = None
        self.macropad = None

    def initialize(self):
        self.group = displayio.Group()
        for key_index in range(ScreenController.MAX_LABELS):
            x = key_index % 3
            y = key_index // 3
            self.group.append(
                label.Label(
                    terminalio.FONT,
                    text='',
                    color=0xFFFFFF,
                    background_color=0x000000,
                    anchored_position=(
                        (self.display.width - 1) * x / 2,
                        self.display.height - 1 - (3 - y) * 12
                    ),
                    anchor_point=(x / 2, 1.0)
                )
            )
        self.group.append(Rect(0, 0, self.display.width, 12, fill=0xFFFFFF))
        self.group.append(
            label.Label(
                terminalio.FONT,
                text='',
                color=0x000000,
                anchored_position=(self.display.width//2, -1),
                anchor_point=(0.5, 0.0)
            )
        )
        self.display.root_group = self.group

    def setTitle(self, text):
        self.group[13].text = text
        self.display.refresh()

    def register(self, macros):
        for i in range(ScreenController.MAX_LABELS):
            if i < len(macros):
                self.group[i].text = macros[i].name
            else:
                self.group[i].text = ''
        self.display.refresh()

    def pressed(self, key_index):
        if key_index < ScreenController.MAX_LABELS:
            self.group[key_index].color = 0x000000
            self.group[key_index].background_color = 0xFFFFFF
            self.display.refresh()

    def released(self, key_index):
        if key_index < ScreenController.MAX_LABELS:
            self.group[key_index].color = 0xFFFFFF
            self.group[key_index].background_color = 0x000000
            self.display.refresh()

    def sleep(self):
        self.macropad.display_sleep = True

    def wake(self):
        self.macropad.display_sleep = False
