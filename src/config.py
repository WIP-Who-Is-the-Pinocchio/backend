import os

from pydantic import MySQLDsn, Field, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MysqlSettings(BaseSettings):
    db_protocol: str = os.getenv("DB_PROTOCOL")
    db_user: str = os.getenv("DB_USER")
    db_password: str = os.getenv("DB_PASSWORD")
    db_host: str = os.getenv("DB_HOST")
    db_port: int = os.getenv("DB_PORT")
    database_name: str = os.getenv("DB_NAME")
    echo: bool = os.getenv("DB_ECHO")


class RedisSettings(BaseSettings):
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    auth_num_db: int = Field(default=0, env="AUTH_NUM_DB")


class Settings(BaseSettings):
    protocol: str = os.getenv("PROTOCOL")
    host: str = os.getenv("HOST")
    port: int = os.getenv("PORT")
    mysql_settings: MysqlSettings = MysqlSettings()
    mysql_dsn: MySQLDsn = f"{mysql_settings.db_protocol}://{mysql_settings.db_user}:{mysql_settings.db_password}@{mysql_settings.db_host}:{mysql_settings.db_port}/{mysql_settings.database_name}"
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    access_token_secret_key: str = os.getenv("ACCESS_TOKEN_SECRET_KEY")
    access_token_exp: int = os.getenv("ACCESS_TOKEN_EXP")
    refresh_token_secret_key: str = os.getenv("REFRESH_TOKEN_SECRET_KEY")
    refresh_token_exp: int = os.getenv("REFRESH_TOKEN_EXP")
    sender_gmail: EmailStr = os.getenv("SENDER_GMAIL")
    gmail_password: str = os.getenv("GMAIL_PASSWORD")
    redis_settings: RedisSettings = RedisSettings()

    model_config = SettingsConfigDict(validate_default=False)


settings = Settings()
