"""Тесты бизнес-логики InvestCalc (уровень сервисного слоя)."""

import pytest
from pydantic import ValidationError

from src.models.invest import InvestInput
from src.services.invest_service import calculate_metrics, InvestService


def test_calculate_metrics_basic():
    """Проверка базового расчёта экономических показателей."""
    input_data = InvestInput(
        project_name="Test",
        capex=100_000,
        opex=20_000,
        effects=180_000,
        period_months=24,
        discount_rate_percent=None,
    )

    result = calculate_metrics(input_data)

    assert result.project_name == "Test"
    assert result.tco == 120_000.0
    assert isinstance(result.roi_percent, float)
    assert result.payback_months is not None
    assert result.payback_years is not None
    assert isinstance(result.note, str)


def test_calculate_metrics_negative_values_validation():
    """При отрицательных значениях CAPEX должно срабатывать валидирование модели InvestInput."""
    with pytest.raises(ValidationError):
        InvestInput(
            project_name="Bad",
            capex=-1,
            opex=10_000,
            effects=50_000,
            period_months=12,
            discount_rate_percent=None,
        )


def test_invest_service_calculate():
    """Проверка, что класс InvestService оборачивает calculate_metrics."""
    service = InvestService()

    input_data = InvestInput(
        project_name="Service test",
        capex=50_000,
        opex=10_000,
        effects=90_000,
        period_months=12,
        discount_rate_percent=None,
    )

    result = service.calculate(input_data)

    assert result.project_name == "Service test"
    assert result.tco == 60_000.0
    assert isinstance(result.roi_percent, float)
    assert result.payback_months is not None
    assert result.payback_years is not None
