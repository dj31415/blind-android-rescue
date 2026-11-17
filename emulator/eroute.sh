#!/bin/bash
# eroute.sh ROUTE... : on $ANDROID_SERIAL: unlock with $EPIN, then per route (route_s, route_c, ...):
# force-stop Settings, re-fake USB, RESET + route; report the resumed activity and the checked USB option.
cd "$(dirname "$0")"; . ./env.sh; . ../routes.sh
python3 -I emu.py $(unlock "$EPIN")
for r in "$@"; do
  adb shell am force-stop com.android.settings; ./efakeusb.sh >/dev/null 2>&1
  python3 -I emu.py $RESET $($r "$EPIN")
  adb shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1
  echo "$r: $(adb shell dumpsys activity activities | grep -m1 topResumedActivity | grep -o '[^ ]*/[^ ]*') $(adb shell cat /sdcard/ui.xml | python3 -I estate.py)"
done
