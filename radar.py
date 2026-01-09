import subprocess
import math
import time
import os
import re

RED = "\033[91m"
RESET = "\033[0m"

SIZE = 21
CENTER = SIZE // 2

def scan_wifi():
    cmd = ["iw", "dev", "wlan0", "scan"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout

    nets = []
    ssid = None
    signal = None
    open_net = False

    for line in out.splitlines():
        line = line.strip()

        if line.startswith("BSS"):
            if ssid and signal:
                nets.append((ssid, signal, open_net))
            ssid = None
            signal = None
            open_net = False

        if "signal:" in line:
            signal = int(float(line.split("signal:")[1].split("dBm")[0]))

        if "SSID:" in line:
            ssid = line.replace("SSID:", "").strip()

        if "capability:" in line and "Privacy" not in line:
            open_net = True

    if ssid and signal:
        nets.append((ssid, signal, open_net))

    return nets

def draw_radar(networks):
    grid = [[" " for _ in range(SIZE)] for _ in range(SIZE)]
    grid[CENTER][CENTER] = "@"

    angle_step = 360 / max(1, len(networks))

    for i, (ssid, signal, open_net) in enumerate(networks):
        dist = min(10, max(1, int((abs(signal) - 30) / 5)))
        angle = math.radians(i * angle_step)

        x = int(CENTER + math.cos(angle) * dist)
        y = int(CENTER + math.sin(angle) * dist)

        if 0 <= x < SIZE and 0 <= y < SIZE:
            grid[y][x] = f"{RED}*{RESET}" if open_net else "*"

    os.syst
