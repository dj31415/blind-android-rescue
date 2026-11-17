#!/bin/bash
# es.sh OUT.png STEPS... : run emu.py steps on $ANDROID_SERIAL, screenshot (downscaled) + focused node
out=$(realpath -m "$1"); shift; cd "$(dirname "$0")"; . ./env.sh
python3 -I emu.py "$@" sleep:1.2
adb exec-out screencap -p > "$out.full.png"
ffmpeg -loglevel error -y -i "$out.full.png" -vf scale=360:-1 "$out"; ./efocus.sh
