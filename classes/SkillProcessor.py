from typing import List

from classes.SkillRecord import SkillRecord


class SkillProcessor:

    def build_skill_records(self, checklist: dict, ticket_id: int) -> list[SkillRecord]:
        """
        Работает с сырым чеклистом, возвращая из него объекты записей,
        где для каждого критерия указано его минимальное значение
        :param checklist: структура типа  { 0: {title: ..., skill: ..., grade: ...} , 1: {...}, ... }
        :param ticket_id: номер тикета, нужен для записи в нормальной форме
        :return: список объектов записей о достижении навыков
        """

        skills_with_min_grades = {}

        for item in checklist.values():

            # тихо пропускаем записи, у которых нет навыка или оценки
            if "skill" not in item or "grade" not in item:
                continue

            # вытаскиваем название скилла и оценку из критерия
            skill, grade = item['skill'], int(item['grade'])

            # Вписываем в скилл минимальную оценку из критерия и того, что в нем было раньше
            skills_with_min_grades[skill] = min(grade, skills_with_min_grades.get(skill, 100))

        return [
            SkillRecord(ticket_id=ticket_id, skill=skill, grade=grade)
            for skill, grade in skills_with_min_grades.items()
        ]
