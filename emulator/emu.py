"""Same step syntax as aoa.py, but sent to the emulator as hardware key events via `adb emu event send`."""
import sys, time, subprocess
HID = {0x28: 'ENTER', 0x29: 'ESCAPE', 0x2A: 'DEL', 0x2B: 'TAB', 0x2C: 'SPACE', 0x46: 'SYSRQ',
       0x4F: 'DPAD_RIGHT', 0x50: 'DPAD_LEFT', 0x51: 'DPAD_DOWN', 0x52: 'DPAD_UP', 0x80: 'VOLUME_UP', 0x81: 'VOLUME_DOWN', 0xF1: 'BACK', 0x2D: 'MINUS', 0x37: 'PERIOD', 0x4A: 'MOVE_HOME', 0x4D: 'MOVE_END', 0x4B: 'PAGE_UP', 0x4E: 'PAGE_DOWN', 0x4C: 'FORWARD_DEL', 0xE3: 'META_LEFT', 0x76: 'MENU'}
for i in range(26): HID[0x04 + i] = chr(ord('A') + i)
for i in range(9): HID[0x1E + i] = str(i + 1)
HID[0x27] = '0'
MODS = {0x01: 'CTRL_LEFT', 0x02: 'SHIFT_LEFT', 0x04: 'ALT_LEFT', 0x08: 'META_LEFT'}
def ev(*parts): subprocess.run(['adb', 'emu', 'event', 'send', *parts], capture_output=True)
def key(usage, mod=0):
    mods = [MODS[m] for m in MODS if mod & m]
    names = mods + ([HID[usage]] if usage else [])
    cmd = ['keycombination'] if len(names) > 1 else ['keyevent']
    subprocess.run(['adb', 'shell', 'input', 'keyboard', *cmd, *[f'KEYCODE_{n}' for n in names]], capture_output=True); time.sleep(0.12)
def char_usage(c):
    if c.isdigit(): return (0x27 if c == '0' else 0x1E + int(c) - 1), 0
    if c.isalpha(): return 0x04 + ord(c.lower()) - ord('a'), (0x02 if c.isupper() else 0)
    return {' ': (0x2C, 0), '_': (0x2C, 0), '-': (0x2D, 0), '.': (0x37, 0)}[c]
for step in sys.argv[1:]:
    name, *a = step.split(':')
    if name == 'wake': subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_WAKEUP'])
    elif name == 'type': [key(*char_usage(c)) for c in a[0]]
    elif name == 'enter': key(0x28)
    elif name == 'tab': key(0x2B, 0x02 if a and a[0] == 'shift' else 0)
    elif name == 'esc': key(0x29)
    elif name == 'key': key(int(a[0], 16), int(a[1], 16) if len(a) > 1 else 0)
    elif name == 'sleep': time.sleep(float(a[0]))
    else: sys.exit(f'unsupported step {step}')
    time.sleep(0.4)
