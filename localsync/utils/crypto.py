import ssl
import socket
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class CryptoManager:
    @staticmethod
    def generate_ssl_certificates(common_name, cert_path="certs/", days_valid=365):
        """Generate self-signed SSL certificates for secure communication"""
        from OpenSSL import crypto
        
        # Create key pair
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        
        # Create certificate
        cert = crypto.X509()
        cert.get_subject().CN = common_name
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(days_valid * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha256')
        
        # Save certificate and key
        with open(os.path.join(cert_path, "server.crt"), "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(os.path.join(cert_path, "server.key"), "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
            
        return True
    
    @staticmethod
    def create_ssl_context(certfile, keyfile):
        """Create SSL context for secure connections"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile, keyfile)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    
    @staticmethod
    def create_ssl_client_context():
        """Create SSL context for client connections"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    
    @staticmethod
    def derive_key(password: str, salt: bytes = None) -> tuple:
        """Derive encryption key from password using PBKDF2"""
        if salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    @staticmethod
    def encrypt_data(data: bytes, password: str) -> bytes:
        """Encrypt data with password-derived key"""
        key, salt = CryptoManager.derive_key(password)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)
        return salt + encrypted
    
    @staticmethod
    def decrypt_data(encrypted_data: bytes, password: str) -> bytes:
        """Decrypt data with password-derived key"""
        salt = encrypted_data[:16]
        encrypted = encrypted_data[16:]
        key, _ = CryptoManager.derive_key(password, salt)
        fernet = Fernet(key)
        return fernet.decrypt(encrypted)