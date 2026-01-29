"""Models and schema definitions for backend data structures"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, ConfigDict

from aind_dataverse_service_server import __version__


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: Literal["OK"] = "OK"
    service_version: str = __version__


class EntityTableRow(BaseModel):
    """Model of Entity Table Row"""

    model_config = ConfigDict(extra="ignore")

    entityid: Optional[str] = Field(default=None)
    entitysetname: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    logicalname: Optional[str] = Field(default=None)
