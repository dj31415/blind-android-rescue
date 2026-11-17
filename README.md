# blind-android-rescue

Get your files off an Android phone whose screen is dead, without opening it, without ADB, and without
seeing anything.

The laptop pretends to be a USB keyboard (Android Open Accessory 2 HID) and types a fixed key sequence: it
unlocks the phone, opens Settings, goes to USB Preferences and picks **File transfer**. After that the
phone's storage is a normal MTP device and you copy your photos.

Built to rescue the photos from a Pixel 7 Pro with a black display, touch of unknown state, USB debugging
off, and nothing in the cloud. It worked on the first real run.

## When this can help

All of these must be true:

- The phone still boots (it shows up in `lsusb` when plugged in, vibrates, rings).
- The USB-C port works.
- You know the PIN/password. Nothing here bypasses the lock screen.
- It's Android. iPhones don't support AOA.
- There is a route for its Settings layout. Trained so far: **Pixel on Android 14, 15, 16**, plus one
  untrained Android 17 observation. Other makers (Samsung One UI, Xiaomi, …) need their own routes; see
  *Training a new route*.

If USB debugging was already on, you don't need this: use `adb pull` or `scrcpy`.

## Risks, read before running on a real phone

- **Wrong PIN attempts count.** Several failures lock the phone for increasing periods. Run one route at a
  time and check the result before trying the next.
- **Keys go wherever focus is.** If the phone is in an unexpected state or on an untrained version, Tab
  and Enter click something you can't see. The trained routes include a reset first, but a wrong route
  can still open or toggle things in Settings.
- **Fingerprint prompts.** Newer Android versions ask "Verify it's you" before switching to File
  transfer. With a fingerprint enrolled, that prompt may default to the fingerprint sensor, which on
  under-display sensors needs a working screen. There is no trained keyboard path to "Use PIN" yet.
- Use at your own risk; see LICENSE.

## Quick start

