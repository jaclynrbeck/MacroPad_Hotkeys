class PixelController:
    BRIGHTNESS = 0.1
    MAX_LEDS = 12

    def __init__(self, macropad):
        self.pixels = macropad.pixels
        self.pixels.auto_write = False
        self.pixels.brightness = PixelController.BRIGHTNESS
        self.keycolors = []

    def __del__(self):
        self.pixels.clear()

    def register(self, macros):
        self.keycolors = list(map(lambda m: m.color if m else 0x000000, macros))
        for i in range(PixelController.MAX_LEDS):
            if i < len(self.keycolors):
                self.pixels[i] = self.keycolors[i]
            else:
                self.pixels[i] = 0x000000
        self.pixels.show()

    def pressed(self, key_index):
        if key_index < PixelController.MAX_LEDS:
            self.pixels[key_index] = 0xFFFFFF
            self.pixels.show()

    def released(self, key_index):
        if key_index < PixelController.MAX_LEDS:
            self.pixels[key_index] = self.keycolors[key_index]
            self.pixels.show()

    def sleep(self):
        self.pixels.brightness = 0.0
        self.pixels.show()

    def wake(self):
        self.pixels.brightness = PixelController.BRIGHTNESS
        self.pixels.show()
