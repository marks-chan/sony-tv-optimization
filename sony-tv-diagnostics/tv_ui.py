import os
import pathlib
import re
import subprocess
import xml.etree.ElementTree as ET

TARGET = os.environ.get("SONY_TV_TARGET")
if not TARGET:
    raise SystemExit("Set SONY_TV_TARGET to the authorized TV's ADB address first.")
BASE = pathlib.Path(__file__).resolve().parent


def shell(*args):
    return subprocess.run(["adb", "-s", TARGET, "shell", *args],
                          check=True, capture_output=True, text=True, timeout=20).stdout


def tree():
    shell("uiautomator", "dump", "/data/local/tmp/sony-ui.xml")
    return ET.fromstring(shell("cat", "/data/local/tmp/sony-ui.xml"))


def snapshot():
    root = tree()
    for node in root.iter("node"):
        a = node.attrib
        if a.get("text") or a.get("content-desc") or a.get("checkable") == "true":
            print({k: a.get(k) for k in ["text", "content-desc", "resource-id",
                  "class", "clickable", "checked", "focused", "bounds"]}, flush=True)
    return root


def tap(label):
    matches = [n for n in tree().iter("node")
               if label in [n.get("text"), n.get("content-desc")]
               and n.get("clickable") == "true"]
    if len(matches) != 1:
        raise ValueError("Expected one clickable control: " + label)
    coords = list(map(int, re.findall(r"\d+", matches[0].get("bounds"))))
    x1, y1, x2, y2 = coords
    shell("input", "tap", str((x1 + x2) // 2), str((y1 + y2) // 2))


def key(code):
    shell("input", "keyevent", code)


def screenshot(label):
    p = subprocess.run(["adb", "-s", TARGET, "exec-out", "screencap", "-p"],
                       check=True, capture_output=True, timeout=15)
    path = BASE / (label + ".png")
    path.write_bytes(p.stdout)
    print("SCREEN=" + str(path), flush=True)
