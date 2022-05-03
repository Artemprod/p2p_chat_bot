from pydantic import BaseSettings, Field


class Secrets(BaseSettings):
    token: str = Field(..., env="TOKEN")
    bd_password: str = Field(..., env="DB_PASSWORD")
    bd_host: str = Field(..., env="DB_HOST")
    bd_port: int = Field(..., env="DB_PORT")
    bd_user: str = Field(default="postgres", env="DB_USER")


SECRETS = Secrets()
