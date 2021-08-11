from time import sleep

import requests

from vpngate import VpnGate
from crawlers.utils import get_external_ip

print(f"Previous IP: {get_external_ip()}")
vpn_gate = VpnGate()
vpn_gate.connect_server()
print(f"Current IP : {get_external_ip()}")

sleep(3)
response = requests.get("https://www.google.com")
print(f"After vpn, {response.status_code}")

vpn_gate.disconnect()