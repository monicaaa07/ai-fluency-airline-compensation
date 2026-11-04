"""Settings come from environment variables; nothing else reads os.environ."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_path: str = "airline.db"
    seed_demo_data: bool = True
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=os.environ.get("AIRLINE_DB_PATH", "airline.db"),
            seed_demo_data=os.environ.get("AIRLINE_SEED_DEMO_DATA", "1") == "1",
            log_level=os.environ.get("AIRLINE_LOG_LEVEL", "INFO"),
        )
