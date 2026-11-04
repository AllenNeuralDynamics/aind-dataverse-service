"""Module to handle query logic and responses. Note that the Dataverse SQL API
is read-only and has protections against injection attacks. The histology
queries are expressed as FetchXML, the SDK's supported way to express JOINs.
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
LABELING_PROCEDURE = "SmartSPIM Labeling"

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


# Joins the whole brain imaging records of the same procedure request, whose
# brain ID is the specimen ID. A procedure request can have more than one, so
# rows can repeat per record.
_WHOLE_BRAIN_IMAGING_LINK = """
    <link-entity name="aibs_wholebrainimaging"
                 from="aibs_procedurerequestid"
                 to="aibs_procedurerequestid"
                 link-type="outer" alias="w">
      <attribute name="aibs_brainid" alias="specimen_id" />
      <attribute name="cr138_batchid" alias="imaging_batch_id" />
    </link-entity>"""


def _pick_specimen_id(
    rows: list[dict[str, object]], batch_id: object
) -> object:
    """
    Pick the brain ID from the joined whole brain imaging records.

    Parameters
    ----------
    rows : list[dict[str, object]]
        Rows of one record, each with the ``specimen_id`` and
        ``imaging_batch_id`` of an imaging record.
    batch_id : object
        The batch of the record. An imaging record in this batch is preferred.

    Returns
    -------
    object
        The brain ID of an imaging record in the same batch, otherwise the
        first one found, or None when there is none.
    """
    found = [r for r in rows if r.get("specimen_id") is not None]
    same_batch = [r for r in found if r.get("imaging_batch_id") == batch_id]
    return next((r["specimen_id"] for r in same_batch + found), None)


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


def _histology_filters(
    subject_attribute: str,
    date_attribute: str,
    subject_id: str,
    start_date_gte: datetime | None,
    end_date_lte: datetime | None,
) -> tuple[str, str]:
    """
    Build the subject filter and the optional date filter for the histology
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

    Returns one row per specimen, imaging record, batch step, step reagent lot
    and step participant. Removed batch memberships are excluded. The date
    range is applied to the batch's ``createdon``.

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
    subject_filter, date_filter = _histology_filters(
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
    {subject_filter}{_WHOLE_BRAIN_IMAGING_LINK}
    <link-entity name="cr138_delipidationbatchmembership"
                 from="cr138_reagentwash" to="aibs_reagentwashid"
                 link-type="inner" alias="m">
      <filter>
        <condition attribute="cr138_removedon" operator="null" />
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


def labeling_fetchxml(
    subject_id: str,
    start_date_gte: datetime | None = None,
    end_date_lte: datetime | None = None,
) -> str:
    """
    Generate FetchXML that gathers specimen labeling records.

    Returns one row per labeling record and imaging record. The date range is
    applied to its ``createdon``.

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
    subject_filter, date_filter = _histology_filters(
        "cr138_aibsmouseregistry",
        "createdon",
        subject_id,
        start_date_gte,
        end_date_lte,
    )
    return f"""
<fetch>
  <entity name="aibs_specimenlabeling">
    <order attribute="aibs_specimenlabelingid" />
    <attribute name="aibs_specimenlabelingid" alias="labeling_id" />
    <attribute name="cr138_batchid" alias="batch_id" />
    <attribute name="cr138_aibsmouseregistry" alias="subject_id" />
    <attribute name="createdon" alias="created_on" />
    <attribute name="aibs_startdate" alias="start_time" />
    <attribute name="aibs_enddate" alias="end_time" />
    {subject_filter}
    {date_filter}{_WHOLE_BRAIN_IMAGING_LINK}
    <link-entity name="cr138_aibsantibody"
                 from="cr138_aibsantibodyid" to="cr138_aibsfirstantibody"
                 link-type="outer" alias="a1">
      <attribute name="cr138_name" alias="primary_antibody" />
    </link-entity>
    <link-entity name="cr138_aibsantibody"
                 from="cr138_aibsantibodyid" to="cr138_aibssecondantibody"
                 link-type="outer" alias="a2">
      <attribute name="cr138_name" alias="secondary_antibody" />
    </link-entity>
    <link-entity name="cr138_aibsdye"
                 from="cr138_aibsdyeid" to="cr138_aibsdye"
                 link-type="outer" alias="d">
      <attribute name="cr138_name" alias="dye" />
    </link-entity>
    <link-entity name="systemuser"
                 from="systemuserid" to="modifiedby"
                 link-type="outer" alias="u">
      <attribute name="fullname" alias="modified_by" />
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
        ``row``, its ``step_ids`` in first-seen order and its
        ``imaging_rows``; and the steps, keyed by step ID, each with its first
        ``row``, its reagent ``lots`` and its ``participants``.
    """
    runs: dict[tuple, dict[str, object]] = {}
    steps: dict[object, dict[str, object]] = {}
    for row in rows:
        run = runs.setdefault(
            (row["reagent_wash_id"], row["batch_id"]),
            {"row": row, "step_ids": [], "imaging_rows": []},
        )
        run["imaging_rows"].append(row)
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
    without them applies to every specimen in the batch.

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
                        "specimen_id": _pick_specimen_id(
                            run["imaging_rows"], run["row"]["batch_id"]
                        ),
                        "washes": [
                            w
                            for _, w in sorted(
                                procedure_washes, key=lambda w: w[0]
                            )
                        ],
                    }
                )
    return records


def labeling_rows_to_histology(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """
    Collapse specimen labeling rows into one histology record per labeling
    record.

    Each labeling record has a single start and end time, so it becomes one
    wash whose reagents are its primary antibody, secondary antibody and dye,
    when set.

    Parameters
    ----------
    rows : list[dict[str, object]]
        The rows returned by ``labeling_fetchxml``.

    Returns
    -------
    list[dict[str, object]]
        Records shaped like ``HistologyModel``.
    """
    grouped: dict[object, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(row["labeling_id"], []).append(row)
    return [
        {
            "procedure_name": LABELING_PROCEDURE,
            "experiment_run_created_on": row.get("created_on"),
            "subject_id": row.get("subject_id"),
            "specimen_id": _pick_specimen_id(group, row.get("batch_id")),
            "washes": [
                {
                    "wash_name": "Labeling",
                    "start_time": row.get("start_time"),
                    "end_time": row.get("end_time"),
                    "modified_by": row.get("modified_by"),
                    "reagents": [
                        {"name": row[field]}
                        for field in (
                            "primary_antibody",
                            "secondary_antibody",
                            "dye",
                        )
                        if row.get(field) is not None
                    ],
                }
            ],
        }
        for group in grouped.values()
        for row in group[:1]
    ]
