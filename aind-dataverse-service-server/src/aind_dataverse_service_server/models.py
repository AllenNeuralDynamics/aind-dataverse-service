"""Models and schema definitions for backend data structures"""

from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict

from aind_dataverse_service_server import __version__


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: Literal["OK"] = "OK"
    service_version: str = __version__


class ProjectsTableRow(BaseModel):
    """Model of Projects Table Row"""
    model_config = ConfigDict(extra='ignore')

    cr138_projectcode: Optional[str] = Field(default=None)
    cr138_projectid: Optional[str] = Field(default=None)
    cr138_projectlimsid: Optional[str] = Field(default=None)
    cr138_projectname: Optional[str] = Field(default=None)
