import socket
import threading
import time
import json
import struct

class DeviceDiscovery:
    def __init__(self, port=8889, broadcast_addr=None):
        self.port = port
        self.broadcast_addr = broadcast_addr or self._get_broadcast_address()
        self.online_devices = {}
        self.running = False
        self.socket = None
        self.listener_thread = None
        self.broadcaster_thread = None
        self.username = None
        self.device_name = None

    def _get_broadcast_address(self):
        """Auto-detect subnet broadcast address (works cross-platform)"""
        try:
            # Get the real LAN IP (not 127.x.x.x)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            # Compute broadcast by replacing last octet with 255
            ip_parts = local_ip.split('.')
            ip_parts[-1] = '255'
            broadcast = '.'.join(ip_parts)

            print(f"[Network] Local IP: {local_ip}, Broadcast: {broadcast}")
            return broadcast
        except Exception as e:
            print(f"[Network] Could not detect LAN IP automatically: {e}")
            return '255.255.255.255'


    def start_discovery(self, username, device_name):
        """Start discovery service"""
        self.running = True
        self.username = username
        self.device_name = device_name

        print(f"🔍 Starting discovery for {username}@{device_name}")
        print(f"📡 Broadcasting to {self.broadcast_addr}:{self.port}")

        self.listener_thread = threading.Thread(target=self._listen_for_devices, daemon=True)
        self.listener_thread.start()

        time.sleep(0.2)
        self.broadcaster_thread = threading.Thread(target=self._broadcast_presence, daemon=True)
        self.broadcaster_thread.start()

    def stop_discovery(self):
        """Stop discovery"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("🛑 Discovery stopped")

    def _broadcast_presence(self):
        """Broadcast presence over UDP"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            while self.running:
                try:
                    data = json.dumps({
                        'username': self.username,
                        'device_name': self.device_name,
                        'timestamp': time.time()
                    })
                    sock.sendto(data.encode(), (self.broadcast_addr, self.port))
                    print(f"[Broadcasting] {self.username}@{self.device_name} → {self.broadcast_addr}:{self.port}")
                    time.sleep(5)
                except Exception as e:
                    print(f"[Broadcast error] {e}")
                    time.sleep(2)

    def _listen_for_devices(self):
        """Listen for other devices on the same port"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.settimeout(1.0)
            self.socket.bind(('', self.port))
            print(f"👂 Listening on UDP port {self.port}")

            while self.running:
                try:
                    data, addr = self.socket.recvfrom(1024)
                    message = json.loads(data.decode())

                    match message:
                        case {"type": "discover", "username": username, "device_name": device_name, "timestamp": ts}:
                        # Ignore self
                            if username == self.username and device_name == self.device_name:
                                continue
                            self._handle_discovery(username, device_name, addr[0], ts)

                        case {"type": "ping", "username": username}:
                            print(f"[Ping] Received ping from {username}@{addr[0]}")

                        case _:
                            print(f"[Unknown message] {message}")

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[Listen error] {e}")
                    continue
        except Exception as e:
            print(f"[Socket setup error] {e}")
        finally:
            if self.socket:
                self.socket.close()

    def _clean_old_devices(self):
        """Remove devices not seen recently"""
        current_time = time.time()
        expired = [k for k, v in self.online_devices.items() if v['last_seen'] < current_time - 30]
        for k in expired:
            print(f"[Cleanup] Removing {k}")
            del self.online_devices[k]

    def get_online_devices_list(self):
        """Return list of online devices"""
        return [
            {
                'username': v['username'],
                'device_name': v['device_name'],
                'ip_address': v['ip_address'],
                'last_seen': time.strftime('%H:%M:%S', time.localtime(v['last_seen']))
            }
            for v in self.online_devices.values()
        ]

