import hashlib

from jose import jwt
from datetime import datetime, timedelta

from models.inputs import User
from db.crud_operations import CRUDOperations


class AuthUtils:
    def __init__(self, config, crud_ops: CRUDOperations):
        self.SECRET_KEY = config.secret_key
        self.ALGORITHM = config.algorithm
        self.expires_delta = timedelta(minutes=config.auth_expiry)

        self.crud_ops = crud_ops

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + self.expires_delta

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def decode_token(self, token):
        decoded_data = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

        user = User(
            first_name=decoded_data["first_name"],
            last_name=decoded_data["last_name"],
            username=decoded_data["username"],
            email=decoded_data["email"],
        )

        return user

    @staticmethod
    def hash_value(value):
        m = hashlib.sha256()
        m.update(value.encode("utf-8"))
        m.digest()
        return m.hexdigest()
