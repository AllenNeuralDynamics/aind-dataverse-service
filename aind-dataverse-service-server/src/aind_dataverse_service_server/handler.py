"""Module to handle query logic and responses."""

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
