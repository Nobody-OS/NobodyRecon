import subprocess
import json

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
