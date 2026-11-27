"""Module to handle query logic and responses. Note that the Dataverse SQL API
is read-only and has protections against injection attacks. The histology
and imaging queries are expressed as FetchXML, the SDK's supported way to
express JOINs.
"""

from datetime import datetime, timezone
from xml.sax.saxutils import quoteattr

funding_sql_query = """
SELECT
    p.cr138_project as project_name,
    p.cr138_sub_project as subproject,
    u1.fullname as investigators,
    fc.cr138_grant as grant_number,
    u2.fullname as fundees,
    fc.cr138_funding_code as project_code,
    fi.aibs_institutionname as funding_institution
FROM cr138_funding_codes fc
LEFT JOIN cr138_projects_cr138_funding_codes pfc
    ON fc.cr138_funding_codesid = pfc.cr138_funding_codesid
LEFT JOIN cr138_projects p
    ON pfc.cr138_projectsid = p.cr138_projectsid
LEFT JOIN cr138_projects_systemuser pu
    ON p.cr138_projectsid = pu.cr138_projectsid
LEFT JOIN systemuser u1
    ON pu.systemuserid = u1.systemuserid
LEFT JOIN aibs_funding_institution fi
    ON fc.cr138_funding_institution = fi.aibs_funding_institutionid
LEFT JOIN cr138_funding_codes_systemuser fcu
    ON fc.cr138_funding_codesid = fcu.cr138_funding_codesid
LEFT JOIN systemuser u2
    ON fcu.systemuserid = u2.systemuserid
"""


def water_restriction_sql_query(mouse_id: str) -> str:
    """
    Generates query used to gather water restriction data for a mouse.
    Parameters
    ----------
    mouse_id : str

    Returns
    -------
    str

    """
    return f"""
    SELECT
      m.aibs_mouse_id AS mouse_id,
      p.aibs_protocol_id AS protocol_id,
      w.aibs_record_name AS record_name,
      w.aibs_active_record AS active_record,
      w.aibs_baseline_weight AS baseline_weight,
      w.aibs_last_watered_datetime AS last_watered_datetime,
      w.aibs_low_weight_threshold AS low_weight_threshold,
      w.aibs_target_weight AS target_weight,
      w.aibs_targeted_weight_percentage AS targeted_weight_percentage,
      w.aibs_water_restriction_status AS water_restriction_status,
      c.aibs_change_date_time as change_date_time,
      c.aibs_new_value AS new_value,
      c.aibs_old_value AS old_value
    FROM aibs_dim_mice m
    LEFT JOIN aibs_dim_iacuc_protocols p
      ON p.aibs_dim_iacuc_protocolsid = m.aibs_iacuc_protocol
    INNER JOIN aibs_fact_mouse_water_restriction w
      ON w.aibs_mouse_id = m.aibs_dim_miceid
    INNER JOIN aibs_fact_mouse_water_restriction_change_log c
      ON c.aibs_mouse_id = m.aibs_dim_miceid
      AND (c.aibs_new_value = 'active water restriction'
      OR c.aibs_old_value = 'active water restriction')
    WHERE m.aibs_mouse_id = '{mouse_id}'
    """


DELIPIDATION_PROCEDURE = "SmartSPIM Delipidation"
RI_MATCHING_PROCEDURE = "SmartSPIM Refractive Index Matching"

# ``cr138_delipidationbatchmembership.cr138_membershipstatus`` code for a
# specimen that was removed from the batch.
MEMBERSHIP_STATUS_REMOVED = 2

# Batch steps whose ``cr138_stepkey`` starts with one of these belong to
# refractive index matching. Every other step belongs to delipidation.
RI_MATCHING_STEP_KEY_PREFIXES = ("ri-", "embedding")

