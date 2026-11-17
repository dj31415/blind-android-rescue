#!/bin/bash
# efocus.sh : print resumed activity and the focused UI node of $ANDROID_SERIAL emulator
cd "$(dirname "$0")"; . ./env.sh
adb shell dumpsys activity activities 2>/dev/null | grep -m1 -E 'topResumedActivity|mResumedActivity' | sed 's/^ *//'
adb shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1
adb shell cat /sdcard/ui.xml | python3 -I -c '
import sys, xml.etree.ElementTree as ET
r = ET.fromstring(sys.stdin.read())
f = [n for n in r.iter("node") if n.get("focused") == "true"]
for n in f[-1:]:
    txt = n.get("text") or n.get("content-desc") or ""
    sub = [c.get("text") for c in n.iter("node") if c.get("text")]
    print("FOCUS:", n.get("class").split(".")[-1], n.get("resource-id"), repr(txt), sub[:3], n.get("bounds"))
if not f: print("FOCUS: none")
'
