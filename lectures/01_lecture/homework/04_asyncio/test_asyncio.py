"""Тесты к ДЗ 4: Asyncio."""

import sys
import os
import asyncio
import time

# Загружаем локальный task.py, а не закешированный из соседнего каталога
sys.path.insert(0, os.path.dirname(__file__))
if "task" in sys.modules:
    del sys.modules["task"]

from task import (
    fetch_one_async,
    fetch_all_async,
    async_process_numbers,
    blocking_compute,
)


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 4.1 — Первая корутина
# ═══════════════════════════════════════════════════════════


class TestFetchOneAsync:
    """Тесты для fetch_one_async()."""

    def test_returns_correct_data(self):
        result = asyncio.run(fetch_one_async("test"))
        assert result == "data:test", f"Ожидали 'data:test', получили {result}"

    def test_is_coroutine(self):
        import inspect

        assert inspect.iscoroutinefunction(fetch_one_async), (
            "fetch_one_async должна быть async def функцией"
        )

    def test_uses_await(self):
        """Проверяем, что функция действительно асинхронная."""
        start = time.perf_counter()
        asyncio.run(fetch_one_async("x"))
        elapsed = time.perf_counter() - start
        assert elapsed < 0.1, (
            f"Слишком медленно: {elapsed:.3f}с. "
            f"Убедитесь, что используете await asyncio.sleep(), "
            f"а не time.sleep()"
        )


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 4.2 — Параллельный запуск
# ═══════════════════════════════════════════════════════════


class TestFetchAllAsync:
    """Тесты для fetch_all_async()."""

    def test_returns_correct_data(self):
        result = asyncio.run(fetch_all_async(["a", "b"]))
        assert result == ["data:a", "data:b"]

    def test_faster_than_sequential(self):
        urls = [str(i) for i in range(10)]
        start = time.perf_counter()
        _ = asyncio.run(fetch_all_async(urls))
        elapsed = time.perf_counter() - start
        assert elapsed < 0.15, (
            f"Слишком медленно: {elapsed:.3f}с. "
            f"Ожидалось ~0.05с при параллельном запуске 10 URL. "
            f"Возможно, корутины запускаются последовательно, "
            f"а не через asyncio.gather()"
        )

    def test_empty_input(self):
        result = asyncio.run(fetch_all_async([]))
        assert result == []

    def test_single_url(self):
        result = asyncio.run(fetch_all_async(["only"]))
        assert result == ["data:only"]

    def test_preserves_order(self):
        urls = [str(i) for i in range(20)]
        result = asyncio.run(fetch_all_async(urls))
        expected = [f"data:{u}" for u in urls]
        assert result == expected, (
            "Порядок должен сохраняться. "
            "Проверьте, что asyncio.gather() сохраняет порядок"
        )


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 4.3 — Смешивание sync и async
# ═══════════════════════════════════════════════════════════


class TestAsyncProcessNumbers:
    """Тесты для async_process_numbers()."""

    def test_returns_correct_values(self):
        numbers = [5, 10, 15]
        result = asyncio.run(async_process_numbers(numbers, max_workers=2))
        expected = [blocking_compute(n) for n in numbers]
        assert result == expected, f"Ожидали {expected}, получили {result}"

    def test_does_not_block_event_loop(self):
        """Проверяем, что event loop не блокируется."""

        async def run_test():
            coro = async_process_numbers([10, 20, 30], max_workers=2)
            return await asyncio.wait_for(coro, timeout=2.0)

        result = asyncio.run(run_test())
        assert len(result) == 3

    def test_concurrent_faster(self):
        """Больше workers — быстрее (в ThreadPoolExecutor)."""
        numbers = list(range(200, 300))

        start = time.perf_counter()
        result_1 = asyncio.run(async_process_numbers(numbers, max_workers=1))
        time_1 = time.perf_counter() - start

        start = time.perf_counter()
        result_4 = asyncio.run(async_process_numbers(numbers, max_workers=4))
        time_4 = time.perf_counter() - start

        assert result_1 == result_4, (
            "Результаты должны совпадать при разном max_workers"
        )
        assert time_4 < time_1 * 0.7, (
            f"max_workers=4 должен быть быстрее max_workers=1:\n"
            f"  workers=1: {time_1:.3f}s\n"
            f"  workers=4: {time_4:.3f}s\n"
        )

    def test_empty(self):
        result = asyncio.run(async_process_numbers([], max_workers=2))
        assert result == []
