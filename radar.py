import os
import math
import time
import subprocess
import json
from datetime import datetime

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

SIZE = 21
CENTER = SIZE // 2
ECHO_LIFE = 3

os.makedirs("logs", exist_ok=True)

echo_points = []
nets = []

def live_scan():
    result = subprocess.run(
        ["termux-wifi-scaninfo"],
        capture_output=True,
        text=True,
        timeout=5
    )

    data = json.loads(result.stdout or "[]")
    networks = []

    for n in data:
        ssid = n.get("ssid") or "Hidden"
        signal = n.get("level", -100)

        caps = n.get("capabilities", "")
        open_net = ("WPA2" not in caps and "WPA3" not in caps and "WEP" not in caps)

        networks.append((ssid, signal, open_net))

    return networks

def log_scan(networks):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("logs/radar.log", "a") as f:
        for ssid, signal, open_net in networks:
            f.write(f"{ts} | {ssid} | {signal} | {'OPEN' if open_net else 'SECURE'}\n")

def draw_radar(networks):
    global echo_points

    grid = [[" " for _ in range(SIZE)] for _ in range(SIZE)]
    grid[CENTER][CENTER] = "@"

    new_points = []
    angle_step = 360 / len(networks) if networks else 360

    for i, (ssid, signal, open_net) in enumerate(networks):
        dist = int(max(1, min(9, (100 + signal) / 10)))

        angle = math.radians(i * angle_step)
        x = int(CENTER + math.cos(angle) * dist)
        y = int(CENTER + math.sin(angle) * dist)

        color = GREEN
        if open_net:
            color = RED
        if signal > -45:
            color = YELLOW

        new_points.append((x, y, color, ECHO_LIFE))

    echo_points = [
        (x, y, c, l - 1)
        for (x, y, c, l) in echo_points
        if l > 0
    ]

    echo_points.extend(new_points)

    for x, y, color, _ in echo_points:
        if 0 <= x < SIZE and 0 <= y < SIZE and (x, y) != (CENTER, CENTER):
            grid[y][x] = f"{color}*{RESET}"

    os.system("clear")

    print("LIVE RADAR\n")

    for row in grid:
        print(" ".join(row))

    print("\n@ = du | grün = sicher | rot = offen | gelb = stark")

    for ssid, signal, open_net in networks:
        status = "OFFEN" if open_net else "OK"
        print(f"{ssid[:20]:20} {signal:>4} dBm {status}")

while True:
    try:
        nets = live_scan()
        log_scan(nets)
        draw_radar(nets)
        time.sleep(3)

    except KeyboardInterrupt:
        break
