# Install the firmware — model 2381 only

This folder contains the exact **ID2381 V302 F6PK** firmware used with this project's SignalRGB plugin, plus **stock ID2381 V302** for rollback.

**Only for MonsGeek FUN60 Ultra model 2381. Do not flash model 2307 or another keyboard.** The name “FUN60” alone is not enough. Flashing can reset settings or leave a keyboard unusable if interrupted or used on incompatible hardware. This experimental image was tested on one keyboard; typing and live lighting worked. Recovery from a completely unresponsive keyboard has not been tested.

Already using V302 F6PK with working per-key lighting? **Skip flashing** and follow the [main setup guide](../README.md).

## 1. Get ready

1. Download and extract the [whole project ZIP](https://github.com/sinsaintly/fun60-signalrgb-fix/archive/refs/heads/main.zip). Keep the files in this folder together.
2. Before closing MonsGeek, record your important remaps, actuation settings, and other preferences. These files do not include a backup of your settings or calibration.
3. Fully quit SignalRGB and MonsGeek from their tray menus. If the tool says `iot_manager_rs` is still running, close that MonsGeek background process in Task Manager too.
4. Connect **only the keyboard being flashed**, using a reliable wired USB connection. Disconnect other MonsGeek keyboards/receivers and keep the PC powered on throughout the flash.
5. Install [Python 3](https://www.python.org/downloads/windows/) if needed.

## 2. Open the firmware folder

Open this `firmware` folder in File Explorer. You should see `flash-2381.py` and both `.bin` files.

Click File Explorer's address bar, type **powershell**, and press **Enter**.

Install the USB library:

```powershell
py -3 -m pip install hidapi
```

## 3. Check your keyboard first — no flashing yet

```powershell
py -3 .\flash-2381.py
```

The tool checks the file checksum and queries the keyboard. It should show:

- `"model": 2381`
- `"version": "0403"` for V304 or `"version": "0203"` for V302 (the displayed bytes are little-endian)
- A `plan` line with `"armed": false`

If the marker is already `4636504b`, that spells **F6PK**. You normally do not need to flash again.

**If there is an error or the model is wrong, stop. Do not edit the checks or run Python with `-O`.** The tool accepts only the observed V302/V304 versions and model 2381. A successful check verifies these identifiers, not every possible hardware difference.

## 4. Flash V302 F6PK

Only after the previous check passes, run:

```powershell
py -3 .\flash-2381.py --arm
```

**Leave the keyboard connected and wait until the tool finishes.** It will restart the keyboard and check its identity again.

Success is a final line containing:

```text
"event": "verified", "model": 2381, "version": "0302", "marker": "4636504b"
```

Check that you can type, then return to [the main guide, step 2](../README.md#2-fully-close-both-apps) to install the plugin and MonsGeek detection fix. MonsGeek may keep searching until that app fix is applied.

## Want to return to stock firmware?

The included stock image is **V302**, not V304. It removes F6PK/live streaming. The original V304 image was not obtained, so this package cannot restore V304.

Close the apps again, then check the stock recovery plan:

```powershell
py -3 .\flash-2381.py --stock
```

If the check passes, restore stock V302:

```powershell
py -3 .\flash-2381.py --stock --arm
```

Success ends with `"event": "verified"`, version `0302`, and marker `00000000`. Disable/remove the F6PK SignalRGB plugin afterward. It will refuse to stream to stock firmware anyway. See [app/plugin rollback](../HELP.md#uninstall--rollback) to undo the desktop changes.

## If a flash fails

Keep the error text and local `flash-*-log.json`. Do not publish logs without checking them for personal paths. Do not repeatedly retry with different firmware.

If this **same keyboard was already positively identified as model 2381** and now appears only in its bootloader, the tool cannot read its normal model identity. The bootloader USB ID alone does not prove the model. For that specific recovery case, check the plan with:

```powershell
py -3 .\flash-2381.py --stock --recover-model-2381
```

Then, only for that previously verified keyboard, attempt stock recovery:

```powershell
py -3 .\flash-2381.py --stock --recover-model-2381 --arm
```

This is an explicit model-confirmation override for bootloader recovery, not an automatic compatibility check. Recovery on a completely unresponsive device is untested. If the bootloader is not detected, stop and seek model-specific recovery help.

## Files and verification

| File | Purpose | SHA-256 |
| --- | --- | --- |
| `ID2381-V302-F6PK.bin` | Exact experimental image flashed on the tested keyboard | `6766c13b834f74ec3b736f3578a405598f45c6cdee1bf595a7b9ca7b3175e555` |
| `stock-ID2381-V302.bin` | Vendor V302 base/recovery image | `c3204d50a60afc7a0f573638c440cd1762e78cd4c25462aa39a6927d0b5481f3` |

The flasher validates both hashes against `manifest.json`. Firmware images contain vendor code; they are not an official release of this project and no ownership of that vendor code is claimed. The base image was retrieved for device 2381, vendor firmware record 794, `fw_upgrade_file/2381_v302`. Flasher protocol reference: [dot-agi/ry5088-flasher](https://github.com/dot-agi/ry5088-flasher).

The published flasher adds model-recovery opt-in and app-process checks to the script used on the tested keyboard. These packaging checks were tested offline; the publication itself does not reflash a keyboard or establish multi-device compatibility.
