import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_checklist_without_sheet_id(checklist_data: dict, async_client: AsyncClient):
    # Test without sheet_id
    response = await async_client.post("/checklist", json=checklist_data, timeout=20)

    assert response.status_code == 200, "Status code is not 200"
    result_data = response.json()
    assert result_data[0].get("title") == "Функциональный код разбит на модули"


@pytest.mark.asyncio
async def test_checklist_with_sheet_id(checklist_data: dict, async_client: AsyncClient):
    # Test with sheet_id
    checklist_data['sheet_id'] = '1ljb-Sa0VAp0pDIcRJWsl9I_yICbhA6taQBJKzQQ47bk'
    response = await async_client.post("/checklist", json=checklist_data, timeout=20)

    assert response.status_code == 200, "Status code is not 200"
    result_data = response.json()
    assert result_data[1].get("title") == "Решение выложено на GitHub"


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
    response = await async_client.post("/report", json=report_data, timeout=10)
    assert response.status_code == 201, "Status code is not 201"


@pytest.mark.asyncio
async def test_report_soft_skills(report_soft_skills_data: dict, async_client: AsyncClient):
    response = await async_client.post("/report-soft-skills", json=report_soft_skills_data, timeout=10)
    assert response.status_code == 201, "Status code is not 201"


@pytest.mark.asyncio
async def test_explain_slug(async_client: AsyncClient):
    slug = "sozdaet-klassy-i-ekzemplyary-iz-klassov"
    student_id = "123456"

    # Test 1: with student_id
    response = await async_client.get(f"/explain/{slug}?student_id={student_id}", timeout=10)
    assert response.status_code == 301, "Status code is not 301"

    # Test 2: without student_id
    slug = "realizuet-razlichnye-metody-klassov-soglasno-postavlennoy-zadache"
    response = await async_client.get(f"/explain/{slug}", timeout=10)
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
        f"/explain/{slug}/rate?grade={grade}&student_id={student_id}&personalized={personalized}", timeout=10
    )
    assert response.status_code == 200, "Status code is not 200"
