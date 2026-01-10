import subprocess
import time
import os
import math

# gleiche Radar-Funktionen wie oben

def scan_wifi():
    result = subprocess.run(["termux-wifi-scaninfo"], capture_output=True, text=True)
    networks = []
    import json
    data = json.loads(result.stdout)
    for n in data:
        ssid = n["SSID"] or "Hidden"
        signal = n["level"]
        open_net = n["capabilities"] == "[ESS]"
        networks.append((ssid, signal, open_net))
    return networks
