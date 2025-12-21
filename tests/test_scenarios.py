"""Тесты работы со сценариями InvestCalc (JSON-хранилище)."""

from datetime import datetime

from src.models.invest import InvestInput, ScenarioDetail
from src.services.invest_service import InvestService


def test_scenario_crud_in_tmp_dir(tmp_data_dir):
    """Создание, сохранение и чтение сценариев через InvestService.

    tmp_data_dir фиксируется фикстурой из conftest.py и подменяет
    DATA_DIR/SCENARIOS_FILE в настройках.
    """
    service = InvestService()

    ## Изначально сценариев нет
    scenarios = service.list_scenarios()
    assert scenarios == []

    ## Создаём новый сценарий
    input_data = InvestInput(
        project_name="Scenario 1",
        capex=100_000,
        opex=20_000,
        effects=180_000,
        period_months=24,
        discount_rate_percent=None,
    )

    scenario = ScenarioDetail(
        id="temp-id",
        name="Первый сценарий",
        description="Тестовый сценарий",
        created_at=datetime.utcnow(),
        updated_at=None,
        input=input_data,
        last_result=None,
    )

    saved = service.save_scenario(scenario)
    assert saved.id is not None

    ## Список сценариев теперь содержит один элемент
    scenarios_after = service.list_scenarios()
    assert len(scenarios_after) == 1
    assert scenarios_after[0].id == saved.id

    ## Можно прочитать сценарий по id
    loaded = service.get_scenario(saved.id)
    assert loaded is not None
    assert loaded.name == "Первый сценарий"
    assert loaded.input.project_name == "Scenario 1"
