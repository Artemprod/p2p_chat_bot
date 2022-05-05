from pydantic import BaseSettings, Field


class Secrets(BaseSettings):
    token: str = Field(..., env="TOKEN")
    bd_password: str = Field(..., env="DB_PASSWORD")
    bd_host: str = Field(default="127.0.0.1", env="DB_HOST")
    bd_port: int = Field(default=5432, env="DB_PORT")
    bd_user: str = Field(default="postgres", env="DB_USER")
    database: str = Field(default="ChatBot_p2_delivery", env="DATABASE_NAME")


SECRETS = Secrets(token = '5193936594:AAESI-SFziCVSzSnl7b7Zz3leB7swYNwL08', bd_password='Portnov1991')
