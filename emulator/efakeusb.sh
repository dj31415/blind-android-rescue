#!/bin/bash
# efakeusb.sh : make $ANDROID_SERIAL (rooted) look connected to a PC in "No data transfer" mode:
# a simulated type-C port in device role plus a sticky USB_STATE broadcast (connected, data locked).
cd "$(dirname "$0")"; . ./env.sh
[ -f sticky/classes.dex ] || sticky/build.sh
adb push sticky/classes.dex /data/local/tmp/sticky.dex >/dev/null
adb shell 'dumpsys usb remove-port p1 >/dev/null 2>&1; dumpsys usb add-port p1 ufp >/dev/null; dumpsys usb connect-port p1 ufp sink device >/dev/null'
adb shell svc usb setFunctions >/dev/null 2>&1; sleep 1
adb shell CLASSPATH=/data/local/tmp/sticky.dex app_process / Sticky true false
