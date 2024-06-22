import asyncio
from datetime import datetime

import pytest
from httpx import AsyncClient

from src.dependencies import sheet_loader
from src.models.checklist_report import ChecklistReport


@pytest.mark.asyncio
async def test_checklist_full(checklist_data: dict, async_client: AsyncClient):
    response = await async_client.post("/checklist/full", json=checklist_data, timeout=20)

    assert response.status_code == 200, "Status code is not 200"
    result_data = response.json()
    assert result_data.get("sheet_id") == "1eob4Hykpmm3S2Cigz31aPBTBNXHKbexuHq5h4h1Ehbk"
    assert result_data.get("softcheck") == True
    assert result_data.get("is_ready") == True


@pytest.mark.asyncio
async def test_checklist_is_ready_false(checklist_is_ready_false_data: dict, async_client: AsyncClient):
    response = await async_client.post("/checklist", json=checklist_is_ready_false_data, timeout=20)

    assert response.status_code == 404, "Status code is not 404"


@pytest.mark.asyncio
async def test_checklist_status_error(checklist_status_error_data: dict, async_client: AsyncClient):
    response = await async_client.post("/checklist", json=checklist_status_error_data, timeout=20)

    assert response.status_code == 500, "Status code is not 500"


@pytest.mark.asyncio
async def test_checklist_not_exists(checklist_data_not_exists: dict, async_client: AsyncClient):
    # Test with task_name of checklist that not exists
    response = await async_client.post("/checklist", json=checklist_data_not_exists, timeout=20)

    assert response.status_code == 404, "Status code is not 404"
    await asyncio.sleep(1)

    recorded_rows = sheet_loader.get_all_rows(sheet_name="ACTIVITIES")

    expected_data = [
        str(checklist_data_not_exists["ticket_id"]),
        checklist_data_not_exists["task_name"],
        checklist_data_not_exists["mentor_full_name"],
        'Checklist not found',
    ]

    found = False

    for row in recorded_rows:
        if row[1] == expected_data[0]:
            assert row[1:5] == expected_data  # убираем record_time в начале и timedelta, ticket_link в конце
            found = True

    assert found, "Expected record not found in table ACTIVITIES"


@pytest.mark.asyncio
async def test_checklist_with_sheet_id(checklist_data_sheet_id: dict, async_client: AsyncClient):
    # Test with sheet_id
    response = await async_client.post("/checklist", json=checklist_data_sheet_id, timeout=20)

    assert response.status_code == 200, "Status code is not 200"


@pytest.mark.asyncio
async def test_checklist_without_sheet_id(checklist_data: dict, async_client: AsyncClient):
    # Test with task_name
    response = await async_client.post("/checklist", json=checklist_data, timeout=20)

    assert response.status_code == 200, "Status code is not 200"


@pytest.mark.asyncio
async def test_generate_motivation_with_noai(motivation_data_noai: dict, async_client: AsyncClient):
    response = await async_client.post("/generate-motivation", json=motivation_data_noai, timeout=30)
    assert response.status_code == 200, "Status code is not 200"
    result = response.json()
    assert 'Глеб' in result.get("response")


@pytest.mark.asyncio
async def test_generate_motivation_with_python_simple(motivation_data_simple: dict, async_client: AsyncClient):
    response = await async_client.post("/generate-motivation", json=motivation_data_simple, timeout=30)
    assert response.status_code == 200, "Status code is not 200"
    result = response.json()
    assert 'Глеб' in result.get("response")


