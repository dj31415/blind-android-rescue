# /// script
# dependencies = ["pyusb"]
# ///
"""Unstick the phone's MTP responder: drain bulk-in, PTP class Device Reset, then get device status."""
import os
import usb.core, usb.util
d = usb.core.find(idVendor=int(os.environ.get("VID", "18d1"), 16))  # VID=04e8 for Samsung etc.
intf = d.get_active_configuration()[(0, 0)]
if d.is_kernel_driver_active(0): d.detach_kernel_driver(0)
usb.util.claim_interface(d, 0)
ep_in = next(e for e in intf if e.bmAttributes == 2 and usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
for _ in range(5):
    try: print("drained", len(ep_in.read(1 << 20, timeout=300)))
    except usb.core.USBError: break
try: d.ctrl_transfer(0x21, 0x66, 0, 0, None); print("device reset ok")
except usb.core.USBError as e: print("device reset:", e)
try: print("status", bytes(d.ctrl_transfer(0xA1, 0x67, 0, 0, 64)).hex())
except usb.core.USBError as e: print("status:", e)
usb.util.release_interface(d, 0)
