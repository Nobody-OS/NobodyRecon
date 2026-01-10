import pywifi
from pywifi import const
import time
import os
import math

RED = "\033[91m"
RESET = "\033[0m"
SIZE = 21
CENTER = SIZE // 2

wifi = pywifi.PyWiFi()
iface = wifi.interfaces()[0]

def scan_wifi():
    iface.scan()
    time.sleep(2)
    results = iface.scan_results()
    networks = []
    for r in results:
        ssid = r.ssid or "Hidden"
        signal = r.signal
        open_net = (len(r.akm) == 0)
        networks.append((ssid, signal, open_net))
    return networks

def draw_radar(networks):
    grid = [[" " for _ in range(SIZE)] for _ in range(SIZE)]
    grid[CENTER][CENTER] = "@"

    angle_step = 360 / max(1, len(networks))

    for i, (ssid, signal, open_net) in enumerate(networks):
        dist = min(10, max(1, int((100 - signal) / 10)))
        angle = math.radians(i * angle_step)
        x = int(CENTER + math.cos(angle) * dist)
        y = int(CENTER + math.sin(angle) * dist)
        if 0 <= x < SIZE and 0 <= y < SIZE:
            grid[y][x] = f"{RED}*{RESET}" if open_net else "*"

    os.system("cls" if os.name == "nt" else "clear")
    for row in grid:
        print(" ".join(row))
    print("\nLegende: @ = du | * = verschlüsselt | rotes * = offen\n")
    for ssid, signal, open_net in networks:
        flag = "OFFEN" if open_net else "OK"
        print(f"{ssid[:20]:20} {signal:>4} dBm {flag}")

while True:
    try:
        nets = scan_wifi()
        draw_radar(nets)
        time.sleep(3)
    except KeyboardInterrupt:
        break
