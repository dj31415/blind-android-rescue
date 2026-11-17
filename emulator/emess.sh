#!/bin/bash
# emess.sh N : put $ANDROID_SERIAL emulator into a messy start state (assumes unlocked)
cd "$(dirname "$0")"; . ./env.sh
case $1 in
  1) python3 -I emu.py key:0x0c:08 sleep:2.5 tab tab tab tab tab tab tab tab tab enter sleep:2 tab tab ;;   # Settings subpage
  2) adb shell am start -n 'com.android.settings/.Settings$DisplaySettingsActivity' >/dev/null; sleep 2; python3 -I emu.py tab tab tab tab tab ;;  # deep page, focus inside
  3) python3 -I emu.py key:0xf1 key:0xf1 key:0xf1 sleep:1 key:0xe3 sleep:2 type:hello ;;   # launcher all apps + search text
  4) python3 -I emu.py key:0x0c:08 sleep:2.5 tab tab tab tab tab tab tab tab tab tab tab tab tab tab sleep:0.5; adb shell input keyevent KEYCODE_SLEEP ;;  # Settings scrolled + screen off/locked
esac
sleep 1
