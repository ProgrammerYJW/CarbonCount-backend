from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_username: str = "ShuTanUser"
    database_password: str = "STuser1234!"
    database_host: str = "118.178.179.237"
    database_port: int = 3306
    database_name: str = "CarbonCountTestDB"

    class Config:
        env_file = ".env"  # 可选，从.env文件加载


settings = Settings()
