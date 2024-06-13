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

        recorded_rows = sheet_loader.get_last_n_rows(sheet_name="CRITERIA", rows_count=checklist_count,
                                                     worksheet_name="criteria")

        for i, row in enumerate(recorded_rows):
            expected_report = checklist_report.checklist_data[str(i)]

            assert row[0] == str(checklist_report.ticket_id)
            assert row[1] == str(checklist_report.student_id)
            assert row[2] == expected_report["title"]
            assert row[3] == str(expected_report["grade"])
            assert row[4] == checklist_report.mentor_full_name
            assert row[5] == checklist_report.stream_name
            assert row[6] == checklist_report.task_name
            assert row[7] == expected_report["step"]
            assert row[8] == expected_report["skill"]
            assert row[9] == expected_report["note"]

    def test_push_ai_generation_from_request(self, ai_request: AIRequest):
        """ Test push AI generation report to GENERATIONS google sheet """
        output_text = (
            'TEST / Заметно, что ты вложил много усилий в это задание, и результат получился великолепным. '
            'Все необходимые элементы выполнены и отмечены как "✅". Что касается твоего кода, я проверил его '
            'с удовольствием и не нашел никаких замечаний.\nКроме того, нет никаких задач, требующих исправлений. '
            'Так что я с радостью принимаю твою работу. Желаю удачи в следующих уроках и с нетерпением жду новых '
            'интересных решений. У меня даже нет предложений по улучшению!'
        )
        result = sheet_pusher.push_ai_generation_from_request(ai_request, output_text)

        assert result["updates"]["updatedRows"] == 1

        recorder_row = sheet_loader.get_last_n_rows(sheet_name="GENERATIONS", rows_count=1)
        row = recorder_row[0]

        assert row[1] == str(ai_request.ticket_id)
        assert row[2] == ai_request.mentor_full_name
        assert row[4] == output_text

    def test_push_activity_from_request(self, checklist_report: ChecklistReport):
        """ Test push activities report to ACTIVITIES google sheet """
        event = "close"
        result = sheet_pusher.push_activity_from_request(model=checklist_report, event=event)

        assert result["updates"]["updatedRows"] == 1

        recorded_row = sheet_loader.get_last_n_rows(sheet_name="ACTIVITIES", rows_count=1)
        row = recorded_row[0]

        assert row[1] == str(checklist_report.ticket_id)
        assert row[2] == checklist_report.mentor_full_name
        assert row[3] == event

    def test_push_softskills_from_request(self, softskills_report: SoftskillsReport):
        """ Test push softskills report to SOFTSKILLS google sheet """
        skills_count = len(softskills_report.skills)
        result = sheet_pusher.push_softskills_from_request(softskills_report)

        assert result["updates"]["updatedRows"] == skills_count

        recorded_rows = sheet_loader.get_last_n_rows(sheet_name="SOFTSKILLS", rows_count=skills_count)

        for i, row in enumerate(recorded_rows, start=1):
            expected_skill = f"skill_{i}"
            value = softskills_report.skills[expected_skill]

            assert row[0] == str(softskills_report.ticket_id)
            assert row[1] == str(softskills_report.student_id)
            assert row[3] == softskills_report.mentor_full_name
            assert row[4] == softskills_report.task_name
            assert row[5] == expected_skill
            assert row[6] == str(value)

    def test_push_save_request_to_wiki(self):
        """ Test push save request to WIKI_REQUESTS google sheet """
        student_id = "111222333"
        skill = "TEST / Skill"
        result = sheet_pusher.push_save_request_to_wiki(student_id=student_id, skill=skill)

        assert result["updates"]["updatedRows"] == 1

        recorded_row = sheet_loader.get_last_n_rows(sheet_name="WIKI_REQUESTS", rows_count=1)
        row = recorded_row[0]

        assert row[1] == student_id
        assert row[2] == skill

    def test_push_wiki_rate(self):
        """ Test push wiki rate to WIKI_RATES google sheet """
        slug = "test-slug"
        grade = 5
        student_id = 111222333
        result = sheet_pusher.push_wiki_rate(
            slug=slug, grade=grade, student_id=student_id, personalized="personalized"
        )

        assert result["updates"]["updatedRows"] == 1

        recorded_row = sheet_loader.get_last_n_rows(sheet_name="WIKI_RATES", rows_count=1)
        row = recorded_row[0]

        assert row[0] == slug
        assert row[1] == str(student_id)
        assert row[2] == str(grade)
        assert row[3] == "personalized"
