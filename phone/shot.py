# /// script
# dependencies = ["pyusb"]
# ///
"""Fetch the newest file from Pictures/Screenshots over MTP: shot.py OUTFILE"""
import os
import sys, struct, usb.core, usb.util
d = usb.core.find(idVendor=int(os.environ.get("VID", "18d1"), 16))  # VID=04e8 for Samsung etc.
intf = d.get_active_configuration()[(0, 0)]
if d.is_kernel_driver_active(0): d.detach_kernel_driver(0)
usb.util.claim_interface(d, 0)
eps = [e for e in intf if e.bmAttributes == 2]
ep_out = next(e for e in eps if usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
ep_in = next(e for e in eps if usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
tid = 0
def op(code, *params):
    global tid; tid += 1
    ep_out.write(struct.pack('<IHHI', 12 + 4 * len(params), 1, code, tid) + b''.join(struct.pack('<I', p) for p in params))
    data = b''
    while True:
        r = bytes(ep_in.read(1 << 20, timeout=20000))
        length, typ, c, _ = struct.unpack('<IHHI', r[:12])
        while len(r) < length: r += bytes(ep_in.read(1 << 20, timeout=20000))
        if typ == 2: data = r[12:length]
        elif typ == 3: return c, data
def handles(storage, parent):
    c, data = op(0x1007, storage, 0, parent)
    n = struct.unpack('<I', data[:4])[0]
    return struct.unpack(f'<{n}I', data[4:4 + 4 * n])
def name(h):
    _, data = op(0x1008, h)
    n = data[52]
    return data[53:53 + 2 * n].decode('utf-16le').rstrip('\0')
def child(storage, parent, wanted):
    return next(h for h in handles(storage, parent) if name(h) == wanted)
try:
    op(0x1002, 1)
    _, data = op(0x1004)
    storage = struct.unpack('<I', data[4:8])[0]
    shots = child(storage, child(storage, 0xFFFFFFFF, 'Pictures'), 'Screenshots')
    newest = max(handles(storage, shots))
    print(name(newest))
    _, img = op(0x1009, newest)
    open(sys.argv[1], 'wb').write(img)
    op(0x1003)
finally:
    usb.util.release_interface(d, 0)