@pytest.mark.asyncio
async def test_report(report_data: dict, async_client: AsyncClient):
    response = await async_client.post("/report", json=report_data, timeout=20)
    assert response.status_code == 201, "Status code is not 201"
    await asyncio.sleep(1)

    recorded_rows = sheet_loader.get_all_rows(sheet_name="ACTIVITIES")

    expected_data = [
        str(report_data["ticket_id"]),
        report_data["task_name"],
        report_data["mentor_full_name"],
        'close',
    ]

    found = False

    for row in recorded_rows:
        if row[1] == expected_data[0]:
            assert row[1:5] == expected_data  # убираем record_time в начале и timedelta, ticket_link в конце
            found = True

    assert found, "Expected record not found in table ACTIVITIES"

    recorded_rows_criteria = sheet_loader.get_all_rows(sheet_name="CRITERIA", worksheet_name="criteria")

    report = ChecklistReport(**report_data)

    expected_count = len(report.checklist_data)
    found_criteria_count = 0

    for row in recorded_rows_criteria:
        for expected_checklist in report.checklist_data.values():
            if row[2] == expected_checklist["criteria"]:
                assert row[0] == str(report.ticket_id)
                assert row[1] == str(report.student_id)
                assert row[3] == str(expected_checklist["grade"])
                assert row[4] == report.mentor_full_name
                assert row[5] == report.stream_name
                assert row[6] == report.task_name
                assert row[7] == expected_checklist["step"]
                assert row[8] == expected_checklist["skill"]
                assert row[9] == expected_checklist["note"]
                assert datetime.strptime(row[10], "%Y-%m-%dT%H:%M:%S")
                found_criteria_count += 1

    assert found_criteria_count == expected_count, \
        f"Expected {expected_count} criteria records, but found {found_criteria_count}"


@pytest.mark.asyncio
async def test_report_soft_skills(report_soft_skills_data: dict, async_client: AsyncClient):
    response = await async_client.post("/report-soft-skills", json=report_soft_skills_data, timeout=20)
    assert response.status_code == 201, "Status code is not 201"


@pytest.mark.asyncio
async def test_explain_slug(async_client: AsyncClient):
    slug = "sozdaet-klassy-i-ekzemplyary-iz-klassov"
    student_id = "123456"

    response = await async_client.get(f"/explain/{slug}?student_id={student_id}", timeout=20)
    assert response.status_code == 301, "Status code is not 301"
    await asyncio.sleep(1)

    recorded_row = sheet_loader.get_all_rows(sheet_name="WIKI_REQUESTS")

    expected_data = [student_id, slug]

    found = False

    for row in recorded_row:
        if row[1] == expected_data[0]:
            assert row[1:] == expected_data
            found = True

    assert found, "Expected record not found in table WIKI_REQUESTS"


@pytest.mark.asyncio
async def test_explain_slug_without_student_id(async_client: AsyncClient):
    slug = "realizuet-razlichnye-metody-klassov-soglasno-postavlennoy-zadache"

    response = await async_client.get(f"/explain/{slug}", timeout=20)
    assert response.status_code == 200, "Status code is not 200"


@pytest.mark.asyncio
async def test_explain_slug_personalized(async_client: AsyncClient):
    slug = "sozdaet-klassy-i-ekzemplyary-iz-klassov"

    # Test with student_id
    response = await async_client.get(f"/explain/{slug}/personalize", timeout=60)
    assert response.status_code == 200, "Status code is not 200"
    assert "Эта статья сгенерирована с помощью ИИ под ваш запрос" in response.text


@pytest.mark.asyncio
async def test_explain_slug_rate(async_client: AsyncClient):
    slug = "sozdaet-klassy-i-ekzemplyary-iz-klassov"
    student_id = 123456
    grade = 5
    personalized = "personalized"

    response = await async_client.get(
        f"/explain/{slug}/rate?grade={grade}&student_id={student_id}&personalized={personalized}", timeout=20
    )
    assert response.status_code == 200, "Status code is not 200"
    await asyncio.sleep(1)

    recorded_row = sheet_loader.get_all_rows(sheet_name="WIKI_RATES")

    expected_data = [
        slug,
        str(student_id),
        str(grade),
        personalized
    ]

    found = False

    for row in recorded_row:
        if row[0] == expected_data[0]:
            assert row[:-1] == expected_data  # убираем datetime в конце
            found = True

    assert found, "Expected record not found in table WIKI_RATES"
