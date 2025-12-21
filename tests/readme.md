## Тесты проекта InvestCalc

Каталог `tests/` содержит **автоматические тесты** для учебного проекта InvestCalc:

- проверка работы HTTP-API (FastAPI);
- проверка бизнес-логики расчётов (TCO, ROI, Payback);
- тесты анализа чувствительности;
- тесты работы со сценариями в JSON-хранилище.

Отдельно в `project/api-skeleton/tests/` лежат **тесты-образцы** для учебного каркаса API (skeleton).

---

## Структура тестов

```text
project/
  api-skeleton/
    tests/
      test_healthcheck.py   ## Проверка health-check в учебном skeleton API

tests/
  conftest.py               ## Общие фикстуры и настройка окружения
  test_api.py               ## Тесты HTTP-эндпоинтов (уровень FastAPI)
  test_service.py           ## Тесты бизнес-логики (service / calculate_metrics)
  test_sensitivity.py       ## Тесты анализа чувствительности
  test_scenarios.py         ## Тесты работы со сценариями (JSON-хранилище)
```

---

## Общая настройка (`conftest.py`)

Файл `tests/conftest.py`:

* добавляет корень проекта в `sys.path`, чтобы можно было писать `from src....`;
* импортирует:

  * `src.main.app` — FastAPI-приложение;
  * `src.services.invest_service.InvestService` — сервисный слой;
  * `src.core.config.settings` — конфигурация;
* предоставляет фикстуры:

## `test_app`

```python
@pytest.fixture(scope="session")
def test_app():
    """Экземпляр FastAPI-приложения для API-тестов."""
    return app
```

Используется для создания `TestClient` или интеграции с async-тестами.

## `service`

```python
@pytest.fixture(scope="session")
def service() -> InvestService:
    """Сервис бизнес-логики InvestCalc."""
    return InvestService()
```

Даёт доступ к сервисному слою без HTTP.

## `tmp_data_dir`

```python
@pytest.fixture
def tmp_data_dir(tmp_path, monkeypatch):
    """
    Временная директория для JSON-данных (scenarios.json и т.п.).

    Подменяет:
    - settings.DATA_DIR
    - settings.SCENARIOS_FILE
    на путь в tmp_path.
    """
```

Нужно, чтобы тесты со сценариями **не портили реальные файлы** в `data/`.
Каждый тест получает «чистую» временную папку, в которой создаются и проверяются `scenarios.json`.

---

## Тесты HTTP-API (`test_api.py`)

Файл `test_api.py` проверяет базовые эндпоинты FastAPI-приложения:

* `GET /health`
  Убедиться, что сервис жив и возвращает:

  ```json
  {"status": "ok"}
  ```

* `POST /api/v1/calc`
  Проверяется:

  * успешный статус `200`;
  * наличие ключевых полей в ответе: `tco`, `roi_percent` (или `roi`), `payback_months`, `payback_years`, `note`.

Тесты используют `fastapi.testclient.TestClient` и реальный `app` из `src.main`.

---

## Тесты бизнес-логики (`test_service.py`)

Файл `test_service.py` работает напрямую с Pydantic-моделями и сервисным слоем:

* `test_calculate_metrics_basic`
  Проверяет, что `calculate_metrics`:

  * корректно считает TCO (CAPEX + OPEX),
  * возвращает числовые значения ROI и срока окупаемости,
  * формирует текстовый комментарий.

* `test_calculate_metrics_negative_values_validation`
  Подтверждает, что **валидация Pydantic-модели `InvestInput`** не позволяет отрицательные значения CAPEX (ожидается `ValidationError`).

* `test_invest_service_calculate`
  Проверяет, что `InvestService.calculate()` правильно оборачивает `calculate_metrics`.

---

## Тесты анализа чувствительности (`test_sensitivity.py`)

Файл `test_sensitivity.py` проверяет модуль `run_sensitivity` и метод `InvestService.run_sensitivity`:

* `test_run_sensitivity_function`

  * формирует базовый `InvestInput` и `SensitivityRequest`,
  * вызывает `run_sensitivity(...)`,
  * убеждается, что:

    * `delta_percent` совпадает,
    * есть базовый результат,
    * список `items` не пустой,
    * у каждого `SensitivityItem` есть `minus_delta_result` и `plus_delta_result`.

* `test_invest_service_run_sensitivity`
  Проверяет, что метод сервиса оборачивает функцию и возвращает ожидаемую структуру.

---

## Тесты сценариев (`test_scenarios.py`)

Файл `test_scenarios.py` проверяет CRUD-операции над сценариями:

* использует фикстуру `tmp_data_dir`, чтобы работать в временной директории;
* через `InvestService` выполняет:

  1. Чтение списка сценариев (`list_scenarios`) — в начале он пустой.
  2. Создание `ScenarioDetail` с валидными полями:

     * `id` (строка),
     * `created_at` (datetime),
     * основной `input` (`InvestInput`).
  3. Сохранение сценария через `save_scenario`.
  4. Повторное чтение списка сценариев.
  5. Чтение сценария по `id` через `get_scenario` и проверку полей.

Таким образом проверяется связка:

* `settings.DATA_DIR` / `settings.SCENARIOS_FILE`;
* функции `_load_scenarios_raw`, `_save_scenarios_raw`;
* API сервисного слоя: `list_scenarios`, `save_scenario`, `get_scenario`.

---

## Тесты учебного skeleton API

В `project/api-skeleton/tests/test_healthcheck.py` находится минимальный тест:

* `test_health` — проверяет, что учебный skeleton API корректно отдаёт ответ на health-check.

Эти тесты показывают студентам, как строить простую проверку API **на уровне каркаса**, ещё до полноценной реализации InvestCalc.

---

## Как запускать тесты

Из корня проекта `investcalc` (где лежит папка `src`):

```bash
pytest -vv
```

или только основные тесты:

```bash
pytest tests -vv
```

> Убедись, что установлены зависимости:
>
> ```bash
> pip install pytest fastapi[all]
> ```

---

## Как адаптировать тесты под изменения

Если ты:

* меняешь структуру моделей (`InvestInput`, `InvestResult`, `ScenarioDetail`),
* добавляешь новые поля,
* меняешь маршруты (`/api/v1/calc`, `/api/v1/scenarios`),

то:

1. сначала обнови **модели и сервисный слой**;
2. затем поправь ожидания в тестах:

   * поля в JSON-ответах,
   * ограничения в Pydantic-моделях,
   * количество сценариев и т.п.

Тесты здесь — это **опорный пример**, как проверять:

* расчётные функции,
* слой сервисов,
* работу с JSON-хранилищем,
* HTTP-эндпоинты через FastAPI.

 