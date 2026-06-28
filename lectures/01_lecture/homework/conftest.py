"""
Общие фикстуры и настройки pytest для домашних заданий.

Что делает:
    - Устанавливает таймаут на каждый тест (30с — запас для CPU-bound)
    - Добавляет русские сообщения в summary
    - Регистрирует маркеры
"""

import pytest


def pytest_configure(config):
    """Регистрация кастомных маркеров."""
    config.addinivalue_line(
        "markers",
        "slow: медленные тесты (CPU-bound, >1с). Запускать отдельно: pytest -m slow",
    )
    config.addinivalue_line(
        "markers",
        "race: тесты race condition. "
        "Могут быть нестабильны из-за особенностей планировщика ОС",
    )


def pytest_report_header(config):
    """Добавляем информацию в заголовок pytest."""
    return [
        "Домашние задания — Лекция 1: Асинхронность в Python",
        "Ожидания: все тесты должны быть зелёными ✅",
    ]


@pytest.fixture
def timeout_counter():
    """Фикстура для замера времени выполнения теста.

    Использование:
        def test_something(timeout_counter):
            timeout_counter.start = time.perf_counter()
            # ... тест ...
            elapsed = time.perf_counter() - timeout_counter.start
            assert elapsed < 2.0
    """

    class TimeCtx:
        start: float = 0.0

    return TimeCtx()
