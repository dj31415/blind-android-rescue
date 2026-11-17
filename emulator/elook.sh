#!/bin/bash
# elook.sh OUT.png STEPS... : like es.sh, but captures at emulator level (adb emu screenrecord screenshot),
# which also shows FLAG_SECURE windows such as PIN prompts
out=$(realpath -m "$1"); shift; cd "$(dirname "$0")"; . ./env.sh
python3 -I emu.py "$@" sleep:1.5
d=$(mktemp -d); adb emu screenrecord screenshot "$d" >/dev/null; sleep 1
ffmpeg -loglevel error -y -i "$d"/*.png -vf scale=400:-1 "$out"; rm -rf "$d"; echo "$out"
