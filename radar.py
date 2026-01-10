import os
import math
import time
import random
import sys
import subprocess
import json
from datetime import datetime

# Farben
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Radar-Einstellungen
SIZE = 21
CENTER = SIZE // 2
ECHO_LIFE = 3  # wie lange Punkte bleiben

# Modus
MODE = "test"
if len(sys.argv) > 1:
    MODE = sys.argv[1].lower()

# Logs Ordner
os.makedirs("logs", exist_ok=True)

# -------------------- Testdaten --------------------
FAKE_NETWORKS = [
    ("Home_WiFi", -42, False),
    ("Android_AP_93F2", -55, True),
    ("Vodafone-2G", -73, False),
    ("Hidden_Net", -80, True),
    ("Cafe_Free_WiFi", -60, True),
    ("TP-Link_Office", -50, False),
]

def fake_scan():
    nets = []
    for ssid, base_signal, open_net in FAKE_NETWORKS:
        drift = random.randint(-3, 3)
        signal = base_signal + drift
        nets.append((ssid, signal, open_net))
    return nets

# -------------------- Live Scan für Termux --------------------
def live_scan():
    try:
        result = subprocess.run(
            ["termux-wifi-scaninfo"],
            capture_output=True,
            text=True,
            timeout=5
        )
        data = json.loads(result.stdout)
        networks = []

        for n in data:
            ssid = n.get("ssid") or "Hidden"
            signal = n.get("level", -100)

            caps = n.get("capabilities", "")
            open_net = ("WEP" not in caps and "WPA" not in caps)

            networks.append((ssid, signal, open_net))

        return networks

    except Exception:
        return []

# -------------------- Logging --------------------
def log_scan(networks):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("logs/radar.log", "a") as f:
        for ssid, signal, open_net in networks:
            f.write(f"{ts} | {ssid} | {signal} | {'OPEN' if open_net else 'SECURE'}\n")

# -------------------- Radar --------------------
echo_points = []

def draw_radar(networks):
    global echo_points

    # Gitter
    grid = [[" " for _ in range(SIZE)] for _ in range(SIZE)]
    grid[CENTER][CENTER] = "@"

    new_points = []
    if networks:
        angle_step = 360 / len(networks)
    else:
        angle_step = 360

    # Neue Punkte berechnen
    for i, (ssid, signal, open_net) in enumerate(networks):
        dist = min(10, max(1, int((abs(signal) - 30) / 5)))
        angle = math.radians(i * angle_step)
        x = int(CENTER + math.cos(angle) * dist)
        y = int(CENTER + math.sin(angle) * dist)

        # Farbe
        color = GREEN
        if open_net:
            color = RED
        if signal > -45:
            color = YELLOW  # sehr nah

        new_points.append((x, y, color, ECHO_LIFE))

    # Alte Punkte verblassen
    updated_echo = []
    for x, y, color, life in echo_points:
        if life > 0:
            updated_echo.append((x, y, color, life - 1))
    echo_points = updated_echo + new_points

    # Punkte ins Grid eintragen
    for x, y, color, _ in echo_points:
        if 0 <= x < SIZE and 0 <= y < SIZE and (x, y) != (CENTER, CENTER):
            grid[y][x] = f"{color}*{RESET}"

    # Clear Screen
    os.system("cls" if os.name == "nt" else "clear")

    title = "TEST RADAR" if MODE == "test" else "LIVE RADAR"
    print(f"NobodyRecon – {title}\n")

    # ASCII-Radar ausgeben
    for row in grid:
        print(" ".join(row))

    # Legende
    print("\nLegende:")
    print(" @ = du")
    print(" grün * = verschlüsselt")
    print(" rot * = offen")
    print(" gelb * = sehr nah\n")

    # Liste Netzwerke
    for ssid, signal, open_net in networks:
        status = "OFFEN" if open_net else "OK"
        warn = " !!!" if open_net and signal > -50 else ""
        print(f"{ssid[:20]:20} {signal:>4} dBm {status}{warn}")

# -------------------- Main Loop --------------------
while True:
    try:
        # Live Scan nur, wenn möglich
        nets = fake_scan()
        if MODE == "live":
            nets_live = live_scan()
            if nets_live:
                nets = nets_live
            else:
                print("\n[!] Live Scan liefert keine Daten – Testmodus aktiv\n")
                MODE = "test"

        log_scan(nets)
        draw_radar(nets)
        time.sleep(3)

    except KeyboardInterrupt:
        break
