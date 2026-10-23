# MonsGeek FUN60 Ultra: SignalRGB / MonsGeek Driver handoff fix

Use MonsGeek Driver to edit your keyboard settings without manually disabling the keyboard in SignalRGB. SignalRGB pauses this keyboard while MonsGeek runs and can resume live per-key lighting after MonsGeek fully exits.

This project also fixes MonsGeek's **“Searching for device…”** screen for the specific experimental **ID2381 V302 F6PK** firmware and reduces two handoff delays.

**This is an experimental compatibility fix for an already-patched keyboard. It does not install firmware or add live per-key support to a stock keyboard.** It is not an official MonsGeek, SignalRGB, or SRGBmods release.

## Compatibility

| Item | Tested configuration |
| --- | --- |
| Keyboard | MonsGeek FUN60 Ultra, model ID **2381** |
| USB vendor/product | **3151:502D** (hexadecimal) |
| Lighting interface | Interface 2; usage page 65535; usage 2 |
| Firmware | Model-2381 V302 with the custom **F6PK RAM-streaming patch** |
| SignalRGB | Windows, version 2.5.80 |
| MonsGeek | Driver v4; reported driver V500.3.4_IOTV0.1.8 |
| Tested app bundle | `resources/app/dist/js/index.f9e8588e.js` |

Model **2307**, other FUN60 variants, stock V302/V304, and other firmware are not supported by this lighting plugin. Matching the product name or USB ID alone is not enough. The plugin verifies model 2381, version 0x0302, and the F6PK marker before sending RGB frames.

The supplied files do not flash, reset, or calibrate your keyboard. If you have stock firmware, stop here: this package is not a complete firmware-conversion guide. Firmware images and a flasher are deliberately not included.

## What is included

- `MonsGeek_FUN60_Ultra_Manual.js`: the live per-key plugin, 60% keycap-shaped layout, and automatic process conflict handling.
- `patch_monsgeek.py`: a local patcher for the tested MonsGeek app bundle, with dry-run checks and automatic backup.
- `tests/`: offline checks for the plugin and patcher.
- `TECHNICAL.md`: protocol, compatibility fix, timing, and validation details.

No vendor app bundle, firmware binary, personal device settings, USB serial number, or legacy sharing token is distributed here.

## Installation

### 1. Check prerequisites and close the apps

