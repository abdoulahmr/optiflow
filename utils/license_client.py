# utils/license_client.py
import socket
import platform
import uuid
import re
import requests

class LicenseClient:
    def __init__(self, server_url: str, api_token: str):
        self.server_url = server_url.rstrip('/')
        self.api_token = api_token

    def collect_machine_info(self) -> dict:
        # Fix: uuid.getnode() returns an int, we must format it as a hex string first
        mac_int = uuid.getnode()
        mac_hex = format(mac_int, '012x')
        mac = ':'.join(re.findall('..', mac_hex))
        
        try:
            hostname = socket.gethostname()
        except Exception:
            hostname = 'unknown'

        public_ip = None
        try:
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
        except Exception:
            pass

        return {
            'hostname':    hostname,
            'os_info':     platform.system(),
            'os_version':  platform.version(),
            'architecture':platform.machine(),
            'processor':   platform.processor() or platform.machine(),
            'local_ip':    socket.gethostbyname(socket.gethostname()),
            'mac_address': mac,
            'public_ip':   public_ip,
        }
    
    def activate(self, license_key: str) -> dict:
        machine = self.collect_machine_info()
        try:
            r = requests.post(
                f'{self.server_url}/api/v1/licenses/activate',
                json={'license_key': license_key, 'machine': machine},
                headers={'Authorization': f'Bearer {self.api_token}'},
                timeout=10,
            )
            return r.json(), r.status_code
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}, 500

    def verify(self, license_key: str) -> dict:
        machine = self.collect_machine_info()
        try:
            r = requests.post(
                f'{self.server_url}/api/v1/licenses/verify',
                json={'license_key': license_key, 'machine': machine},
                headers={'Authorization': f'Bearer {self.api_token}'},
                timeout=10,
            )
            return r.json(), r.status_code
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}, 500