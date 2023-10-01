import bcrypt

from config import settings


class AuthManager:
    encoding: str = "UTF-8"
    jwt_algorithm: str = "HS256"
    secret_key: str = settings.secret_key

    def hash_password(self, plain_password: str) -> str:
        hashed_password: bytes = bcrypt.hashpw(
            plain_password.encode(self.encoding), salt=bcrypt.gensalt()
        )
        return hashed_password.decode(self.encoding)
