import socket
import threading
import time
import json

class DeviceDiscovery:
    def __init__(self, port=8888, broadcast_addr='255.255.255.255'):
        self.port = port
        self.broadcast_addr = broadcast_addr
        self.online_devices = {}
        self.running = False
        self.socket = None
        self.listener_thread = None
        self.broadcaster_thread = None
        self.username = None
        self.device_name = None
        
    def start_discovery(self, username, device_name):
        """Start the discovery service"""
        self.running = True
        self.username = username
        self.device_name = device_name
        
        # Start listener thread first
        self.listener_thread = threading.Thread(target=self._listen_for_devices)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        
        # Give listener a moment to start
        time.sleep(0.1)
        
        # Start broadcaster thread
        self.broadcaster_thread = threading.Thread(target=self._broadcast_presence)
        self.broadcaster_thread.daemon = True
        self.broadcaster_thread.start()
        
        print(f"Discovery started for {username} on {device_name}")
        
    def stop_discovery(self):
        """Stop the discovery service"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("Discovery service stopped")
            
    def _broadcast_presence(self):
        """Broadcast presence to the network - FIXED: uses instance attributes"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            while self.running:
                try:
                    data = json.dumps({
                        'username': self.username,
                        'device_name': self.device_name,
                        'timestamp': time.time()
                    })
                    sock.sendto(data.encode(), (self.broadcast_addr, self.port))
                    time.sleep(5)  # Broadcast every 5 seconds
                except Exception as e:
                    print(f"Broadcast error: {e}")
                    time.sleep(1)  # Wait before retrying
                    
    def _listen_for_devices(self):
        """Listen for incoming device broadcasts"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.settimeout(1.0)  # Add timeout to allow checking running flag
            self.socket.bind(('', self.port))
            
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(1024)
                    device_info = json.loads(data.decode())
                    
                    # Don't add our own device
                    if (device_info['username'] == self.username and 
                        device_info['device_name'] == self.device_name):
                        continue
                    
                    # Only add devices that have been active in the last 30 seconds
                    current_time = time.time()
                    if device_info['timestamp'] > current_time - 30:
                        self.online_devices[f"{device_info['username']}@{device_info['device_name']}"] = {
                            'username': device_info['username'],
                            'device_name': device_info['device_name'],
                            'ip_address': addr[0],
                            'last_seen': device_info['timestamp']
                        }
                    
                    # Clean up old devices
                    self._clean_old_devices()
                    
                except socket.timeout:
                    continue  # Timeout is expected, just continue
                except Exception as e:
                    print(f"Listen error: {e}")
                    continue
                    
        except Exception as e:
            print(f"Socket setup error: {e}")
        finally:
            if self.socket:
                self.socket.close()
                
    def _clean_old_devices(self):
        """Remove devices not seen in the last 30 seconds"""
        current_time = time.time()
        to_remove = []
        
        for device_id, info in self.online_devices.items():
            if info['last_seen'] < current_time - 30:
                to_remove.append(device_id)
                
        for device_id in to_remove:
            del self.online_devices[device_id]
            
    def get_online_devices(self):
        """Get current online devices (excluding self)"""
        return self.online_devices.copy()
    
    def get_online_devices_list(self):
        """Get online devices as a formatted list"""
        devices = []
        for device_id, info in self.online_devices.items():
            devices.append({
                'username': info['username'],
                'device_name': info['device_name'],
                'ip_address': info['ip_address'],
                'last_seen': time.strftime('%H:%M:%S', time.localtime(info['last_seen']))
            })
        return devices

# Usage example and test
def main():
    # Example usage
    discovery = DeviceDiscovery()
    
    try:
        # Start discovery with user credentials
        discovery.start_discovery("alice", "Alice-Laptop")
        
        # Let it run for 20 seconds to see it working
        for i in range(20):
            devices = discovery.get_online_devices_list()
            print(f"\n--- Online Devices ({len(devices)}) ---")
            for device in devices:
                print(f"User: {device['username']}, Device: {device['device_name']}, "
                      f"IP: {device['ip_address']}, Last Seen: {device['last_seen']}")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nStopping discovery...")
    finally:
        discovery.stop_discovery()

if __name__ == "__main__":
    main()