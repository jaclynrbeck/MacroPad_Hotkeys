# Macropad_Hotkeys

Personal fork of the code from ["Macropad Hotkeys"](https://learn.adafruit.com/macropad-hotkeys/). I've made the following modifications:

- Created my own list of macro hotkeys for a Mac computer (macros/hotkeys.py)
- Added code to allow repeated firing when a key is held down for more than 0.5 seconds. 
	- Must be explicitly enabled for each desired key via the command list. 

<br />
Repeated firing can be added to any macro command by adding 
`'repeat': <float>` to a dictionary in the command list.

<br />
Example configuration for repeating key: 

`(0xF00030, 'Undo', [Keycode.COMMAND, 'z', {'repeat': 0.2}])`

This will send CMD-Z, and if the key is held down for longer than 0.5 seconds,
it will send CMD-Z every 0.2 seconds until the key is released. 
 
<br />
Another example, using mouse commands:

`(0x202020, 'Right', [{'x':10, 'repeat': 0.1}])`

This will repeatedly move the mouse cursor right by 10 px, as long as the key
is held down for longer than 0.5 seconds. A quick press and release will move
the mouse once. 
 
<br />
This code was built using [CircuitPython 7.3.3 for the MacroPad RP2040](https://circuitpython.org/board/adafruit_macropad_rp2040/).

