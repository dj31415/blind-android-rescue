#!/bin/bash
# etap.sh TEXT : tap the first UI node whose text/desc matches TEXT (setup helper, emulator only)
cd "$(dirname "$0")"; . ./env.sh
adb shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1
b=$(adb shell cat /sdcard/ui.xml | python3 -I -c '
import sys,re,xml.etree.ElementTree as ET
for n in ET.fromstring(sys.stdin.read()).iter("node"):
    if any(re.search(sys.argv[1], n.get(a) or "", re.I) for a in ("text","content-desc")):
        x1,y1,x2,y2=map(int,re.findall(r"\d+",n.get("bounds"))); print((x1+x2)//2,(y1+y2)//2); break' "$1")
[ -n "$b" ] && adb shell input tap $b && echo "tapped $1 at $b" || echo "no $1"
