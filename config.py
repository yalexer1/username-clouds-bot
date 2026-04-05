import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    BOT_TOKEN: str
    API_ID: int
    API_HASH: str
    SESSION_STRING: str = ""
    ADMIN_IDS: str = ""
    FRAGMENT_BASE_URL: str = "https://fragment.com/username"
    WORKER_SLEEP: int = 5
    MT_PROTO_DELAY: float = 0.5
    BEAUTY_SCORE_THRESHOLD: int = 20   # снизил с 70 до 20
    LIMIT_PER_REQUEST: int = 10

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()