# FUN60 Ultra — easy setup

Fix MonsGeek getting stuck on **“Searching for device…”** and switch automatically between MonsGeek settings and SignalRGB lighting.

> **Check this first:** You need a FUN60 Ultra **model 2381** that already has the custom **V302 F6PK firmware**. If you are still on stock V302/V304, use the [firmware setup guide](firmware/README.md) first. It includes the exact flashed image and stock V302 recovery. Do not use it on model 2307 or an unidentified keyboard.

## 1. Download and unzip

[**Download the fix (ZIP)**](https://github.com/sinsaintly/fun60-signalrgb-fix/archive/refs/heads/main.zip)

Right-click the downloaded ZIP → **Extract All** → **Extract**. Open the extracted folder until you can see `patch_monsgeek.py`.

## 2. Fully close both apps

Near the Windows clock, click the **^** arrow. Right-click **SignalRGB** and choose **Exit/Quit**. Do the same for **MonsGeek**.

**Clicking the X on the window may leave the app running.**

## 3. Copy the plugin

1. Open **File Explorer → Documents → WhirlwindFX → Plugins**.
2. If you already have a FUN60 plugin there, move it to a backup folder outside `Plugins`.
3. From the extracted download, copy **`MonsGeek_FUN60_Ultra_Manual.js`** into `Plugins`.

Keep only **one FUN60 plugin** in that folder. If your Documents folder is in OneDrive, use that Documents folder instead.

## 4. Apply the MonsGeek fix

You need **Python 3**. If you don't have it, install it from [python.org](https://www.python.org/downloads/windows/), then continue.

1. Return to the extracted download folder where you can see `patch_monsgeek.py`.
2. Click File Explorer's **address bar** at the top.
3. Type **`powershell`** and press **Enter**.
4. Copy this command, paste it into the window, and press **Enter**:

```powershell
py -3 .\patch_monsgeek.py --apply
```

**Success looks like:** `Patch installed` or `Already patched`.

The installer checks compatibility before changing anything and makes a backup automatically. Keep the backup location it prints. If you get an error, use the help below instead of changing the script.

## 5. Open your apps

1. Open **SignalRGB**. Leave the FUN60 enabled and check that its lights follow your effect.
2. Open **MonsGeek**. It should show **FUN60 Ultra**. Click **Retrieve Current Setting** before editing your keyboard settings.
3. When finished, **fully exit MonsGeek from the tray**. SignalRGB should resume lighting automatically.

**Everyday use:** open MonsGeek to change settings, then quit it to return to SignalRGB. Lighting pauses while MonsGeek is running; you don't need to toggle the keyboard manually.

## Having trouble?

| What you see | What to do |
| --- | --- |
| `py` is not recognized | Install Python 3 and open a new PowerShell window. If Python is already installed, try `python .\patch_monsgeek.py --apply`. |
| Can't find `patch_monsgeek.py` | Open PowerShell from the extracted folder that contains that file, as shown in step 4. |
| Can't find the MonsGeek app file / unsupported bundle | Your app location or version may differ. See [advanced installation](HELP.md#3-patch-monsgeek-detection). |
| MonsGeek is still searching | Fully quit both apps, then reopen them. See [detection help](HELP.md#monsgeek-is-still-searching) if it continues. |
| Lighting stays paused | Quit MonsGeek from the tray, not just its window. Keep the keyboard enabled in SignalRGB. |
| Missing F6PK marker | See the [model-2381 firmware guide](firmware/README.md). Check your exact model before flashing. |

## Need to undo it?

Close both apps. Restore your old plugin and the MonsGeek backup made by the installer. [Step-by-step rollback instructions →](HELP.md#uninstall--rollback)

---

Experimental community fix, tested on one model-2381 keyboard with SignalRGB 2.5.80 and MonsGeek Driver v4 (V500.3.4_IOTV0.1.8). It is not an official release. Other models and stock firmware are unsupported. MonsGeek updates may replace the fix.

[Full help and compatibility](HELP.md) · [Technical details](TECHNICAL.md) · [Report a problem](https://github.com/sinsaintly/fun60-signalrgb-fix/issues)
