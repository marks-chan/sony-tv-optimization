import datetime
import json
import os
import pathlib
import re
import subprocess
import sys

TARGET = os.environ.get("SONY_TV_TARGET")
if not TARGET:
    raise SystemExit("Set SONY_TV_TARGET to the authorized TV's ADB address first.")
BASE = pathlib.Path(__file__).resolve().parent


def shell(command, timeout=20):
    try:
        p = subprocess.run(
            ["adb", "-s", TARGET, "shell", command],
            capture_output=True, text=True, timeout=timeout,
        )
        return {"command": command, "returncode": p.returncode,
                "stdout": p.stdout, "stderr": p.stderr}
    except subprocess.TimeoutExpired:
        return {"command": command, "error": "timeout"}


label = sys.argv[1] if len(sys.argv) > 1 else "snapshot"
if not re.fullmatch(r"[a-z0-9_-]+", label):
    raise SystemExit("Invalid snapshot label")
maker = shell("getprop ro.product.manufacturer")
if maker.get("stdout", "").strip().lower() != "sony":
    raise SystemExit("The authorized target did not identify as Sony")

commands = {
    "model": "getprop ro.product.model",
    "firmware": "getprop ro.build.display.id",
    "hardware": "getprop ro.hardware",
    "uptime": "uptime",
    "storage": "df -k /data",
    "memory": "cat /proc/meminfo",
    "cpu": "dumpsys cpuinfo",
    "processes": "top -b -n 1 -m 20",
    "app_memory": "dumpsys meminfo --oom",
    "diskstats": "dumpsys diskstats",
    "third_party_apps": "pm list packages -3",
    "disabled_apps": "pm list packages -d",
    "launcher": "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME",
    "animation_window": "settings get global window_animation_scale",
    "animation_transition": "settings get global transition_animation_scale",
    "animation_animator": "settings get global animator_duration_scale",
    "low_power": "settings get global low_power",
    "thermal": "dumpsys thermalservice",
    "downloads_size": "du -sk /sdcard/Download",
}
result = {"target": TARGET, "timestamp": datetime.datetime.now().astimezone().isoformat(),
          "label": label, "checks": {}}
for name, command in commands.items():
    result["checks"][name] = shell(command)
    print(json.dumps({"check": name, "status": result["checks"][name].get("returncode", "timeout")}), flush=True)
path = BASE / (label + ".json")
if path.exists():
    raise SystemExit("Snapshot already exists: " + str(path))
path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
print("SNAPSHOT=" + str(path), flush=True)