# Labels of the ``cr138_delipidationbatchstep.cr138_washtype`` choice column.
# FetchXML returns only the numeric code, so unknown codes are returned as the
# code itself.
WASH_TYPE_LABELS = {
    1: "Shield Off",
    2: "Shield On",
    3: "Passive Delipidation",
    4: "Active Delipidation",
    5: "Refractive Index Wash #1",
    6: "Refractive Index Wash #2",
    7: "Embedding",
}


def _to_utc_iso(d: datetime) -> str:
    """
    Convert a datetime to an ISO string in UTC.

    Parameters
    ----------
    d : datetime
        The datetime. Naive times are treated as UTC.

    Returns
    -------
    str
        The ISO-formatted UTC datetime.
    """
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).isoformat()


def _fetchxml_filters(
    subject_attribute: str,
    date_attribute: str,
    subject_id: str,
    start_date_gte: datetime | None,
    end_date_lte: datetime | None,
) -> tuple[str, str]:
    """
    Build the subject filter and the optional date filter for the FetchXML
    queries.

    Parameters
    ----------
    subject_attribute : str
        The attribute holding the mouse ID.
    date_attribute : str
        The attribute the date range is applied to.
    subject_id : str
        Only return this mouse. It is XML-escaped before being embedded.
    start_date_gte : datetime | None
        Only return records created on or after this time. Naive times are
        treated as UTC.
    end_date_lte : datetime | None
        Only return records created on or before this time. Naive times are
        treated as UTC.

    Returns
    -------
    tuple[str, str]
        The subject filter and the date filter. The date filter is empty when
        no date is given.
    """
    subject_filter = (
        f'<filter><condition attribute="{subject_attribute}" operator="eq" '
        f"value={quoteattr(subject_id)} /></filter>"
    )
    conditions = [
        f'<condition attribute="{date_attribute}" operator="{operator}" '
        f'value="{_to_utc_iso(d)}" />'
        for operator, d in (("ge", start_date_gte), ("le", end_date_lte))
        if d is not None
    ]
    date_filter = (
        f"<filter>{''.join(conditions)}</filter>" if conditions else ""
    )
    return subject_filter, date_filter


