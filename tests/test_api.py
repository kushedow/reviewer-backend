import pytest
from httpx import AsyncClient


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
    # Test without sheet_id
    response = await async_client.post("/checklist", json=checklist_data, timeout=20)

    assert response.status_code == 200, "Status code is not 200"
    result_data = response.json()
    assert result_data[0].get("title") == "Решение выложено на GitHub"


@pytest.mark.asyncio
async def test_checklist_with_sheet_id(checklist_data: dict, async_client: AsyncClient):
    # Test with sheet_id
    checklist_data['sheet_id'] = '1eob4Hykpmm3S2Cigz31aPBTBNXHKbexuHq5h4h1Ehbk'
    response = await async_client.post("/checklist", json=checklist_data, timeout=20)

    assert response.status_code == 200, "Status code is not 200"
    result_data = response.json()
    assert result_data[1].get("title") == "В проекте есть .gitignore"


@pytest.mark.asyncio
async def test_generate_motivation_with_noai(generate_motivation_data: dict, async_client: AsyncClient):
    response = await async_client.post("/generate-motivation", json=generate_motivation_data, timeout=30)
    assert response.status_code == 200, "Status code is not 200"
    result = response.json()
    assert 'Глеб' in result.get("response")


@pytest.mark.asyncio
async def test_generate_motivation_with_python_simple(generate_motivation_data: dict, async_client: AsyncClient):
    generate_motivation_data['prompt_name'] = 'python_simple'
    response = await async_client.post("/generate-motivation", json=generate_motivation_data, timeout=30)
    assert response.status_code == 200, "Status code is not 200"
    result = response.json()
    assert 'Глеб' in result.get("response")


@pytest.mark.asyncio
async def test_report(report_data: dict, async_client: AsyncClient):
    response = await async_client.post("/report", json=report_data, timeout=20)
    assert response.status_code == 201, "Status code is not 201"


@pytest.mark.asyncio
async def test_report_soft_skills(report_soft_skills_data: dict, async_client: AsyncClient):
    response = await async_client.post("/report-soft-skills", json=report_soft_skills_data, timeout=20)
    assert response.status_code == 201, "Status code is not 201"


@pytest.mark.asyncio
async def test_explain_slug(async_client: AsyncClient):
    slug = "sozdaet-klassy-i-ekzemplyary-iz-klassov"
    student_id = "123456"

    # Test 1: with student_id
    response = await async_client.get(f"/explain/{slug}?student_id={student_id}", timeout=20)
    assert response.status_code == 301, "Status code is not 301"

    # Test 2: without student_id
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
