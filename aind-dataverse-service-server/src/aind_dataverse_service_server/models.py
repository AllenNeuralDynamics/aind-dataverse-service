"""Models and schema definitions for backend data structures"""

from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

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


class WaterRestrictionModel(BaseModel):
    """Response model for the Water Restriction API"""

    model_config = ConfigDict(coerce_numbers_to_str=True)
    mouse_id: str | None = Field(..., title="Mouse ID")
    protocol_id: str | None = Field(default=None, title="IACUC Protocol ID")
    record_name: str | None = Field(default=None, title="Record Name")
    active_record: bool | None = Field(default=None, title="Active Record")
    baseline_weight: Decimal | None = Field(
        default=None, title="Baseline Weight"
    )
    last_watered_datetime: datetime | None = Field(
        default=None, title="Last Watered Datetime"
    )
    low_weight_threshold: Decimal | None = Field(
        default=None, title="Low Weight Threshold"
    )
    target_weight: Decimal | None = Field(default=None, title="Target Weight")
    targeted_weight_percentage: Decimal | None = Field(
        default=None, title="Targeted Weight Percentage"
    )
    water_restriction_status: str | None = Field(
        default=None, title="Water Restriction Status"
    )
    change_date_time: datetime | None = Field(
        default=None, title="Change Date Time"
    )
    new_value: str | None = Field(default=None, title="New Value")
    old_value: str | None = Field(default=None, title="Old Value")


class HistologyReagentModel(BaseModel):
    """A reagent used in a histology wash"""

    name: str | None = Field(default=None, title="Name")
    source: str | None = Field(default=None, title="Source")
    lot_number: str | None = Field(default=None, title="Lot Number")


class HistologyWashModel(BaseModel):
    """A wash step in a histology procedure"""

    wash_name: str | None = Field(default=None, title="Wash Name")
    wash_type: str | None = Field(default=None, title="Wash Type")
    start_time: AwareDatetime | None = Field(default=None, title="Start Time")
    end_time: AwareDatetime | None = Field(default=None, title="End Time")
    modified_by: str | None = Field(default=None, title="Modified By")
    reagents: List[HistologyReagentModel] = Field(
        default_factory=list, title="Reagents"
    )


class HistologyModel(BaseModel):
    """Response model for the Histology API"""

    procedure_name: str | None = Field(default=None, title="Procedure Name")
    experiment_run_created_on: AwareDatetime | None = Field(
        default=None, title="Experiment Run Created On"
    )
    specimen_id: str | None = Field(default=None, title="Specimen ID")
    subject_id: str | None = Field(default=None, title="Subject ID")
    protocol_id: str | None = Field(default=None, title="Protocol ID")
    protocol_name: str | None = Field(default=None, title="Protocol Name")
    washes: List[HistologyWashModel] = Field(
        default_factory=list, title="Washes"
    )
