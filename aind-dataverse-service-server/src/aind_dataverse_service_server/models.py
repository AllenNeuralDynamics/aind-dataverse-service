"""Models and schema definitions for backend data structures"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

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


class FundingModel(BaseModel):
    """Response model for the Funding API"""

    project_name: str | None = Field(default=None, title="Project Name")
    subproject: str | None = Field(default=None, title="Subproject")
    project_code: str | None = Field(default=None, title="Project Code")
    funding_institution: str | None = Field(
        default=None, title="Funding Institution"
    )
    grant_number: str | None = Field(default=None, title="Grant Number")
    fundees: str | None = Field(default=None, title="Fundees (PI)")
    investigators: str | None = Field(default=None, title="Investigators")
    model_config = ConfigDict(populate_by_name=True)
