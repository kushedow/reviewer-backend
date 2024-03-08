from classes.SkillProcessor import SkillProcessor

skill_processor = SkillProcessor()

def process_skills_from_checklist(checklist_data, ticket_id: int):

    skill_records = skill_processor.build_skill_records(checklist_data, ticket_id)

    return skill_records