def delipidation_fetchxml(
    subject_id: str,
    start_date_gte: datetime | None = None,
    end_date_lte: datetime | None = None,
) -> str:
    """
    Generate FetchXML that gathers the batch steps each specimen went through.

    Returns one row per specimen, batch step, step reagent lot and step
    participant. Removed batch memberships are excluded. The date range is
    applied to the batch's ``createdon``.

    Parameters
    ----------
    subject_id : str
        Only return this mouse.
    start_date_gte : datetime | None
        Only return batches created on or after this time.
    end_date_lte : datetime | None
        Only return batches created on or before this time.

    Returns
    -------
    str
        The FetchXML query string.
    """
    subject_filter, date_filter = _fetchxml_filters(
        "cr138_aibsmouseregistry",
        "createdon",
        subject_id,
        start_date_gte,
        end_date_lte,
    )
    return f"""
<fetch>
  <entity name="aibs_reagentwash">
    <order attribute="aibs_reagentwashid" />
    <attribute name="aibs_reagentwashid" alias="reagent_wash_id" />
    <attribute name="cr138_aibsmouseregistry" alias="subject_id" />
    {subject_filter}
    <link-entity name="cr138_delipidationbatchmembership"
                 from="cr138_reagentwash" to="aibs_reagentwashid"
                 link-type="inner" alias="m">
      <attribute name="cr138_aibsmouseregistry" alias="specimen_id" />
      <filter>
        <condition attribute="cr138_removedon" operator="null" />
        <condition attribute="cr138_membershipstatus" operator="ne"
                   value="{MEMBERSHIP_STATUS_REMOVED}" />
      </filter>
      <link-entity name="cr138_batch"
                   from="cr138_batchid" to="cr138_batch"
                   link-type="inner" alias="b">
        <attribute name="cr138_batchid" alias="batch_id" />
        <attribute name="cr138_batchnumber" alias="batch_number" />
        <attribute name="createdon" alias="batch_created_on" />
        {date_filter}
        <link-entity name="cr138_delipidationbatchstep"
                     from="cr138_batch" to="cr138_batchid"
                     link-type="outer" alias="s">
          <attribute name="cr138_delipidationbatchstepid" alias="step_id" />
          <attribute name="cr138_delipidationbatchstepname"
                     alias="step_name" />
          <attribute name="cr138_stepkey" alias="step_key" />
          <attribute name="cr138_sequence" alias="step_sequence" />
          <attribute name="cr138_washtype" alias="wash_type" />
          <attribute name="cr138_startdate" alias="start_time" />
          <attribute name="cr138_enddate" alias="end_time" />
          <attribute name="cr138_notes" alias="notes" />
          <link-entity name="systemuser"
                       from="systemuserid" to="cr138_completedby"
                       link-type="outer" alias="u">
            <attribute name="fullname" alias="modified_by" />
          </link-entity>
          <link-entity name="cr138_delipidationstepreagentlot"
                       from="cr138_delipidationbatchstep"
                       to="cr138_delipidationbatchstepid"
                       link-type="outer" alias="sl">
            <attribute name="cr138_delipidationstepreagentlotid"
                       alias="step_lot_id" />
            <attribute name="cr138_usagerole" alias="lot_usage_role" />
            <attribute name="cr138_displayorder" alias="lot_display_order" />
            <link-entity name="cr138_reagentlot"
                         from="cr138_reagentlotid" to="cr138_reagentlot"
                         link-type="outer" alias="l">
              <attribute name="cr138_lotnumber" alias="lot_number" />
              <link-entity name="cr138_aibsreagents"
                           from="cr138_aibsreagentsid"
                           to="cr138_aibsreagent"
                           link-type="outer" alias="r">
                <attribute name="cr138_name" alias="reagent_name" />
                <attribute name="cr138_vendor" alias="reagent_source" />
              </link-entity>
            </link-entity>
          </link-entity>
          <link-entity name="cr138_delipidationstepparticipant"
                       from="cr138_delipidationbatchstep"
                       to="cr138_delipidationbatchstepid"
                       link-type="outer" alias="p">
            <attribute name="cr138_reagentwash"
                       alias="participant_reagent_wash_id" />
          </link-entity>
        </link-entity>
      </link-entity>
    </link-entity>
  </entity>
</fetch>
"""


def _step_to_wash(
    step: dict[str, object], batch_number: object
) -> tuple[str, int, dict[str, object]]:
    """
    Convert a delipidation batch step into a wash.

    Parameters
    ----------
    step : dict[str, object]
        The step, with its first ``row`` and its reagent ``lots``.
    batch_number : object
        The batch number, which is stripped from the start of the step name.

    Returns
    -------
    tuple[str, int, dict[str, object]]
        The procedure the step belongs to, its sequence and the wash.
    """
    row = step["row"]
    lots = sorted(
        step["lots"].values(),
        key=lambda lot: (
            lot.get("lot_usage_role") or 0,
            lot.get("lot_display_order") or 0,
        ),
    )
    procedure = (
        RI_MATCHING_PROCEDURE
        if (row.get("step_key") or "").startswith(
            RI_MATCHING_STEP_KEY_PREFIXES
        )
        else DELIPIDATION_PROCEDURE
    )
    wash_type = row.get("wash_type")
    wash = {
        "wash_name": (row.get("step_name") or "").removeprefix(
            f"{batch_number} - "
        )
        or None,
        "wash_type": (
            None
            if wash_type is None
            else WASH_TYPE_LABELS.get(wash_type, str(wash_type))
        ),
        "start_time": row.get("start_time"),
        "end_time": row.get("end_time"),
        "modified_by": row.get("modified_by"),
        "notes": row.get("notes"),
        "reagents": [
            {
                "name": lot.get("reagent_name"),
                "source": lot.get("reagent_source"),
                "lot_number": lot.get("lot_number"),
            }
            for lot in lots
        ],
    }
    return procedure, row.get("step_sequence") or 0, wash


