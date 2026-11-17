# /// script
# dependencies = ["pyusb"]
# ///
"""Blind Android control via AOA2 HID (no adb). Steps on the command line, e.g.:
   aoa.py wake swipeup type:1234 enter tap:0.5:0.5 sleep:1 key:0x2b"""
import os
import sys, time, struct, usb.core

KBD, TOUCH = 1, 2
KBD_DESC = bytes.fromhex(
    "05010906a101050719e029e715002501750195088102"   # 8 modifier bits
    "950175088101"                                    # reserved byte
    "95067508150026ff0005071900 29ff8100c0".replace(" ", ""))
TOUCH_DESC = bytes.fromhex(
    "050d0904a1010922a102"
    "0942150025017501950181029507810 3".replace(" ", "") +
    "05010930093115002 6ff7f751095028102c0c0".replace(" ", ""))

d = usb.core.find(idVendor=int(os.environ.get("VID", "18d1"), 16))  # VID=04e8 for Samsung etc.
assert d, "phone not found"
proto = struct.unpack('<H', bytes(d.ctrl_transfer(0xC0, 51, 0, 0, 2)))[0]
print("AOA protocol", proto)

def register(hid_id, desc):
    try: d.ctrl_transfer(0x40, 55, hid_id, 0, None)
    except usb.core.USBError: pass
    d.ctrl_transfer(0x40, 54, hid_id, len(desc), None)
    d.ctrl_transfer(0x40, 56, hid_id, 0, desc)

def send(hid_id, report): d.ctrl_transfer(0x40, 57, hid_id, 0, bytes(report))

def key(usage, mod=0):
    send(KBD, [mod, 0, usage, 0, 0, 0, 0, 0]); time.sleep(0.05)
    send(KBD, [0] * 8); time.sleep(0.12)

def touch(down, x, y):
    send(TOUCH, [1 if down else 0] + list(struct.pack('<HH', int(x * 32767), int(y * 32767))))

def swipe(x0, y0, x1, y1, ms=300, n=15):
    touch(True, x0, y0)
    for i in range(1, n + 1):
        time.sleep(ms / 1000 / n)
        touch(True, x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n)
    time.sleep(0.03); touch(False, x1, y1)

def char_usage(c):
    if c.isdigit(): return 0x27 if c == '0' else 0x1E + int(c) - 1, 0
    if c.isalpha(): return 0x04 + ord(c.lower()) - ord('a'), (0x02 if c.isupper() else 0)
    return {' ': (0x2C, 0), '_': (0x2C, 0), '-': (0x2D, 0), '.': (0x37, 0)}[c]

register(KBD, KBD_DESC); register(TOUCH, TOUCH_DESC)
time.sleep(1.5)  # let Android add the input devices
try:
    for step in sys.argv[1:]:
        name, *a = step.split(':')
        print("->", name if name != 'type' else 'type:' + '*' * len(a[0]))
        if name == 'wake': send(KBD, [0x02] + [0] * 7); time.sleep(0.05); send(KBD, [0] * 8)
        elif name == 'swipeup': swipe(0.5, 0.92, 0.5, 0.35)
        elif name == 'type':
            for c in a[0]: key(*char_usage(c))
        elif name == 'enter': key(0x28)
        elif name == 'tab': key(0x2B, 0x02 if a and a[0] == 'shift' else 0)
        elif name == 'esc': key(0x29)
        elif name == 'key': key(int(a[0], 16), int(a[1], 16) if len(a) > 1 else 0)
        elif name == 'tap': touch(True, float(a[0]), float(a[1])); time.sleep(0.08); touch(False, float(a[0]), float(a[1]))
        elif name == 'swipe': swipe(*map(float, a[:4]))
        elif name == 'hold':  # hold:secs:usage1:usage2...
            us = [int(u, 16) for u in a[1:]]
            send(KBD, [0, 0] + us + [0] * (6 - len(us))); time.sleep(float(a[0])); send(KBD, [0] * 8)
        elif name == 'sleep': time.sleep(float(a[0]))
        else: sys.exit(f"unknown step {step}")
        time.sleep(0.4)
finally:
    time.sleep(0.3)
    for i in (KBD, TOUCH):
        try: d.ctrl_transfer(0x40, 55, i, 0, None)
        except usb.core.USBError: pass
