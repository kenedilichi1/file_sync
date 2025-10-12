import socket
import threading
import time
import json
import platform
import subprocess

class DeviceDiscovery:
    def __init__(self, port=8888):
        self.port = port
        self.broadcast_addr = '255.255.255.255'
        self.online_devices = {}
        self.running = False
        self.socket = None
        self.listener_thread = None
        self.broadcaster_thread = None
        self.username = None
        self.device_name = None
        self.multicast_group = "224.1.1.1"  # fallback

    def start_discovery(self, username, device_name):
        """Start discovery service with firewall fix"""
        self.username = username
        self.device_name = device_name
        self._ensure_firewall_open()

        self.running = True

        self.listener_thread = threading.Thread(target=self._listen_for_devices)
        self.listener_thread.daemon = True
        self.listener_thread.start()

        time.sleep(0.1)

        self.broadcaster_thread = threading.Thread(target=self._broadcast_presence)
        self.broadcaster_thread.daemon = True
        self.broadcaster_thread.start()

        print(f"🚀 Discovery started for {username}@{device_name}")

    def stop_discovery(self):
        """Stop the discovery service"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
        print("🛑 Discovery service stopped")

    def _ensure_firewall_open(self):
        """Automatically allow UDP through Windows Firewall"""
        if platform.system().lower() == "windows":
            try:
                subprocess.run([
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    "name=FileSync_Discovery", "dir=in", "action=allow",
                    "protocol=UDP", f"localport={self.port}"
                ], capture_output=True, check=False)
            except Exception as e:
                print(f"⚠️ Could not configure firewall: {e}")

    def _broadcast_presence(self):
        """Broadcast device presence (with multicast fallback)"""
        while self.running:
            try:
                message = json.dumps({
                    "username": self.username,
                    "device_name": self.device_name,
                    "timestamp": time.time()
                }).encode()

                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.settimeout(0.5)
                    try:
                        sock.sendto(message, (self.broadcast_addr, self.port))
                    except Exception:
                        # fallback to multicast
                        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
                        sock.sendto(message, (self.multicast_group, self.port))

                time.sleep(5)
            except Exception as e:
                print(f"Broadcast error: {e}")
                time.sleep(2)

    def _listen_for_devices(self):
        """Listen for incoming broadcasts or multicasts"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', self.port))

            # Join multicast group
            group = socket.inet_aton(self.multicast_group)
            mreq = group + socket.inet_aton("0.0.0.0")
            try:
                self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            except Exception:
                pass  # Multicast may fail silently on Windows

            self.socket.settimeout(1)

            while self.running:
                try:
                    data, addr = self.socket.recvfrom(1024)
                    device_info = json.loads(data.decode())

                    if (device_info["username"] == self.username and
                        device_info["device_name"] == self.device_name):
                        continue

                    if time.time() - device_info["timestamp"] < 30:
                        key = f"{device_info['username']}@{device_info['device_name']}"
                        self.online_devices[key] = {
                            **device_info,
                            "ip_address": addr[0]
                        }

                    self._clean_old_devices()

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Listen error: {e}")
                    continue

        except Exception as e:
            print(f"Socket setup error: {e}")
        finally:
            if self.socket:
                self.socket.close()

    def _clean_old_devices(self):
        """Remove devices inactive >30s"""
        cutoff = time.time() - 30
        self.online_devices = {
            k: v for k, v in self.online_devices.items() if v["timestamp"] > cutoff
        }

    def get_online_devices_list(self):
        """Return list of visible devices"""
        return [
            {
                "username": info["username"],
                "device_name": info["device_name"],
                "ip_address": info["ip_address"],
                "last_seen": time.strftime("%H:%M:%S", time.localtime(info["timestamp"]))
            }
            for info in self.online_devices.values()
        ]
