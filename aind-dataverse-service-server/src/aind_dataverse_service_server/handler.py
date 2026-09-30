"""Module to handle query logic and responses. Note that the Dataverse SQL API
is read-only and has protections against injection attacks.
"""

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
    INNER JOIN aibs_fact_mouse_water_restriction w
      ON w.aibs_mouse_id = m.aibs_dim_miceid
    INNER JOIN aibs_fact_mouse_water_restriction_change_log c
      ON c.aibs_mouse_id = m.aibs_dim_miceid
      AND (c.aibs_new_value = 'active water restriction'
      OR c.aibs_old_value = 'active water restriction')
    WHERE m.aibs_mouse_id = '{mouse_id}'
    """
