# /// script
# dependencies = ["pyusb"]
# ///
"""Print MTP GetDeviceInfo strings (works even in 'No data transfer')."""
import os
import usb.core, usb.util, struct
d = usb.core.find(idVendor=int(os.environ.get("VID", "18d1"), 16))  # VID=04e8 for Samsung etc.
intf = d.get_active_configuration()[(0,0)]
if d.is_kernel_driver_active(0): d.detach_kernel_driver(0)
usb.util.claim_interface(d, 0)
eps = [e for e in intf if e.bmAttributes == 2]
ep_out = next(e for e in eps if usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
ep_in = next(e for e in eps if usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
ep_out.write(struct.pack('<IHHI', 12, 1, 0x1001, 0))
data = b''
while True:
    r = bytes(ep_in.read(65536, timeout=5000))
    length, typ, c, _ = struct.unpack('<IHHI', r[:12])
    while len(r) < length: r += bytes(ep_in.read(65536, timeout=5000))
    if typ == 2: data = r[12:length]
    elif typ == 3: break
p = 8  # std version(2) vendor ext id(4) version(2)
def s():
    global p
    n = data[p]; v = data[p+1:p+1+2*n].decode('utf-16le').rstrip('\0'); p += 1 + 2*n; return v
def arr(sz):
    global p
    n = struct.unpack('<I', data[p:p+4])[0]; p += 4 + n*sz
print("ext:", s()); p += 2
for _ in range(5): arr(2)
print("manufacturer:", s()); print("model:", s()); print("device version:", s()); print("serial:", s())
usb.util.release_interface(d, 0)
