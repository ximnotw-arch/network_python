"""Тесты к ДЗ 1: ThreadPoolExecutor."""

import sys
import os
import time

# Загружаем локальный task.py, а не закешированный из соседнего каталога
sys.path.insert(0, os.path.dirname(__file__))
if "task" in sys.modules:
    del sys.modules["task"]

from task import (
    fetch_all,
    fetch_all_with_errors,
    fetch_all_with_progress,
)


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 1.1 — Базовый пул потоков
# ═══════════════════════════════════════════════════════════


class TestFetchAll:
    """Тесты для fetch_all()."""

    def test_returns_correct_data(self):
        urls = ["a", "b", "c"]
        result = fetch_all(urls, max_workers=2)
        assert result == ["data:a", "data:b", "data:c"], (
            f"Ожидали ['data:a', 'data:b', 'data:c'], получили {result}"
        )

    def test_faster_than_sequential(self):
        """3 URL x 0.05с = 0.15с последовательно.
        С max_workers=3 должно быть ~0.05с."""
        urls = ["x", "y", "z"]
        start = time.perf_counter()
        fetch_all(urls, max_workers=3)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.10, (
            f"Слишком медленно: {elapsed:.3f}с. Ожидалось ~0.05с при max_workers=3"
        )

    def test_respects_max_workers(self):
        """max_workers=1 должен быть медленнее max_workers=4."""
        urls = [f"url{i}" for i in range(4)]

        start = time.perf_counter()
        fetch_all(urls, max_workers=1)
        elapsed_1 = time.perf_counter() - start

        start = time.perf_counter()
        fetch_all(urls, max_workers=4)
        elapsed_4 = time.perf_counter() - start

        assert elapsed_1 > elapsed_4 * 1.8, (
            f"max_workers=1 ({elapsed_1:.3f}s) должен быть "
            f"существенно медленнее max_workers=4 ({elapsed_4:.3f}s). "
            f"Возможно, пул не используется или ThreadPoolExecutor не создаётся"
        )

    def test_empty_input(self):
        """Граничный случай: пустой список."""
        assert fetch_all([], max_workers=4) == [], (
            "Для пустого списка должен вернуться пустой список"
        )

    def test_single_url(self):
        """Граничный случай: один URL."""
        result = fetch_all(["only"], max_workers=4)
        assert result == ["data:only"], f"Ожидали ['data:only'], получили {result}"

    def test_preserves_order(self):
        """Порядок результатов = порядку URL."""
        urls = [str(i) for i in range(20)]
        result = fetch_all(urls, max_workers=4)
        expected = [f"data:{u}" for u in urls]
        assert result == expected, (
            f"Порядок результатов не совпадает с порядком URL.\n"
            f"Ожидали: {expected}\nПолучили: {result}"
        )

    def test_uses_threadpoolexecutor(self):
        """Проверяем, что действительно используем пул потоков."""
        urls = [f"url{i}" for i in range(10)]
        start = time.perf_counter()
        fetch_all(urls, max_workers=10)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.15, (
            f"Слишком медленно: {elapsed:.3f}с. "
            f"Похоже, запросы выполняются последовательно, "
            f"а не через ThreadPoolExecutor"
        )


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 1.2 — Обработка ошибок
# ═══════════════════════════════════════════════════════════


class TestFetchAllWithErrors:
    """Тесты для fetch_all_with_errors()."""

    def test_handles_bad_urls(self):
        """Плохие URL должны вернуть None."""
        urls = ["good1", "bad1", "good2", "bad2", "good3"]
        result = fetch_all_with_errors(urls, max_workers=3)
        assert len(result) == 5, f"Должно быть 5 результатов, получили {len(result)}"
        assert result[0] == "data:good1", (
            f"Первый (хороший) URL: ожидали 'data:good1', получили {result[0]}"
        )
        assert result[1] is None, (
            f"Второй (плохой) URL: ожидали None, получили {result[1]}"
        )
        assert result[2] == "data:good2", (
            f"Третий (хороший) URL: ожидали 'data:good2', получили {result[2]}"
        )
        assert result[4] == "data:good3"

    def test_all_good(self):
        """Все URL хорошие — все результаты не None."""
        urls = ["a", "b", "c"]
        result = fetch_all_with_errors(urls, max_workers=2)
        assert all(r is not None for r in result), (
            "Все URL хорошие, но некоторые результаты None"
        )
        assert result == ["data:a", "data:b", "data:c"]

    def test_all_bad(self):
        """Все URL плохие — все результаты None."""
        urls = ["bad1", "bad2", "bad3"]
        result = fetch_all_with_errors(urls, max_workers=2)
        assert all(r is None for r in result), (
            "Все URL плохие, но некоторые результаты не None"
        )
        assert len(result) == 3

    def test_empty(self):
        """Пустой список."""
        assert fetch_all_with_errors([], max_workers=2) == []


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 1.3 — Прогресс-бар
# ═══════════════════════════════════════════════════════════


class TestFetchAllWithProgress:
    """Тесты для fetch_all_with_progress()."""

    def test_calls_progress_callback(self):
        """Коллбэк вызывается для каждого завершённого URL."""
        calls = []

        def track_progress(done: int, total: int) -> None:
            calls.append((done, total))

        urls = [f"url{i}" for i in range(5)]
        fetch_all_with_progress(urls, max_workers=3, progress_callback=track_progress)

        assert len(calls) == 5, (
            f"Коллбэк должен быть вызван 5 раз (по одному на URL), "
            f"вызван {len(calls)} раз"
        )
        assert calls[-1] == (5, 5), (
            f"Последний вызов должен быть (5, 5), получили {calls[-1]}"
        )

    def test_progress_increases(self):
        """Счётчик completed должен монотонно расти."""
        calls = []

        def track_progress(done: int, total: int) -> None:
            calls.append(done)

        urls = [f"url{i}" for i in range(4)]
        fetch_all_with_progress(urls, max_workers=4, progress_callback=track_progress)

        assert sorted(calls) == [1, 2, 3, 4], (
            f"Счётчик должен пройти от 1 до {len(urls)}, получили {sorted(calls)}"
        )

    def test_without_callback(self):
        """Без коллбэка тоже работает."""
        urls = ["a", "b"]
        result = fetch_all_with_progress(urls, max_workers=2)
        assert len(result) == 2, (
            f"Без коллбэка: ожидали 2 результата, получили {len(result)}"
        )

    def test_returns_data(self):
        """Проверяем, что результаты — данные, а не None."""
        urls = ["a", "b", "c"]
        result = fetch_all_with_progress(urls, max_workers=2)
        assert all(r is not None for r in result), (
            "Некоторые результаты None, хотя ошибок нет"
        )
        assert all(r.startswith("data:") for r in result), (
            "Результаты должны начинаться с 'data:'"
        )
