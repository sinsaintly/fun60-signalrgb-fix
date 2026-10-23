# Technical notes

## Why MonsGeek could not identify the keyboard

The experimental model-2381 firmware places ASCII `F6PK` in identity payload bytes 3–6. MonsGeek interprets bytes 1–4 as a little-endian 32-bit model ID, so two marker bytes change the ID it sees. The desktop patch special-cases exactly `4D 09 46 36 50 4B` in bytes 1–6 as model 2381 and preserves the original reader for other responses. Both tested identity-reading sites are patched.

This is an app compatibility workaround for the experimental marker placement. It does not prove a different firmware is compatible and does not modify keyboard firmware.

## Process-based ownership

The plugin exports `ConflictingProcesses()` with `MonsGeek Driver v4.exe`. SignalRGB owns the lighting interface while MonsGeek is closed. While MonsGeek runs, SignalRGB pauses the device so configuration reads/writes do not compete with RGB frames. The earlier UDP pause/acknowledgement experiment is not part of this design: waiting for an acknowledgement from an already-paused plugin caused detection to hang.

## Lighting protocol

The plugin validates model 2381, firmware 0x0302, and F6PK before switching to mode 13. It samples 61 key centers from the current canvas. A frame contains 378 RGB bytes for 126 addressable slots, sent in seven command-0x0C feature-report pages (six 56-byte bodies and one 42-byte body). Selector is 0xFF; only the final page has apply flag 2.

**Apply flag 2 is RAM-only only in this specific experimental firmware. Do not send these frames to stock firmware.** Capability guards are required. The host targets one frame every 33 ms; actual hardware frame rate was not measured.

The 120×40 layout contains display-only keycap pixels but renders from the original 61 centers. Shutdown attempts to restore the captured lighting mode. It does not change remaps, calibration, or actuation settings.

## Timing

The plugin first checks mode readiness after 150 ms instead of 600 ms. If mode 13 is not ready, it queries again until its 600 ms deadline. Query/read spacing remains 70 ms. MonsGeek identity retries for USB 3151:502D use up to 15 attempts spaced 100 ms instead of 3 attempts spaced 500 ms; other devices retain the original policy. USB request durations add to these delays.

These are code-level timing reductions, not a measured fivefold startup speedup. SignalRGB's process watcher, app initialization, and the vendor service are unchanged.

## Development checks

From the repository directory, with Python 3 and Node.js installed:

```powershell
py -3 -m unittest discover -s tests -p "test_*.py"
node tests/test-plugin.cjs
```

Tests use mocked USB and temporary files. They do not flash or contact a keyboard. A real-device check remains necessary for a new firmware, hardware revision, or app version. The patcher is intentionally coupled to the tested minified bundle and refuses unfamiliar patterns.
