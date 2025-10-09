import ssl
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import datetime


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
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile, keyfile)
        return context
    
    @staticmethod
    def create_ssl_server_context(cert_dir):
        cert_dir = os.path.expanduser(cert_dir)
        os.makedirs(cert_dir, exist_ok=True)

        certfile = os.path.join(cert_dir, "cert.pem")
        keyfile = os.path.join(cert_dir, "key.pem")

        # Check if both cert and key exist
        if not (os.path.exists(certfile) and os.path.exists(keyfile)):
            # Use a lock to prevent duplicate generation in multithreaded start-up
            lock_file = os.path.join(cert_dir, ".cert_lock")
            if not os.path.exists(lock_file):
                open(lock_file, "w").close()
                print("🔐 SSL certificates not found, generating new ones...")
                CryptoManager._generate_self_signed_cert(certfile, keyfile)
                os.remove(lock_file)
            else:
                # Another thread is generating — wait briefly
                import time
                time.sleep(1)

        # ✅ Now safely load them
        return CryptoManager.create_ssl_context(certfile, keyfile)
    
    
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
    
    @staticmethod
    def _generate_self_signed_cert(certfile, keyfile):
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "NG"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Lagos"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "LocalSync"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "FileSync"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            )
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName("localhost")]),
                critical=False,
            )
            .sign(key, hashes.SHA256())
        )

        with open(certfile, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        with open(keyfile, "wb") as f:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )