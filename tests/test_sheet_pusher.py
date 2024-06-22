from datetime import datetime

from src.dependencies import sheet_pusher, sheet_loader
from src.models.ai_request import AIRequest
from src.models.checklist_report import ChecklistReport
from src.models.softskills_report import SoftskillsReport


class TestSheetPusher:

    def test_push_criteria_from_report(self, checklist_report: ChecklistReport):
        """ Test push checklist reports to CRITERIA google sheet """
        checklist_count = len(checklist_report.checklist_data)

        result = sheet_pusher.push_criteria_from_report(checklist_report)

        assert result["updates"]["updatedRows"] == checklist_count, \
            'Ошибка: кол-во добавленных строк в таблице не совпадает!'

        recorded_rows = sheet_loader.get_all_rows(sheet_name="CRITERIA", worksheet_name="criteria")

        expected_count = len(checklist_report.checklist_data)
        found_skill_count = 0

        for row in recorded_rows:
            for expected_checklist in checklist_report.checklist_data.values():
                if row[8] == expected_checklist["skill"]:
                    assert row[0] == str(checklist_report.ticket_id)
                    assert row[1] == str(checklist_report.student_id)
                    assert row[2] == expected_checklist["title"]
                    assert row[3] == str(expected_checklist["grade"])
                    assert row[4] == checklist_report.mentor_full_name
                    assert row[5] == checklist_report.stream_name
                    assert row[6] == checklist_report.task_name
                    assert row[7] == expected_checklist["step"]
                    assert row[9] == expected_checklist["note"]
                    assert datetime.strptime(row[10], "%Y-%m-%dT%H:%M:%S")
                    found_skill_count += 1

        assert found_skill_count == expected_count, \
            f"Expected {expected_count} skill records, but found {found_skill_count}!"

    def test_push_ai_generation_from_request(self, ai_request: AIRequest, ai_output_text: str):
        """ Test push AI generation report to GENERATIONS google sheet """
        result = sheet_pusher.push_ai_generation_from_request(ai_request, ai_output_text)

        assert result["updates"]["updatedRows"] == 1

        recorded_rows = sheet_loader.get_all_rows(sheet_name="GENERATIONS")

        expected_data = [
            str(ai_request.ticket_id),
            ai_request.mentor_full_name,
            '',
            ai_output_text
        ]

        found = False

        for row in recorded_rows:
            if row[1] == str(ai_request.ticket_id):
                assert row[1:5] == expected_data  # проверяем ticket_id, mentor, input, output
                found = True

        assert found, "Expected record not found in table GENERATIONS"

    def test_push_activity_from_request(self, checklist_report: ChecklistReport):
        """ Test push activities report to ACTIVITIES google sheet """
        event = "close"
        result = sheet_pusher.push_activity_from_request(model=checklist_report, event=event)

        assert result["updates"]["updatedRows"] == 1

        recorded_rows = sheet_loader.get_all_rows(sheet_name="ACTIVITIES")

        expected_data = [
            str(checklist_report.ticket_id),
            checklist_report.task_name,
            checklist_report.mentor_full_name,
            event
        ]

        found = False

        for row in recorded_rows:
            if row[1] == str(checklist_report.ticket_id):
                assert row[1:5] == expected_data
                found = True

        assert found, "Expected record not found in table ACTIVITIES"

    def test_push_softskills_from_request(self, softskills_report: SoftskillsReport):
        """ Test push softskills report to SOFTSKILLS google sheet """
        skills_count = len(softskills_report.skills)
        result = sheet_pusher.push_softskills_from_request(softskills_report)

        assert result["updates"]["updatedRows"] == skills_count

        recorded_rows = sheet_loader.get_all_rows(sheet_name="SOFTSKILLS")

        expected_count = len(softskills_report.skills)
        found_skill_count = 0

        for row in recorded_rows:
            for skill in softskills_report.skills:
                if row[0] == str(softskills_report.ticket_id) and row[5] == skill:
                    assert row[1] == str(softskills_report.student_id)
                    assert row[3] == softskills_report.mentor_full_name
                    assert row[4] == softskills_report.task_name
                    assert row[6] == str(softskills_report.skills[skill])
                    assert datetime.strptime(row[7], "%Y-%m-%dT%H:%M:%S")
                    found_skill_count += 1

        assert found_skill_count == expected_count, \
            f"Expected {expected_count} skill records, but found {found_skill_count}!"

    def test_push_save_request_to_wiki(self, request_to_wiki_data: dict):
        """ Test push save request to WIKI_REQUESTS google sheet """
        student_id = str(request_to_wiki_data["student_id"])
        skill = request_to_wiki_data["skill"]
        result = sheet_pusher.push_save_request_to_wiki(student_id=student_id, skill=skill)

        assert result["updates"]["updatedRows"] == 1

        recorded_row = sheet_loader.get_all_rows(sheet_name="WIKI_REQUESTS")

        found = False

        for row in recorded_row:
            if row[1] == student_id:
                assert row[2] == skill
                found = True

        assert found, "Expected record not found in table WIKI_REQUESTS"

    def test_push_wiki_rate(self, push_wiki_rate_data: dict):
        """ Test push wiki rate to WIKI_RATES google sheet """
        student_id = str(push_wiki_rate_data["student_id"])
        slug = push_wiki_rate_data["slug"]
        grade = str(push_wiki_rate_data["grade"])
        personalized = push_wiki_rate_data["personalized"]
        result = sheet_pusher.push_wiki_rate(slug=slug, grade=grade, student_id=student_id, personalized=personalized)

        assert result["updates"]["updatedRows"] == 1

        recorded_row = sheet_loader.get_all_rows(sheet_name="WIKI_RATES")

        found = False

        for row in recorded_row:
            if row[0] == slug:
                assert row[1] == student_id
                assert row[2] == grade
                assert row[3] == personalized
                assert datetime.strptime(row[4], "%Y-%m-%dT%H:%M:%S")
                found = True

        assert found, "Expected record not found in table WIKI_RATES"
