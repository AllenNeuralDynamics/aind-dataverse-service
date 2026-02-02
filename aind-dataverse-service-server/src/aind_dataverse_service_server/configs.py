"""Module for settings to connect to Dataverse backend"""

from typing import Optional

from aind_settings_utils.aws import (
    ParameterStoreAppBaseSettings,
)
from pydantic import Field, RedisDsn, SecretStr
from pydantic_settings import SettingsConfigDict


class Settings(ParameterStoreAppBaseSettings):
    """Settings needed to connect to Dataverse"""

    model_config = SettingsConfigDict(
        env_prefix="DATAVERSE_", case_sensitive=False
    )
    tenant_id: str = Field(
        title="Dataverse Tenant ID",
        description="The tenant ID for the Dataverse instance",
    )
    client_id: str = Field(
        title="Dataverse Client ID",
        description="The client ID for authenticating to the Dataverse instance",
    )
    client_secret: SecretStr = Field(
        title="Dataverse Client Secret",
        description="The client secret for authenticating to the Dataverse instance",
    )
    scope: str = Field(
        default="https://service.flow.microsoft.com//.default",
        title="Dataverse Scope",
        description="The scope for authenticating to the Dataverse instance",
    )
    host: Optional[str] = Field(
        default=None,
        title="Dataverse Host URL",
        description="The host URL for the Dataverse instance",
    )
    api_version: int = Field(
        default=1,
        title="Dataverse API Version",
        description="The API version for the Dataverse instance",
    )
    redis_url: Optional[RedisDsn] = Field(
        default=None,
        title="Redis URL",
        description="The Redis URL for caching",
    )


settings = Settings()
