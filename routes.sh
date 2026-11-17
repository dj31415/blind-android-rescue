# Step lists shared by phone/aoa.py (real phone) and emulator/emu.py (rehearsal). Source this file, then e.g.
#   uv run --script phone/aoa.py $(unlock PIN) $RESET $(route_c PIN)
# Every step is "wake", "tab", "enter", "type:<text>", "key:<hid>[:<modifier>]" or "sleep:<s>"; see README.

B="key:0xf1 sleep:0.6"   # Back
D="key:0x2a sleep:0.5"   # Backspace = Android DEL (also dismisses a task in Overview)
T="tab sleep:0.6"

# Shift wakes the screen. Menu (0x76) opens the PIN pad whatever has lock-screen focus; Space would "click"
# a focused element instead (e.g. the date -> Calendar). Wait, clear the field, then type: a digit typed while
# the pad animates in gets lost, and a wrong PIN counts toward lockout.
unlock() { echo wake sleep:2 key:0x76 sleep:2.5 $D $D $D $D $D $D sleep:0.5 "type:$1" sleep:0.8 enter sleep:3; }

# Back out of everything, open Overview (Meta+Tab), dismiss every task (Del) -> next Meta+I opens a fresh Settings.
RESET="$B $B $B $B $B $B key:0x2b:08 sleep:2 $D $D $D $D $D $D $D $D $D $D sleep:1.5"

# Android 16 asks "Verify it's you" (PIN) after choosing File transfer. Where it doesn't, digits + Enter are harmless.
confirm() { echo sleep:3 "type:$1" enter sleep:5; }

# Android 16 (Pixel, QPR2): Meta+I, Tab = search bar, query, first hit = USB Preferences, focus starts on
# "Navigate up", Tab x3 = File transfer. The space is Shift+Space: "usb" alone ranks USB tethering first, and on
# A14/15 (no search box focus) a plain Space page-scrolls the list while Shift+Space is a no-op.
route_s() { echo "key:0x0c:08 sleep:3 $T enter sleep:2.5 type:usb key:0x2c:02 type:preferences sleep:3 key:0x51 sleep:0.6 enter sleep:3 $T $T $T enter $(confirm $1)"; }

# Android 14/15 (Pixel): search bar is not keyboard-reachable. Meta+I, Tab x3 (list, Network & internet,
# Connected devices), Enter, Enter ("USB" is first and pre-focused), Tab x2 (Connected device, This device,
# File transfer), Enter. Arrow keys only scroll the whole list on the Settings home page.
route_c() { echo "key:0x0c:08 sleep:3 $T $T $T enter sleep:2.5 enter sleep:3 $T $T enter $(confirm $1)"; }

# Android 17 (Pixel 8 Pro), observed once, not emulator-trained: Down then Up x3 reaches the search bar.
# The File transfer switch asked for a fingerprint there, confirmed by hand.
route_a17() { echo "key:0x29 sleep:0.6 key:0x0c:08 sleep:3 key:0x51 sleep:0.5 key:0x52 sleep:0.5 key:0x52 sleep:0.5 key:0x52 sleep:0.8 enter sleep:2 type:usb_preferences sleep:3 key:0x51 sleep:0.8 enter sleep:3 key:0x51 sleep:0.5 key:0x51 sleep:0.5 key:0x51 sleep:0.8 enter $(confirm $1)"; }
