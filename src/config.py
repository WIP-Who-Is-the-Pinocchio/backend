from pydantic import MySQLDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MysqlSettings(BaseSettings):
    db_protocol: str = Field(default="mysql+pymysql", env="DB_PROTOCOL")
    db_user: str = Field(default="root", env="DB_USER")
    db_password: str = Field(default="todos", env="DB_PASSWORD")
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=3306, env="DB_PORT")
    database_name: str = Field(default="pinocchio", env="DB_NAME")
    echo: bool = Field(default=True, env="DB_ECHO")


class Settings(BaseSettings, case_sensitive=True):
    model_config = SettingsConfigDict(validate_default=True)

    protocol: str = Field(default="http", env="PROTOCOL")
    host: str = Field(default="localhost", env="HOST")
    port: int = Field(default=2309, env="PORT")
    mysql_settings: MysqlSettings = MysqlSettings()
    mysql_dsn: MySQLDsn = f"{mysql_settings.db_protocol}://{mysql_settings.db_user}:{mysql_settings.db_password}@{mysql_settings.db_host}:{mysql_settings.db_port}/{mysql_settings.database_name}"
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_secret_key: str = Field(
        default="wip-access-secret", env="ACCESS_TOKEN_SECRET_KEY"
    )
    access_token_exp: int = Field(default=60, env="ACCESS_TOKEN_EXP")
    refresh_token_secret_key: str = Field(
        default="wip-refresh-secret", env="REFRESH_TOKEN_SECRET_KEY"
    )
    refresh_token_exp: int = Field(default=1440, env="REFRESH_TOKEN_EXP")


settings = Settings()
