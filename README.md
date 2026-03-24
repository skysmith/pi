# Pi Project Notes

This repo currently documents the state of work on `pi@raspberrypi.local`, a Raspberry Pi Zero 2 W running Debian 13 (`trixie`).

## Current State

- Device: Raspberry Pi Zero 2 W Rev 1.0
- OS: Debian GNU/Linux 13 (`trixie`)
- Arch: `aarch64`
- Memory: about `416 MiB` usable RAM with swap enabled
- Storage: about `22 GiB` free on `/`
- Access: SSH is enabled and reachable at `pi@raspberrypi.local`

## What We Did

- Connected over SSH with the default `pi` account.
- Confirmed the default password is still in use.
- Removed the old `/home/pi/ai-hub` project.
- Checked feasibility for `nanochat` and Ollama on this hardware.
- Started a RetroPie source install via `RetroPie-Setup`.

## RetroPie Status

RetroPie is in progress, not finished.

As of the latest check:

- `RetroPie-Setup` is cloned at `/home/pi/RetroPie-Setup`
- required Debian build dependencies were installed
- RetroPie's custom `SDL2` build completed successfully
- `RetroArch` source checkout completed
- `RetroArch` is currently building from source

This is slow because the Pi is a Zero 2 W with limited RAM and the install path on Debian 13 is source-heavy.

## Issues Hit So Far

- The Pi is still using the default password, which is a security risk.
- RetroPie is not running on the easiest supported path here because the device is on Debian 13 instead of a standard RetroPie image.
- `RetroPie-Setup` attempted a GPG keyserver lookup and printed `gpg: keyserver receive failed: No route to host`, but the install continued afterward.
- The text UI in `retropie_setup.sh` is awkward over raw SSH, so the package script path was more reliable:
  - `sudo ./retropie_packages.sh setup basic_install`
- Because builds are happening from source, installs can take a long time and may still fail later from RAM pressure or package incompatibilities.

## Quick Tips

- SSH in with:

```bash
ssh pi@raspberrypi.local
```

- Check whether the RetroPie build is still active:

```bash
ps aux | grep -E 'retropie|retroarch|sdl2|make' | grep -v grep
```

- Reattach by going into the setup folder:

```bash
cd /home/pi/RetroPie-Setup
```

- If you need a fresh status snapshot:

```bash
free -h
df -h /
tail -n 50 /home/pi/RetroPie-Setup/logs/* 2>/dev/null
```

- The default password should be changed as soon as practical:

```bash
passwd
```

## Practical Notes

- `nanochat` is not realistic on this hardware.
- Ollama might install, but useful local inference on this Pi is not realistic.
- Plex playback is more realistic through Kodi/LibreELEC than through an official Plex app, but this hardware is still very tight for that role.

## Next Recommended Steps

1. Let the current RetroPie build finish and record the final result.
2. Change the `pi` account password.
3. Decide whether this Pi should remain a RetroPie box, become a lightweight Plex/Kodi client experiment, or just stay as a small network utility device.
