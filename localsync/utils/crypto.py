import ssl
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoManager:
    @staticmethod
    def generate_ssl_certificates(common_name, cert_path="certs/", days_valid=365):
        try:
            from OpenSSL import crypto
            
            key = crypto.PKey()
            key.generate_key(crypto.TYPE_RSA, 2048)
            
            cert = crypto.X509()
            cert.get_subject().CN = common_name
            cert.set_serial_number(1000)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(days_valid * 24 * 60 * 60)
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(key)
            cert.sign(key, 'sha256')
            
            os.makedirs(cert_path, exist_ok=True)
            with open(os.path.join(cert_path, "server.crt"), "wb") as f:
                f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            with open(os.path.join(cert_path, "server.key"), "wb") as f:
                f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
                
            return True
        except ImportError:
            return False
    
    @staticmethod
    def create_ssl_context(certfile, keyfile):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile, keyfile)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    
    @staticmethod
    def create_ssl_client_context():
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    
    @staticmethod
    def derive_key(password: str, salt: bytes = None) -> tuple:
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
        key, salt = CryptoManager.derive_key(password)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)
        return salt + encrypted
    
    @staticmethod
    def decrypt_data(encrypted_data: bytes, password: str) -> bytes:
        salt = encrypted_data[:16]
        encrypted = encrypted_data[16:]
        key, _ = CryptoManager.derive_key(password, salt)
        fernet = Fernet(key)
        return fernet.decrypt(encrypted)