Needs Linux, [uv](https://docs.astral.sh/uv/) (scripts carry their own `pyusb` dependency) and USB
access to the phone (root, or a udev rule for its vendor ID).

```bash
cd phone
pkill -x kiod6                      # KDE only: kiod6 grabs the MTP interface
uv run --script ptpcheck.py         # "GetStorageIDs 0x2001 00000000" = locked (No data transfer)

. ../routes.sh
uv run --script aoa.py $(unlock 1234) $RESET $(route_c 1234)    # Android 14/15
uv run --script aoa.py $(unlock 1234) $RESET $(route_s 1234)    # Android 16
sleep 5; uv run --script ptpcheck.py                            # anything other than 00000000 = unlocked
```

Or `./rescue.sh 1234` to try `route_s`, then `route_c`, checking after each. When the mode switches, the phone
re-enumerates on USB; `aoa.py` then ends with `No such device`, and that is the success case.

Then copy, for example with [go-mtpfs](https://github.com/hanwen/go-mtpfs):

```bash
mkdir -p ~/phone && go-mtpfs ~/phone &
rsync -rt ~/phone/"Internal shared storage"/{DCIM,Pictures} ~/rescued/
rsync -rt ~/phone/"Internal shared storage"/Android/media/com.whatsapp ~/rescued/   # messenger media
fusermount -u ~/phone
```

File transfer stays on until you unplug the cable.

Not a Google phone? Set `VID` to its USB vendor ID, e.g. `VID=04e8` for Samsung (see `lsusb`).

## How it works

Android Open Accessory 2 lets a USB host register HID devices on the phone with control requests
(`ACCESSORY_REGISTER_HID`, `ACCESSORY_SET_HID_REPORT_DESC`, `ACCESSORY_SEND_HID_EVENT`). This needs no app,
no ADB and no pairing, and it works on the lock screen. `phone/aoa.py` registers a standard USB keyboard and
plays steps:

| Step | Meaning |
|---|---|
| `wake` | Shift press |
| `key:<hid>[:<mod>]` | HID usage, optional modifier byte: `01` Ctrl, `02` Shift, `04` Alt, `08` Meta |
| `type:<text>` | Letters, digits, space, `-`, `.`; `_` is typed as a space |
| `enter`, `tab`, `tab:shift`, `esc` | Shortcuts |
| `hold:<secs>:<hid>…` | Hold keys |
| `sleep:<secs>` | Pause |

Useful usages: `0x28` Enter, `0x2a` Backspace (Android DEL), `0x2b` Tab, `0x2c` Space, `0x46` Print
(screenshot), `0x51` Down, `0x52` Up, `0x76` Menu, `0xf1` Back, `0x0c:08` Meta+I (Settings), `0x2b:08`
Meta+Tab (Overview).

The success signal is MTP: in "No data transfer" the phone still answers PTP, but `GetStorageIDs` returns
an empty list. The trick is similar to [scrcpy's OTG mode](https://github.com/Genymobile/scrcpy/blob/master/doc/otg.md),
which also uses AOA HID without ADB. The difference is that you don't need to steer a mouse blindly: the routes
are fixed key sequences, rehearsed per Android version.

## The routes (`routes.sh`)

| | Android 14 | Android 15 | Android 16 (QPR2) |
|---|---|---|---|
| First Tab in Settings | whole list | whole list | search bar |
| Search reachable by keyboard | no | no | yes |
| Way to USB Preferences | Tab×3 → Connected devices → USB | same | search "usb⇧␣preferences" |
| Focus on arrival | "Connected device" | "Connected device" | "Navigate up" |
| Tabs to File transfer | 2 | 2 | 3 |
| "Verify it's you" | no | no | PIN |
| Route | `route_c` | `route_c` | `route_s` |

Every run starts with `unlock` and `$RESET`:

- **unlock**: Shift → Menu → Backspace×6 → PIN → Enter. Menu opens the PIN pad whatever the lock screen has
  focused. Space "clicks" the focused element instead, and leftover focus (e.g. on the date, which
  opens Calendar) survives screen-off. The wait and Backspaces stop a digit getting lost while the pad
  animates in.
- **RESET**: Back×6 → Meta+Tab (Overview) → Del×10, each Del dismissing one task. The next Meta+I opens
  a fresh Settings with no focus and no remembered subpage.

Traps found during training, so you don't repeat them:

- On Android 14/15, Up or Shift+Tab from the Settings list lands on the account avatar (Google "Your info"),
  never the search bar.
- Arrow keys on the Settings home page scroll the whole list as one block. Only Tab moves between entries.
- Searching "usb" alone ranks "USB tethering" first.
- A plain Space on the Android 14/15 home list page-scrolls it, and the following keys then wander off
  (System → Navigation mode → gesture tutorial, which blocks the reset). Shift+Space avoids that.
- The Android version can't be read over USB (MTP reports device version `1.0`), so you try one route,
  check, then the next. `route_s` on Android 14/15 ends harmlessly in Apps; `route_c` on Android 16 opens
  Google settings.

## Training a new route (emulator)

Routes were found and tested on Android emulators, where you can read which element has keyboard focus
after every key. Emulators have no USB port, so Settings normally never shows a USB entry. `emulator/` fakes
both the hardware and the PC:

1. `efeature.sh` declares `android.hardware.usb.accessory`/`usb.host` by bind-mounting a permissions XML
   over `/system/etc/permissions` and restarting the framework (root image needed, not persistent).
2. `efakeusb.sh` simulates a type-C port in device role (`dumpsys usb add-port/connect-port`) and sends a
   sticky `USB_STATE` broadcast (connected, data locked). `am broadcast` can't send sticky broadcasts, so
   `sticky/Sticky.java` does it through the hidden `IActivityManager` API via `app_process`. It's built by
   `sticky/build.sh`, which needs a JDK and the SDK's `d8`.

Setup (root-capable `google_apis` images, Pixel profile, hardware keyboard):

```bash
A=$HOME/Android/Sdk/cmdline-tools/latest/bin
$A/sdkmanager "system-images;android-35;google_apis;x86_64"     # newer SDKs: $A/android sdk install system-images/android-35/google_apis/x86_64
echo no | $A/avdmanager create avd -n p7r_35 -k "system-images;android-35;google_apis;x86_64" -d pixel_7_pro
sed -i 's/^hw.keyboard=.*/hw.keyboard=yes/' ~/.android/avd/p7r_35.avd/config.ini
emulator/eboot.sh p7r_35            # boots on 5554, roots, fakes USB, sets PIN $EPIN (default 1234)
```

Run one emulator at a time; three at once can exhaust 30 GB of RAM. The Android 16 image crashed on
`KEYCODE_SLEEP`.

Tools:

| Script | Purpose |
|---|---|
| `emu.py STEPS…` | Same steps as `aoa.py`, sent via `adb shell input keyboard` |
| `efocus.sh` | Resumed activity and the focused UI node, the main training tool |
| `es.sh OUT STEPS…` / `elook.sh OUT STEPS…` | Steps + screenshot + focus. `elook` captures at emulator level, so it also shows secure windows like PIN prompts. |
| `emess.sh N` | Messy start states: 1 Settings subpage, 2 deep page with focus, 3 launcher with search text, 4 Settings scrolled + screen off |
| `eroute.sh route…` | Unlock, then per route: reset Settings and USB, run it, print the checked USB option |
| `etap.sh REGEX` | Tap a node by text (setup only) |

Training loop: put the emulator in a messy state, run `eroute.sh route_x`, read the result, fix
`routes.sh`, and repeat on every version you support. A route for one version must also not do damage on the
others, because you won't know which version the broken phone runs.

## Other phone tools

| Script | Purpose |
|---|---|
| `ptpcheck.py` | PTP OpenSession + GetStorageIDs |
| `devinfo.py` | MTP DeviceInfo (manufacturer, model, serial); works in "No data transfer" too |
| `shot.py OUT` / `look.sh OUT STEPS…` | Once File transfer is on, press Print on the phone and fetch the newest screenshot: now you can see the screen |
| `mtpreset.py` | Drain the bulk endpoint and send a PTP Device Reset when MTP stops answering |

## License

MIT
