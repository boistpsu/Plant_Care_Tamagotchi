from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import os
import socket

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CERT_DIR = os.path.join(BASE_DIR, "pki", "own", "certs")
KEY_DIR = os.path.join(BASE_DIR, "pki", "own", "private")

os.makedirs(CERT_DIR, exist_ok=True)
os.makedirs(KEY_DIR, exist_ok=True)

# OPC UA Application URI (MUST match server)
APPLICATION_URI = "urn:freeopcua:python:client"

HOSTNAME = socket.gethostname()

# Generate private key
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, "FreeOpcUa Python Server"),
])

san = x509.SubjectAlternativeName([
    # OPC UA requires Application URI here
    x509.UniformResourceIdentifier(APPLICATION_URI),

    # Hostname(s)
    x509.DNSName(HOSTNAME),
    x509.DNSName("localhost"),
])

cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(datetime.utcnow() + timedelta(days=365))
    .add_extension(san, critical=False)
    .add_extension(
    x509.BasicConstraints(ca=False, path_length=None),
    critical=True
    )
    .sign(key, hashes.SHA256())
)

# Write private key (PEM)
with open(os.path.join(KEY_DIR, "client_key.pem"), "wb") as f:
    f.write(
        key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
        )
    )

# Write certificate (DER)
with open(os.path.join(CERT_DIR, "client_cert.der"), "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.DER))

print("✅ OPC UA–compliant server certificate generated")
print(" Application URI:", APPLICATION_URI)
print(" Hostname:", HOSTNAME)