# /// script
# dependencies = ["pyusb"]
# ///
import os
import usb.core, usb.util, struct
d = usb.core.find(idVendor=int(os.environ.get("VID", "18d1"), 16))  # VID=04e8 for Samsung etc.
intf = d.get_active_configuration()[(0,0)]
if d.is_kernel_driver_active(0): d.detach_kernel_driver(0)
usb.util.claim_interface(d, 0)
ep_out = [e for e in intf if usb.util.endpoint_direction(e.bEndpointAddress)==usb.util.ENDPOINT_OUT and e.bmAttributes==2][0]
ep_in  = [e for e in intf if usb.util.endpoint_direction(e.bEndpointAddress)==usb.util.ENDPOINT_IN and e.bmAttributes==2][0]
tid=0
def op(code,*params):
    global tid; tid+=1
    pkt=struct.pack('<IHHI',12+4*len(params),1,code,tid)+b''.join(struct.pack('<I',p) for p in params)
    ep_out.write(pkt)
    data=b''
    while True:
        r=bytes(ep_in.read(65536,timeout=5000))
        length,typ,c,t=struct.unpack('<IHHI',r[:12])
        while len(r)<length: r+=bytes(ep_in.read(65536,timeout=5000))
        if typ==2: data=r[12:length]
        elif typ==3: return c,data
print("OpenSession", hex(op(0x1002,1)[0]))
c,data=op(0x1004)
print("GetStorageIDs", hex(c), data.hex())
op(0x1003)
usb.util.release_interface(d,0)
