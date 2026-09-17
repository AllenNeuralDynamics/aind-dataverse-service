"""Module for settings to connect to Dataverse backend"""

from typing import Optional

from aind_settings_utils.aws import (
    SecretsManagerBaseSettings,
)
from pydantic import Field, RedisDsn, SecretStr
from pydantic_settings import SettingsConfigDict


class Settings(SecretsManagerBaseSettings):
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
        description="The client ID for the Dataverse instance",
    )
    client_secret: SecretStr = Field(
        title="Dataverse Client Secret",
        description="The client secret for the Dataverse instance",
    )
    flow_scope: str = Field(
        default="https://service.flow.microsoft.com//.default",
        title="Power Platform/Flow Scope",
        description="The scope for the Dataverse instance",
    )
    host: Optional[str] = Field(
        default=None,
        title="Dataverse Host URL",
        description="The host URL for the Dataverse instance",
    )
    environment_url: str = Field(
        title="Dataverse Environment URL",
        description="The environment URL for the Dataverse instance",
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
    app_concurrency_limit: int = Field(
        default=16,
        description=(
            "Limit number of max API calls that can be made to Dataverse."
            "More than this number will sit in a queue."
        ),
    )


settings = Settings()
