from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    lumen_data_dir: str = "."
    duckdb_path: str | None = None
    demo_mode: bool = False
    transaction_reset_key: str | None = None
    # Explicitly opt-in trial controls for a live Incident demo. This is kept
    # distinct from DEMO_MODE, which intentionally swaps Incident reads for
    # fixtures and therefore cannot prove the persisted pipeline.
    demo_live_trials_enabled: bool = False

    cors_allowed_origins: str = ""

    neo4j_uri: str | None = None
    neo4j_user: str | None = None
    neo4j_password: str | None = None
    neo4j_database: str = "neo4j"

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-sol"
    openai_reasoning_effort: Literal["none", "low", "medium", "high", "xhigh", "max"] = "medium"
    openai_timeout_seconds: float = 20.0

    @field_validator("demo_mode", "demo_live_trials_enabled", mode="before")
    @classmethod
    def blank_feature_flags_are_disabled(cls, value: object) -> object:
        """Treat empty deployment placeholders as the explicit safe default."""

        return False if isinstance(value, str) and not value.strip() else value

    @model_validator(mode="after")
    def default_duckdb_path_to_data_dir(self) -> "Settings":
        if self.duckdb_path is None:
            self.duckdb_path = str(Path(self.lumen_data_dir) / "lumen.duckdb")
        return self

    @property
    def cors_origins(self) -> tuple[str, ...]:
        """Parse the explicit browser-origin allowlist without accepting wildcards."""
        origins = tuple(origin.strip().rstrip("/") for origin in self.cors_allowed_origins.split(",") if origin.strip())
        if "*" in origins:
            raise ValueError("CORS_ALLOWED_ORIGINS must not contain '*'")
        parsed = [urlsplit(origin) for origin in origins]
        if any(
            item.scheme not in {"https", "http"}
            or not item.netloc
            or item.path
            or item.query
            or item.fragment
            for item in parsed
        ):
            raise ValueError("CORS_ALLOWED_ORIGINS must contain absolute HTTP(S) origins")
        return origins


settings = Settings()