1. Confirm you already have the specific F6PK firmware listed above. A stock keyboard will not work with this plugin.
2. Fully quit SignalRGB and MonsGeek from their tray menus. Closing a window may only minimize it.
3. Download this repository using **Code → Download ZIP**, then extract it.
4. Install Python 3 from [python.org](https://www.python.org/downloads/windows/) if it is not already available. The patcher uses only Python's standard library.

### 2. Install the SignalRGB plugin

1. Open your Windows **Documents** folder, then `WhirlwindFX\Plugins`.
2. Back up your existing FUN60 plugin **outside** the Plugins folder. Do not leave another `.js` copy in that folder; two plugins can compete for the same keyboard.
3. Copy this repository's `MonsGeek_FUN60_Ultra_Manual.js` into the Plugins folder. Replace the old file of that name if present.

The usual path is `%USERPROFILE%\Documents\WhirlwindFX\Plugins`. If Windows redirects Documents to OneDrive or another location, use the actual Documents folder. Preserve the existing filename when replacing a working installation to avoid unnecessary changes to its device association.

### 3. Patch MonsGeek detection

Open PowerShell in the extracted repository folder. First run a read-only compatibility check:

```powershell
py -3 .\patch_monsgeek.py
```

It should say **“Compatible bundle. Dry run passed”** or **“Already patched.”** If compatible, apply the patch:

```powershell
py -3 .\patch_monsgeek.py --apply
```

If your Python installation uses `python` instead of `py -3`, substitute that command.

The default app location is:

```text
%LOCALAPPDATA%\Programs\MonsGeek Driver v4\resources\app\dist\js\index.f9e8588e.js
```

For a different installation location, pass its actual bundle path:

```powershell
py -3 .\patch_monsgeek.py --bundle "D:\Apps\MonsGeek Driver v4\resources\app\dist\js\index.f9e8588e.js"
py -3 .\patch_monsgeek.py --bundle "D:\Apps\MonsGeek Driver v4\resources\app\dist\js\index.f9e8588e.js" --apply
```

The script refuses unsupported source patterns rather than guessing. Do not rename another app version's bundle to bypass a failure. Keep the backup path printed after applying the patch.

### 4. Start and verify

1. Start SignalRGB with MonsGeek fully closed. Leave the FUN60 device enabled.
2. Confirm the keyboard follows your current SignalRGB effect. The plugin console should report **“FUN60 F6PK ready: 61 keys…”**.
3. Open MonsGeek. SignalRGB should automatically pause the keyboard, and MonsGeek should display **FUN60 Ultra** instead of searching indefinitely.
4. Use **Retrieve Current Setting** to read the keyboard's configuration before editing it. Confirm the settings make sense before saving changes.
5. Fully exit MonsGeek, including its tray process. SignalRGB should resume the keyboard automatically.

Other SignalRGB devices are not disabled by this plugin's conflict rule. This is automatic handoff, not simultaneous control: live lighting pauses while MonsGeek is running.

## Troubleshooting

### MonsGeek is still searching

- Verify the exact model and F6PK firmware prerequisite. This patch does not repair arbitrary firmware incompatibility.
- Fully quit both apps and reopen them after installation; an already-running MonsGeek process retains its old code.
- Confirm the patcher reports “Already patched” for the bundle actually used by your installed app.
- Check whether a MonsGeek update replaced the bundle. A new app version needs a fresh compatibility check.
- Temporarily quit SignalRGB completely as a diagnostic. If MonsGeek then detects the keyboard, check for duplicate FUN60 plugins and whether the driver process is named `MonsGeek Driver v4.exe`.
- If the patcher reports **“Legacy UDP sharing patch detected”**, restore the backup made before that earlier sharing experiment, then run this patcher. A paused SignalRGB plugin cannot acknowledge the old UDP handshake. Do not install `fun60-sharing.cjs` with this package.

### Lighting does not resume

The MonsGeek process may still be running in the tray. Use its **Exit/Quit** command; Task Manager should no longer show `MonsGeek Driver v4.exe`. Keep the keyboard enabled in SignalRGB. If necessary, restart SignalRGB once after replacing the plugin.

### The plugin reports a missing F6PK marker

It has deliberately stopped streaming. This usually means the required firmware is absent or was replaced by a vendor firmware update. Do not remove the model/version/marker checks. Stock per-key save commands are unsuitable for continuous streaming because they can write flash.

### The layout looks like many dots per key

Those are display-only pixels forming keycap shapes, including the wide spacebar and modifiers. The plugin samples only 61 physical key centers and sends only those keys' colors.

### Detection is not instant

The changes reduce MonsGeek's FUN60 identity retry interval from 500 ms to 100 ms and the plugin's first mode-ready wait from 600 ms to 150 ms. They do not eliminate app startup, driver initialization, or SignalRGB's own process polling. A faster end-to-end startup time has not been benchmarked. A delayed keyboard can still use the plugin's readiness retries.

## Uninstall / rollback

1. Fully quit MonsGeek and SignalRGB.
2. Remove this plugin from the Plugins folder and restore your previous plugin backup, if any.
3. Restore the exact MonsGeek bundle backup printed by the patcher, replacing the same installed bundle. For example, in PowerShell:

```powershell
Copy-Item -LiteralPath "FULL_PATH_TO_THE_PRINTED_BACKUP" -Destination "FULL_PATH_TO_THE_ORIGINAL_BUNDLE" -Force
```

4. Reopen the apps. Reinstalling the official MonsGeek app also replaces modified app files, but removes the F6PK recognition fix.

Rollback here only affects the plugin and desktop app. It does **not** restore stock keyboard firmware. With F6PK still installed, an unpatched MonsGeek app may return to “Searching for device…”.

## Validation and limitations

One model-2381 keyboard was tested. Its owner confirmed typing and live per-key lighting. MonsGeek detection was observed after installing the compatibility fix, including after the retry change. Offline tests check packet layout, model/version/marker rejection, key layout, shutdown restoration, and patcher idempotence/refusal behavior.

All hardware variants, all MonsGeek functions, long-term reliability, and measured startup improvements have not been verified. App updates can overwrite this patch. See [TECHNICAL.md](TECHNICAL.md) for details.

## Reporting a problem

Open an issue with your model ID, firmware label, SignalRGB/MonsGeek versions, which step failed, and the patcher's error text. Do not upload full logs or device configuration dumps containing personal paths, account information, or serial numbers. Mention whether MonsGeek works with SignalRGB fully quit.

## Related projects

- [SignalRGB](https://signalrgb.com/)
- [MonsGeek](https://www.monsgeek.com/)
- [SRGBmods QMK plugins](https://github.com/SRGBmods/qmk-plugins) — a separate project; this is not a QMK plugin or a general MonsGeek QMK conversion.
