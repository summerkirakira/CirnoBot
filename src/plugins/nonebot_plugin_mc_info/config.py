from pydantic import BaseSettings
import os

current_folder = os.path.dirname(__file__)


class Config(BaseSettings):

    class Config:
        extra = "ignore"
