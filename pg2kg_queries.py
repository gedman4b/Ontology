def queries():
    s_query = """
SELECT s.nct_id,
s.verification_date,s.completion_date,
s.study_type,s.baseline_population,s.brief_title,s.official_title,
s.overall_status,s.phase,s.enrollment,s.source,s.limitations_and_caveats,s.number_of_arms,
s.number_of_groups,s.why_stopped,s.has_expanded_access,s.has_dmc,s.is_fda_regulated_drug,
s.is_fda_regulated_device,s.is_unapproved_device,s.is_ppsd,s.is_us_export,s.biospec_retention,
s.biospec_description,s.plan_to_share_ipd,s.plan_to_share_ipd_description,
s.source_class,s.delayed_posting,s.fdaaa801_violation,
s.baseline_type_units_analyzed, bs.description
FROM studies s
JOIN brief_summaries bs
ON s.nct_id = bs.nct_id
"""
    sc_query = """
select s.nct_id as "instance_id", c.name as "studies_condition"
from studies s
join conditions c
on s.nct_id = c.nct_id
"""
    int_query = """
select s.nct_id, i.name, i.description, re.adverse_event_term
from interventions i
join studies s
on i.nct_id = s.nct_id
join reported_events re
on re.nct_id = s.nct_id
"""
    intv_inst_query = """
select s.nct_id,i.name,i.intervention_type,re.adverse_event_term,c.name
from interventions i
join conditions c
on i.nct_id = c.nct_id
join studies s
on i.nct_id = s.nct_id
join reported_events re
on re.nct_id = s.nct_id
"""
