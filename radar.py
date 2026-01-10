import os
import math
import time
import random

RED = "\033[91m"
RESET = "\033[0m"

SIZE = 21
CENTER = SIZE // 2

FAKE_NETWORKS = [
    ("Home_WiFi", -42, False),
    ("Android_AP_93F2", -55, True),
    ("Vodafone-2G", -70, False),
    ("Hidden_Net", -80, True),
    ("Cafe_Free_WiFi", -60, True),
    ("TP-Link_Office", -48, False),
]

def fake_scan():
    nets = []
    for ssid, base_signal, open_net in FAKE_NETWORKS:
        drift = random.randint(-3, 3)
        signal = base_signal + drift
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

    os.system("cls" if os.name == "nt" else "clear")

    for row in grid:
        print(" ".join(row))

    print("\nLegende: @ = du | * = verschlüsselt | rotes * = offen\n")

    for ssid, signal, open_net in networks:
        flag = "OFFEN" if open_net else "OK"
        print(f"{ssid[:20]:20} {signal:>4} dBm {flag}")

if __name__ == "__main__":
    print("NobodyRecon – TEST RADAR\n")
    time.sleep(1)

    while True:
        nets = fake_scan()
        draw_radar(nets)
        time.sleep(2)
