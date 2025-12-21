"""Тесты HTTP-API InvestCalc (уровень FastAPI)."""

from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_health_ok():
    """Эндпоинт /health должен возвращать статус ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_calc_basic_endpoint():
    """Проверка базового расчёта через POST /api/v1/calc."""
    payload = {
        "project_name": "Test project",
        "capex": 100_000,
        "opex": 20_000,
        "effects": 180_000,
        "period_months": 24,
        "discount_rate_percent": None,
    }

    resp = client.post("/api/v1/calc", json=payload)
    assert resp.status_code == 200, resp.text

    data = resp.json()

    ## Проверяем наличие ключевых полей результата
    assert "tco" in data
    assert "roi_percent" in data or "roi" in data
    assert "payback_months" in data
    assert "payback_years" in data
    assert "note" in data