def _index_delipidation_rows(
    rows: list[dict[str, object]],
) -> tuple[dict[tuple, dict[str, object]], dict[object, dict[str, object]]]:
    """
    Index the joined delipidation rows by run and by batch step.

    Parameters
    ----------
    rows : list[dict[str, object]]
        The flat rows returned by ``delipidation_fetchxml``.

    Returns
    -------
    tuple[dict[tuple, dict[str, object]], dict[object, dict[str, object]]]
        The runs, keyed by reagent wash and batch, each with its first
        ``row`` and its ``step_ids`` in first-seen order; and the steps,
        keyed by step ID, each with its first ``row``, its reagent ``lots``
        and its ``participants``.
    """
    runs: dict[tuple, dict[str, object]] = {}
    steps: dict[object, dict[str, object]] = {}
    for row in rows:
        run = runs.setdefault(
            (row["reagent_wash_id"], row["batch_id"]),
            {"row": row, "step_ids": []},
        )
        step_id = row.get("step_id")
        if step_id is None:
            continue
        if step_id not in run["step_ids"]:
            run["step_ids"].append(step_id)
        step = steps.setdefault(
            step_id, {"row": row, "lots": {}, "participants": set()}
        )
        if row.get("step_lot_id") is not None:
            step["lots"][row["step_lot_id"]] = row
        if row.get("participant_reagent_wash_id") is not None:
            step["participants"].add(row["participant_reagent_wash_id"])
    return runs, steps


