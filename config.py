from pydantic_settings import BaseSettings





class Settings(BaseSettings):


    DEBUG_MODE: bool = True

    STATIC_DIR: str = "static"

    class Config:
        env_file = ".env"


config = Settings()