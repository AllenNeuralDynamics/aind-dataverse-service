"""Module for settings to connect to Dataverse backend"""

from typing import Optional

from aind_settings_utils.aws import (
    ParameterStoreAppBaseSettings,
)
from pydantic import Field, SecretStr, RedisDsn
from pydantic_settings import SettingsConfigDict


class Settings(ParameterStoreAppBaseSettings):
    """Settings needed to connect to Dataverse"""

    model_config = SettingsConfigDict(
        env_prefix="DATAVERSE_", case_sensitive=False
    )
    tenant_id: str = Field()
    client_id: str = Field()
    client_secret: SecretStr = Field()
    scope: str = Field(default="https://service.flow.microsoft.com//.default")
    host: Optional[str] = Field(default=None)
    api_version: int = Field(default=1)
    project_table_id: str = Field("cr138_projects")
    redis_url: Optional[RedisDsn] = Field(default=None)


settings = Settings()
