"""Общий конфиг для тестов InvestCalc.

- Добавляет корень проекта в sys.path, чтобы импортировать `src.*`.
- Настраивает временную директорию для JSON-данных (scenarios.json), чтобы не портить реальные файлы.
"""

import sys
from pathlib import Path

import pytest

## Корень проекта = папка, в которой лежит src/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.main import app  ## noqa: E402
from src.services.invest_service import InvestService  ## noqa: E402
from src.core.config import settings  ## noqa: E402


@pytest.fixture(scope="session")
def test_app():
    """Экземпляр FastAPI-приложения для API-тестов."""
    return app


@pytest.fixture(scope="session")
def service() -> InvestService:
    """Сервис бизнес-логики InvestCalc."""
    return InvestService()


@pytest.fixture
def tmp_data_dir(tmp_path, monkeypatch):
    """Временная директория для JSON-данных (scenarios.json и т.п.).

    Чтобы тесты не трогали реальные файлы в data/, мы подменяем:
    - settings.DATA_DIR
    - settings.SCENARIOS_FILE
    на путь в tmp_path.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    scenarios_file = data_dir / "scenarios.json"

    ## Сохраняем старые значения
    old_data_dir = settings.DATA_DIR
    old_scen_file = settings.SCENARIOS_FILE

    monkeypatch.setattr(settings, "DATA_DIR", data_dir)
    monkeypatch.setattr(settings, "SCENARIOS_FILE", scenarios_file)

    yield data_dir

    monkeypatch.setattr(settings, "DATA_DIR", old_data_dir)
    monkeypatch.setattr(settings, "SCENARIOS_FILE", old_scen_file)
