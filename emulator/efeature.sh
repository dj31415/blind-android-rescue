#!/bin/bash
# efeature.sh : declare android.hardware.usb.accessory/host on $ANDROID_SERIAL (rooted) so Settings shows "USB",
# via a bind-mounted permissions dir + framework restart (not persistent), then fake the PC connection.
cd "$(dirname "$0")"; . ./env.sh
adb shell 'mkdir -p /data/local/tmp/perm && cp -a /system/etc/permissions/. /data/local/tmp/perm/ &&
  echo "<permissions><feature name=\"android.hardware.usb.accessory\" /><feature name=\"android.hardware.usb.host\" /></permissions>" > /data/local/tmp/perm/usbfake.xml
  chmod 644 /data/local/tmp/perm/*; chcon -R u:object_r:system_file:s0 /data/local/tmp/perm
  mount -o bind /data/local/tmp/perm /system/etc/permissions; stop; start'
sleep 20; until [ "$(adb shell getprop sys.boot_completed)" = 1 ] && adb shell pm list features 2>/dev/null | grep -q usb.accessory; do sleep 3; done; sleep 15
./efakeusb.sh | tail -1 | cut -c1-40
