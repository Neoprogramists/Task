"""Тесты анализа чувствительности (sensitivity analysis)."""

from src.models.invest import InvestInput, SensitivityRequest
from src.services.invest_service import run_sensitivity, InvestService


def _make_base_input() -> InvestInput:
    return InvestInput(
        project_name="Sensitivity base",
        capex=100_000,
        opex=20_000,
        effects=180_000,
        period_months=24,
        discount_rate_percent=None,
    )


def test_run_sensitivity_function():
    """Проверяем, что функция run_sensitivity возвращает структуру с items."""
    base = _make_base_input()
    req = SensitivityRequest(
        base_input=base,
        delta_percent=20,
        parameters=["capex", "opex", "effects"],
    )

    result = run_sensitivity(req)

    assert result.delta_percent == 20
    assert result.base_result is not None
    assert len(result.items) >= 1

    for item in result.items:
        assert item.minus_delta_result is not None
        assert item.plus_delta_result is not None


def test_invest_service_run_sensitivity():
    """Проверяем, что метод сервиса run_sensitivity() работает как обёртка."""
    service = InvestService()
    base = _make_base_input()
    req = SensitivityRequest(
        base_input=base,
        delta_percent=10,
        parameters=["capex"],
    )

    result = service.run_sensitivity(req)

    assert result.delta_percent == 10
    assert len(result.items) == 1
    item = result.items[0]
    assert item.parameter == "capex"
    assert item.minus_delta_result is not None
    assert item.plus_delta_result is not None
