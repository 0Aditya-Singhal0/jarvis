from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.parse import quote


class ConfigurationError(ValueError):
    """Raised when an allow-listed configuration value is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    environment: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password_file: Path
    data_root: Path

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "Settings":
        values = os.environ if environment is None else environment

        def required(name: str) -> str:
            value = values.get(name, "").strip()
            if not value:
                raise ConfigurationError(f"{name} is required")
            return value

        port_text = required("JARVIS_DB_PORT")
        try:
            port = int(port_text)
        except ValueError as error:
            raise ConfigurationError("JARVIS_DB_PORT must be an integer") from error
        if not 1 <= port <= 65535:
            raise ConfigurationError("JARVIS_DB_PORT is outside the valid range")

        password_file = Path(required("JARVIS_DB_PASSWORD_FILE"))
        data_root = Path(required("JARVIS_DATA_ROOT"))
        if not password_file.is_absolute() or not data_root.is_absolute():
            raise ConfigurationError("secret and data paths must be absolute")

        return cls(
            environment=required("JARVIS_ENV"),
            db_host=required("JARVIS_DB_HOST"),
            db_port=port,
            db_name=required("JARVIS_DB_NAME"),
            db_user=required("JARVIS_DB_USER"),
            db_password_file=password_file,
            data_root=data_root,
        )

    def database_url(self) -> str:
        password = self.read_database_password()
        return (
            "postgresql+psycopg://"
            f"{quote(self.db_user, safe='')}:{quote(password, safe='')}"
            f"@{self.db_host}:{self.db_port}/{quote(self.db_name, safe='')}"
        )

    def read_database_password(self) -> str:
        try:
            value = self.db_password_file.read_text(encoding="utf-8")
        except OSError as error:
            raise ConfigurationError("database password file is unavailable") from error
        if value.endswith("\r\n"):
            value = value[:-2]
        elif value.endswith("\n"):
            value = value[:-1]
        if not value:
            raise ConfigurationError("database password file is empty")
        return value