def group_delipidation_rows(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """
    Collapse the joined delipidation rows into one record per specimen, batch
    and procedure.

    Steps are split into delipidation and refractive index matching by their
    step key. A step with participants only applies to those specimens; a step
    without them applies to every specimen in the batch. The specimen ID is
    the batch membership's mouse ID, falling back to the subject ID.

    Parameters
    ----------
    rows : list[dict[str, object]]
        The flat rows returned by ``delipidation_fetchxml``.

    Returns
    -------
    list[dict[str, object]]
        Records shaped like ``HistologyModel``, with washes ordered by step
        sequence.
    """
    runs, steps = _index_delipidation_rows(rows)
    records = []
    for (reagent_wash_id, _), run in runs.items():
        washes: dict[str, list[tuple]] = {
            DELIPIDATION_PROCEDURE: [],
            RI_MATCHING_PROCEDURE: [],
        }
        for step_id in run["step_ids"]:
            step = steps[step_id]
            if (
                step["participants"]
                and reagent_wash_id not in step["participants"]
            ):
                continue
            procedure, sequence, wash = _step_to_wash(
                step, run["row"]["batch_number"]
            )
            washes[procedure].append((sequence, wash))
        for procedure, procedure_washes in washes.items():
            if procedure_washes:
                records.append(
                    {
                        "procedure_name": procedure,
                        "experiment_run_created_on": run["row"][
                            "batch_created_on"
                        ],
                        "subject_id": run["row"].get("subject_id"),
                        "specimen_id": run["row"].get("specimen_id")
                        or run["row"].get("subject_id"),
                        "washes": [
                            w
                            for _, w in sorted(
                                procedure_washes, key=lambda w: w[0]
                            )
                        ],
                    }
                )
    return records


# ``aibs_wholebrainimaging.cr138_taskstatus`` code for a finished imaging
# session. Records with other statuses haven't been imaged yet.
IMAGING_STATUS_COMPLETE = 8

# Labels of the ``aibs_wholebrainimaging`` choice columns. FetchXML returns
# only the numeric code, so unknown codes are returned as the code itself.
CHAMBER_IMMERSION_MEDIUM_LABELS = {
    2: "Cargille oil",
    3: "diH2O",
    4: "Ethyl cinnamate",
    5: "Optiplex and DMSO",
}
SAMPLE_IMMERSION_MEDIUM_LABELS = {1: "EasyIndex", 2: "Ethyl cinnamate"}
INSTRUMENT_NICKNAME_LABELS = {
    1: "Heffer",
    2: "Rocko",
    3: "Spunky",
    4: "Rocko or Spunky",
}

# The orientation image is named like ``Horizontal_IPR.png``. Its letters give
# the z, y and x axes in that order, each naming the side the axis points to.
AXIS_DIRECTIONS = {
    "L": "Right_to_left",
    "R": "Left_to_right",
    "A": "Posterior_to_anterior",
    "P": "Anterior_to_posterior",
    "S": "Inferior_to_superior",
    "I": "Superior_to_inferior",
}


def imaging_fetchxml(
    subject_id: str,
    start_date_gte: datetime | None = None,
    end_date_lte: datetime | None = None,
) -> str:
    """
    Generate FetchXML that gathers the completed SmartSPIM imaging sessions
    of a mouse.

    Returns one row per whole brain imaging record, newest first. The date
    range is applied to its ``createdon``.

    Parameters
    ----------
    subject_id : str
        Only return this mouse.
    start_date_gte : datetime | None
        Only return records created on or after this time.
    end_date_lte : datetime | None
        Only return records created on or before this time.

    Returns
    -------
    str
        The FetchXML query string.
    """
    subject_filter, date_filter = _fetchxml_filters(
        "cr138_aibsmouseregistry",
        "createdon",
        subject_id,
        start_date_gte,
        end_date_lte,
    )
    return f"""
<fetch>
  <entity name="aibs_wholebrainimaging">
    <order attribute="createdon" descending="true" />
    <attribute name="createdon" alias="experiment_run_created_on" />
    <attribute name="cr138_aibsmouseregistry" alias="subject_id" />
    <attribute name="aibs_brainid" alias="specimen_id" />
    <attribute name="aibs_performeddate" alias="date_performed" />
    <attribute name="aibs_chamberimmersionmedium"
               alias="chamber_immersion_medium" />
    <attribute name="aibs_sampleimmersionmedium"
               alias="sample_immersion_medium" />
    <attribute name="cr138_chamberrefractiveindex"
               alias="chamber_refractive_index" />
    <attribute name="cr138_samplerefractiveindex"
               alias="sample_refractive_index" />
    <attribute name="cr138_instrumentname" alias="instrument_nickname" />
    <attribute name="aibs_imagingfluorescencechannels"
               alias="imaging_channels" />
    <attribute name="aibs_stitchingfluorescencechannels"
               alias="stitching_channels" />
    <attribute name="aibs_ccffluorescencechannels"
               alias="ccf_registration_channels" />
    <attribute name="aibs_celldetectionfluorescencechannels"
               alias="cell_segmentation_channels" />
    {subject_filter}
    {date_filter}
    <filter>
      <condition attribute="cr138_taskstatus" operator="eq"
                 value="{IMAGING_STATUS_COMPLETE}" />
    </filter>
    <link-entity name="systemuser"
                 from="systemuserid" to="aibs_operator"
                 link-type="outer" alias="u">
      <attribute name="fullname" alias="experimenter_name" />
    </link-entity>
    <link-entity name="cr138_imagelibrary"
                 from="cr138_imagelibraryid"
                 to="cr138_detailimagingorientation"
                 link-type="outer" alias="o">
      <attribute name="cr138_imagename" alias="orientation" />
    </link-entity>
    <link-entity name="aibs_procedurerequest1"
                 from="aibs_procedurerequest1id" to="aibs_procedurerequestid"
                 link-type="outer" alias="pr">
      <link-entity name="systemuser"
                   from="systemuserid" to="aibs_requestor"
                   link-type="outer" alias="pu">
        <attribute name="fullname" alias="order_created_by" />
      </link-entity>
      <link-entity name="cr138_aibsprojects"
                   from="cr138_aibsprojectsid" to="cr138_aibsproject"
                   link-type="outer" alias="pp">
        <attribute name="cr138_name" alias="order_project_id" />
      </link-entity>
    </link-entity>
  </entity>
</fetch>
"""


def _choice_label(labels: dict[int, str], code: object) -> str | None:
    """
    Look up the label of a choice column code.

    Parameters
    ----------
    labels : dict[int, str]
        The labels of the choice column, keyed by code.
    code : object
        The code, or None.

    Returns
    -------
    str | None
        The label, the code itself when it is unknown, or None.
    """
    return None if code is None else labels.get(code, str(code))


def _orientation_directions(orientation: object) -> dict[str, str | None]:
    """
    Convert an orientation image name into the z, y and x directions.

    Parameters
    ----------
    orientation : object
        The image name, like ``Horizontal_IPR.png``, or None.

    Returns
    -------
    dict[str, str | None]
        The ``z_direction``, ``y_direction`` and ``x_direction``. All are None
        when the name has no three-letter code; an unknown letter gives None.
    """
    code = str(orientation or "").rsplit(".", 1)[0].rsplit("_", 1)[-1]
    letters = code if len(code) == 3 else ""
    return {
        axis: AXIS_DIRECTIONS.get(letter)
        for axis, letter in zip(
            ("z_direction", "y_direction", "x_direction"),
            letters or (None, None, None),
        )
    }


def _channels(value: object) -> list[str] | None:
    """
    Split a multi-select channel column into its channels. The codes of
    these columns are the wavelengths, which are also their labels.

    Parameters
    ----------
    value : object
        The comma-separated codes, like ``"488,639"``, or None.

    Returns
    -------
    list[str] | None
        The channels, or None when none are selected.
    """
    return None if value is None else str(value).split(",")


def imaging_rows_to_models(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """
    Convert the rows returned by ``imaging_fetchxml`` into records.

    Parameters
    ----------
    rows : list[dict[str, object]]
        The rows returned by ``imaging_fetchxml``.

    Returns
    -------
    list[dict[str, object]]
        Records shaped like ``SmartSpimImagingModel``, in the same order.
    """
    records = []
    for row in rows:
        stitching = _channels(row.get("stitching_channels"))
        ccf = _channels(row.get("ccf_registration_channels"))
        records.append(
            {
                "experiment_run_created_on": row.get(
                    "experiment_run_created_on"
                ),
                "order_created_by": row.get("order_created_by"),
                "order_project_id": row.get("order_project_id"),
                "specimen_id": row.get("specimen_id"),
                "subject_id": row.get("subject_id"),
                "date_performed": row.get("date_performed"),
                "chamber_immersion_medium": _choice_label(
                    CHAMBER_IMMERSION_MEDIUM_LABELS,
                    row.get("chamber_immersion_medium"),
                ),
                "sample_immersion_medium": _choice_label(
                    SAMPLE_IMMERSION_MEDIUM_LABELS,
                    row.get("sample_immersion_medium"),
                ),
                "chamber_refractive_index": row.get(
                    "chamber_refractive_index"
                ),
                "sample_refractive_index": row.get("sample_refractive_index"),
                "instrument_nickname": _choice_label(
                    INSTRUMENT_NICKNAME_LABELS, row.get("instrument_nickname")
                ),
                "experimenter_name": row.get("experimenter_name"),
                **_orientation_directions(row.get("orientation")),
                "imaging_channels": _channels(row.get("imaging_channels")),
                "stitching_channels": (
                    None if stitching is None else ", ".join(stitching)
                ),
                "ccf_registration_channels": (
                    None if ccf is None else ", ".join(ccf)
                ),
                "cell_segmentation_channels": _channels(
                    row.get("cell_segmentation_channels")
                ),
            }
        )
    return records
