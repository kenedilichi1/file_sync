# LocalSync - Secure Local Network File Transfer

![LocalSync](https://img.shields.io/badge/Version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.7%2B-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A secure, cross-platform terminal tool for transferring files between computers on the same local Wi-Fi network. No internet required - perfect for offline environments, secure transfers, and quick file sharing.

## 🌟 Features

- **🔒 Zero Internet Dependency** - Works entirely on local networks
- **🛡️ End-to-End Encryption** - SSL/TLS and optional file encryption
- **📱 Cross-Platform** - Windows, macOS, and Linux support
- **👥 User Authentication** - Secure login system
- **🔍 Device Discovery** - Automatic detection of online devices
- **📊 Progress Tracking** - Real-time transfer progress with visual bars
- **🗜️ Built-in Compression** - Faster transfers with automatic compression
- **✅ Acceptance Protocol** - Approve or decline incoming transfers
- **⚙️ Configurable Auto-Accept** - Trusted senders and size-based rules
- **🔔 Desktop Notifications** - Alert for incoming transfers (optional)

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- All computers on the same Wi-Fi network

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/localsync.git
cd localsync

# Install dependencies
pip install -r requirements.txt

# Install the application
pip install .
```

### First-Time Setup

```bash
# Run LocalSync
localsync

# Register a new user
localsync> register yourusername
Password: ********
Confirm Password: ********

# Login
localsync> login yourusername
Password: ********
```

## 🚀 Quick Start

### 1. Discover Devices

```bash
localsync> devices
Online devices:
1. alice (Alice-MacBook) - 192.168.1.101 [Online]
2. bob (Bob-PC) - 192.168.1.102 [Online]
```

### 2. Send a File

```bash
# Basic transfer
localsync> send /path/to/file.txt alice

# Encrypted transfer
localsync> send /path/to/secret-file.txt bob --encrypt
Encryption password: ********
Confirm password: ********

# Transfer without compression
localsync> send /path/to/file.jpg alice --no-compress
```

### 3. Receive Files

When someone sends you a file:

```
📨 Incoming file transfer request:
   From: alice
   File: project_report.pdf
   Size: 15.2 MB
Accept transfer? (y/n): y
✅ Transfer accepted - receiving file...
```

## ⚙️ Configuration

### Auto-Accept Settings

```bash
# Enable auto-accept
localsync> config auto_accept true

# Add trusted senders
localsync> trust alice
localsync> trust bob

# Set maximum auto-accept size (500MB)
localsync> config max_auto_accept_size 524288000

# View all settings
localsync> config
```

### Change Download Directory

```bash
localsync> config default_download_dir ~/Documents/Received
localsync> set_download_dir ~/Documents/Received
```

## 🎯 Advanced Usage

### Batch Operations

```bash
# Send multiple files
for file in *.pdf; do localsync send "$file" recipient; done
```

### Scripting Integration

```python
#!/usr/bin/env python3
from localsync import LocalSyncCLI

def automated_transfer():
    cli = LocalSyncCLI()
    cli.onecmd("login myuser")
    cli.onecmd("send /data/report.pdf colleague")
    cli.onecmd("exit")
```

### Enterprise Features

```bash
# Always prompt for large files (>100MB)
localsync> config always_ask_for_large_files true
localsync> config large_file_threshold 104857600

# Set request timeout (seconds)
localsync> config request_timeout 300
```

## 🔧 Troubleshooting

### Common Issues

**Devices not showing up?**

- Ensure all computers are on the same Wi-Fi network
- Check firewall allows UDP port 8888 and TCP port 8889
- Restart LocalSync: `localsync> exit` and relaunch

**Connection refused?**

- Verify recipient is logged into LocalSync
- Check firewall settings on both computers

**Slow transfer speeds?**

- Use `--no-compress` for already compressed files
- Check Wi-Fi signal strength

**Certificate errors?**

```bash
# Regenerate certificates
rm -rf ~/.localsync/certs/
localsync  # Certificates will auto-generate
```

### Debug Mode

```bash
# Run with verbose logging
localsync --debug

# Check network connectivity
localsync> ping 192.168.1.101
```

## 🏗️ Architecture

```
LocalSync Application
├── Authentication Module
├── Device Discovery Module (UDP Broadcast)
├── File Transfer Module (TCP/TLS)
├── Encryption Engine (AES-256 + SSL)
├── Compression Engine (ZLIB/LZMA)
├── Configuration System
└── User Interface (CLI)
```

### Network Protocols

- **Discovery**: UDP broadcast on port 8888
- **Transfer**: TCP with TLS on port 8889
- **Heartbeat**: 5-second device presence updates

## 🔒 Security Features

- **No Internet Exposure**: All traffic stays on local network
- **Certificate Pinning**: Self-signed certificates prevent MITM attacks
- **Password Hashing**: SHA-256 with salt for authentication
- **Optional File Encryption**: AES-256 for sensitive files
- **Checksum Verification**: Ensures file integrity
- **Acceptance Protocol**: Users must approve incoming transfers

## 📊 Performance

| File Size | Transfer Time  | With Compression |
| --------- | -------------- | ---------------- |
| 1 MB      | ~1-2 seconds   | ~0.5-1 second    |
| 100 MB    | ~20-30 seconds | ~10-15 seconds   |
| 1 GB      | ~3-4 minutes   | ~1.5-2 minutes   |

_Based on typical 802.11ac Wi-Fi speeds_

## 🚀 Use Cases

- **Enterprise Environments**: Secure internal file sharing
- **Educational Institutions**: Classroom file distribution
- **Creative Studios**: Large media file transfers
- **Offline Networks**: Air-gapped or restricted environments
- **Event Spaces**: Conference and workshop file sharing
- **Home Networks**: Quick family file transfers

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](https://github.com/yourusername/localsync/wiki)
- 🐛 [Issue Tracker](https://github.com/yourusername/localsync/issues)
- 💬 [Discussions](https://github.com/yourusername/localsync/discussions)
- 📧 Email: support@localsync.org

## 🙏 Acknowledgments

# LocalSync - Secure Local Network File Transfer

![LocalSync](https://img.shields.io/badge/Version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.7%2B-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A secure, cross-platform terminal tool for transferring files between computers on the same local Wi-Fi network. No internet required - perfect for offline environments, secure transfers, and quick file sharing.

## 🌟 Features

- **🔒 Zero Internet Dependency** - Works entirely on local networks
- **🛡️ End-to-End Encryption** - SSL/TLS and optional file encryption
- **📱 Cross-Platform** - Windows, macOS, and Linux support
- **👥 User Authentication** - Secure login system
- **🔍 Device Discovery** - Automatic detection of online devices
- **📊 Progress Tracking** - Real-time transfer progress with visual bars
- **🗜️ Built-in Compression** - Faster transfers with automatic compression
- **✅ Acceptance Protocol** - Approve or decline incoming transfers
- **⚙️ Configurable Auto-Accept** - Trusted senders and size-based rules
- **🔔 Desktop Notifications** - Alert for incoming transfers (optional)

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- All computers on the same Wi-Fi network

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/localsync.git
cd localsync

# Install dependencies
pip install -r requirements.txt

# Install the application
pip install .
```

### First-Time Setup

```bash
# Run LocalSync
localsync

# Register a new user
localsync> register yourusername
Password: ********
Confirm Password: ********

# Login
localsync> login yourusername
Password: ********
```

## 🚀 Quick Start

### 1. Discover Devices

```bash
localsync> devices
Online devices:
1. alice (Alice-MacBook) - 192.168.1.101 [Online]
2. bob (Bob-PC) - 192.168.1.102 [Online]
```

### 2. Send a File

```bash
# Basic transfer
localsync> send /path/to/file.txt alice

# Encrypted transfer
localsync> send /path/to/secret-file.txt bob --encrypt
Encryption password: ********
Confirm password: ********

# Transfer without compression
localsync> send /path/to/file.jpg alice --no-compress
```

### 3. Receive Files

When someone sends you a file:

```
📨 Incoming file transfer request:
   From: alice
   File: project_report.pdf
   Size: 15.2 MB
Accept transfer? (y/n): y
✅ Transfer accepted - receiving file...
```

## ⚙️ Configuration

### Auto-Accept Settings

```bash
# Enable auto-accept
localsync> config auto_accept true

# Add trusted senders
localsync> trust alice
localsync> trust bob

# Set maximum auto-accept size (500MB)
localsync> config max_auto_accept_size 524288000

# View all settings
localsync> config
```

### Change Download Directory

```bash
localsync> config default_download_dir ~/Documents/Received
localsync> set_download_dir ~/Documents/Received
```

## 🎯 Advanced Usage

### Batch Operations

```bash
# Send multiple files
for file in *.pdf; do localsync send "$file" recipient; done
```

### Scripting Integration

```python
#!/usr/bin/env python3
from localsync import LocalSyncCLI

def automated_transfer():
    cli = LocalSyncCLI()
    cli.onecmd("login myuser")
    cli.onecmd("send /data/report.pdf colleague")
    cli.onecmd("exit")
```

### Enterprise Features

```bash
# Always prompt for large files (>100MB)
localsync> config always_ask_for_large_files true
localsync> config large_file_threshold 104857600

# Set request timeout (seconds)
localsync> config request_timeout 300
```

## 🔧 Troubleshooting

### Common Issues

**Devices not showing up?**

- Ensure all computers are on the same Wi-Fi network
- Check firewall allows UDP port 8888 and TCP port 8889
- Restart LocalSync: `localsync> exit` and relaunch

**Connection refused?**

- Verify recipient is logged into LocalSync
- Check firewall settings on both computers

**Slow transfer speeds?**

- Use `--no-compress` for already compressed files
- Check Wi-Fi signal strength

**Certificate errors?**

```bash
# Regenerate certificates
rm -rf ~/.localsync/certs/
localsync  # Certificates will auto-generate
```

### Debug Mode

```bash
# Run with verbose logging
localsync --debug

# Check network connectivity
localsync> ping 192.168.1.101
```

## 🏗️ Architecture

```
LocalSync Application
├── Authentication Module
├── Device Discovery Module (UDP Broadcast)
├── File Transfer Module (TCP/TLS)
├── Encryption Engine (AES-256 + SSL)
├── Compression Engine (ZLIB/LZMA)
├── Configuration System
└── User Interface (CLI)
```

### Network Protocols

- **Discovery**: UDP broadcast on port 8888
- **Transfer**: TCP with TLS on port 8889
- **Heartbeat**: 5-second device presence updates

## 🔒 Security Features

- **No Internet Exposure**: All traffic stays on local network
- **Certificate Pinning**: Self-signed certificates prevent MITM attacks
- **Password Hashing**: SHA-256 with salt for authentication
- **Optional File Encryption**: AES-256 for sensitive files
- **Checksum Verification**: Ensures file integrity
- **Acceptance Protocol**: Users must approve incoming transfers

## 📊 Performance

| File Size | Transfer Time  | With Compression |
| --------- | -------------- | ---------------- |
| 1 MB      | ~1-2 seconds   | ~0.5-1 second    |
| 100 MB    | ~20-30 seconds | ~10-15 seconds   |
| 1 GB      | ~3-4 minutes   | ~1.5-2 minutes   |

_Based on typical 802.11ac Wi-Fi speeds_

## 🚀 Use Cases

- **Enterprise Environments**: Secure internal file sharing
- **Educational Institutions**: Classroom file distribution
- **Creative Studios**: Large media file transfers
- **Offline Networks**: Air-gapped or restricted environments
- **Event Spaces**: Conference and workshop file sharing
- **Home Networks**: Quick family file transfers

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](https://github.com/yourusername/localsync/wiki)
- 🐛 [Issue Tracker](https://github.com/yourusername/localsync/issues)
- 💬 [Discussions](https://github.com/yourusername/localsync/discussions)
- 📧 Email: support@localsync.org

## 🙏 Acknowledgments

- Built with Python Standard Library for maximum compatibility
- Uses cryptography libraries for secure transfers
- Inspired by the need for simple, secure local file sharing

---

**LocalSync** - Because sometimes the simplest solutions are the most powerful. Transfer files securely, locally, and without the cloud.

- Built with Python Standard Library for maximum compatibility
- Uses cryptography libraries for secure transfers
- Inspired by the need for simple, secure local file sharing

---

**LocalSync** - Because sometimes the simplest solutions are the most powerful. Transfer files securely, locally, and without the cloud.
