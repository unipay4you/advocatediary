from datetime import datetime
import jwt
import base64
import json
import hmac
import hashlib


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def get_jwt_secret_key_live():
    jwtkey = "UFMwMDE3Mzc5NDJmMDUxYzFhMTg0OWM2NDk2OTk4Y2I5MGYyOWIy"
    partnerId = "PS00173"
    timestamp = int(datetime.now().timestamp())

    # Header
    header = {'alg': 'HS256', 'typ': 'JWT'}
    encoded_header = base64url_encode(json.dumps(header).encode())

    # Payload
    payload = {
        'timestamp': timestamp,
        'partnerId': partnerId,
        'reqid': timestamp
    }

    encoded_payload = base64url_encode(json.dumps(payload).encode())

    # Signature
    message = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(jwtkey.encode(), message, hashlib.sha256).digest()
    encoded_signature = base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"



def get_jwt_secret_key_demo():
    jwtkey = "UFMwMDEyNGQ2NTliODUzYmViM2I1OWRjMDc2YWNhMTE2M2I1NQ=="
    auth_key = "MzNkYzllOGJmZGVhNWRkZTc1YTgzM2Y5ZDFlY2EyZTQ="
    partnerId = "PS001"
    timestamp = int(datetime.now().timestamp())

    # Header
    header = {'alg': 'HS256', 'typ': 'JWT'}
    encoded_header = base64url_encode(json.dumps(header).encode())

    # Payload
    payload = {
        'timestamp': timestamp,
        'partnerId': partnerId,
        'reqid': timestamp
    }

    encoded_payload = base64url_encode(json.dumps(payload).encode())

    # Signature
    message = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(jwtkey.encode(), message, hashlib.sha256).digest()
    encoded_signature = base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


