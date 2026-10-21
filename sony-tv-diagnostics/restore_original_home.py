"""Restore the Sony home screen while preserving apps and their data."""

import os
import subprocess

TARGET = os.environ.get("SONY_TV_TARGET")
if not TARGET:
    raise SystemExit("Set SONY_TV_TARGET to the authorized TV's ADB address first.")
ORIGINAL_HOME = (
    "com.dangbei.TVHomeLauncher/"
    "com.dangbei.leard.leradlauncher.ui.sony.main.MainActivity"
)

subprocess.run(["adb", "connect", TARGET], check=True, timeout=12)
manufacturer = subprocess.run(
    ["adb", "-s", TARGET, "shell", "getprop", "ro.product.manufacturer"],
    check=True, capture_output=True, text=True, timeout=10,
).stdout.strip()
if manufacturer.lower() != "sony":
    raise SystemExit("The target did not identify as Sony; no settings changed.")

subprocess.run(
    ["adb", "-s", TARGET, "shell", "pm", "enable", "--user", "0",
     "com.dangbei.TVHomeLauncher"], check=True, timeout=15,
)
subprocess.run(
    ["adb", "-s", TARGET, "shell", "cmd", "package", "set-home-activity",
     "--user", "0", ORIGINAL_HOME], check=True, timeout=15,
)
subprocess.run(
    ["adb", "-s", TARGET, "shell", "am", "start", "-n", ORIGINAL_HOME],
    check=True, timeout=15,
)
subprocess.run(
    ["adb", "-s", TARGET, "shell", "input", "keyevent", "KEYCODE_HOME"],
    check=True, timeout=10,
)
print("Sony home screen restored. Applications and their data were preserved.")
