#!/bin/bash
# look.sh OUT.png STEPS... : run AOA steps, press Print (screenshot on the phone), fetch it over MTP, downscale.
# Needs File transfer to be on already.
out=$(realpath -m "$1"); shift; cd "$(dirname "$0")"
uv run --script aoa.py "$@" sleep:1 key:0x46 sleep:2.5 >/dev/null 2>&1
uv run --script shot.py "$out.full.png" >/dev/null 2>&1 && ffmpeg -loglevel error -y -i "$out.full.png" -vf scale=450:-1 "$out"
echo "$out"
