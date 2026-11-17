#!/bin/bash
# rescue.sh PIN [ROUTE...] : blind, on the real phone via AOA2 HID. Unlock once, then per route: RESET + route,
# check whether the MTP storage unlocked. Default routes: route_s (Android 16) then route_c (Android 14/15).
# Stops at the first success. Each route that runs on the wrong version clicks around in Settings.
cd "$(dirname "$0")"; . ../routes.sh; pin=${1:?usage: rescue.sh PIN [route_s|route_c|route_a17 ...]}; shift
routes=("$@"); [ $# -eq 0 ] && routes=(route_s route_c)
storage() { pkill -x kiod6 2>/dev/null; sleep 1; uv run --script ptpcheck.py 2>&1 | grep -o 'GetStorageIDs.*'; }
unlocked() { echo "$1" | grep -qvE ' (00000000)?$'; }
s=$(storage); if unlocked "$s"; then echo "already File transfer: $s"; exit 0; fi
uv run --script aoa.py $(unlock "$pin") 2>&1 | grep -v -- '->'
for r in "${routes[@]}"; do
  echo "== $r"
  uv run --script aoa.py $RESET $($r "$pin") 2>&1 | grep -v -- '->' | grep -v 'No such device'
  sleep 5; s=$(storage); echo "$s"
  if unlocked "$s"; then echo "SUCCESS via $r"; exit 0; fi
done
echo "no route worked"; exit 1
