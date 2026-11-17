#!/bin/bash
# eboot.sh AVD : boot one headless emulator on port 5554 (stop others first), root it, add USB features,
# fake a PC connection, set PIN $EPIN, keep the screen awake. EMEM=3072 for more RAM.
cd "$(dirname "$0")"; . ./env.sh; export ANDROID_SERIAL=emulator-5554
nohup "$SDK/emulator/emulator" -avd "$1" -port 5554 -no-window -no-audio -no-boot-anim -gpu swiftshader_indirect \
  -no-snapshot-save -memory "${EMEM:-2048}" > "${TMPDIR:-/tmp}/eboot.log" 2>&1 &
adb wait-for-device; until [ "$(adb shell getprop sys.boot_completed 2>/dev/null)" = 1 ]; do sleep 3; done
adb root >/dev/null; sleep 3; adb wait-for-device; until [ "$(adb shell getprop sys.boot_completed 2>/dev/null)" = 1 ]; do sleep 2; done
adb shell locksettings set-pin "$EPIN" >/dev/null 2>&1
./efeature.sh >/dev/null
adb shell 'svc power stayon true; settings put system screen_off_timeout 1800000'
echo "booted $1: Android $(adb shell getprop ro.build.version.release), PIN $EPIN"
