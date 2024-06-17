import asyncio

import pytest
from httpx import AsyncClient

from src.dependencies import sheet_loader


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
async def test_checklist_without_sheet_id(checklist_data: dict, async_client: AsyncClient):
    # Test with task_name
    response = await async_client.post("/checklist", json=checklist_data, timeout=20)

    assert response.status_code == 200, "Status code is not 200"


@pytest.mark.asyncio
async def test_checklist_with_sheet_id(checklist_data_sheet_id: dict, async_client: AsyncClient):
    # Test with sheet_id
    response = await async_client.post("/checklist", json=checklist_data_sheet_id, timeout=20)

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

    recorded_row = sheet_loader.get_last_n_rows(sheet_name="ACTIVITIES", rows_count=1)
    row = recorded_row[0]

    assert row[1] == str(report_data["ticket_id"])
    assert row[2] == report_data["mentor_full_name"]
    assert row[3] == 'close'


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
    await asyncio.sleep(3)

    recorded_row = sheet_loader.get_last_n_rows(sheet_name="WIKI_REQUESTS", rows_count=1)
    row = recorded_row[0]

    assert row[1] == student_id
    assert row[2] == slug


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
    await asyncio.sleep(3)

    recorded_row = sheet_loader.get_last_n_rows(sheet_name="WIKI_RATES", rows_count=1)
    row = recorded_row[0]

    assert row[0] == slug
    assert row[1] == str(student_id)
    assert row[2] == str(grade)
    assert row[3] == "personalized"
