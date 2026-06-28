"""Тесты к ДЗ 3: Multiprocessing."""

import sys
import os
import time

# Загружаем локальный task.py, а не закешированный из соседнего каталога
sys.path.insert(0, os.path.dirname(__file__))
if "task" in sys.modules:
    del sys.modules["task"]

from task import (
    compute_sequential,
    compute_parallel_pool,
    compute_with_threads,
)


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 3.1 — Пул процессов
# ═══════════════════════════════════════════════════════════


class TestComputeSequential:
    """Тесты для compute_sequential()."""

    def test_returns_correct_values(self):
        numbers = [5, 10, 15]
        result = compute_sequential(numbers)
        expected = [10, 17, 41]
        assert result == expected, f"Ожидали {expected}, получили {result}"

    def test_empty(self):
        assert compute_sequential([]) == []

    def test_single(self):
        assert compute_sequential([5]) == [10]


class TestComputeParallelPool:
    """Тесты для compute_parallel_pool()."""

    def test_returns_correct_values(self):
        numbers = [5, 10, 15]
        result = compute_parallel_pool(numbers, processes=2)
        expected = [10, 17, 41]
        assert result == expected

    def test_faster_than_sequential(self):
        """Тяжёлые вычисления на нескольких процессах быстрее."""
        numbers = [200000, 250000, 300000, 350000]

        start = time.perf_counter()
        seq_result = compute_sequential(numbers)
        seq_time = time.perf_counter() - start

        start = time.perf_counter()
        par_result = compute_parallel_pool(numbers, processes=4)
        par_time = time.perf_counter() - start

        assert seq_result == par_result, (
            "Результаты последовательного и параллельного вычисления должны совпадать"
        )

        assert par_time < seq_time * 0.8, (
            f"Параллельное вычисление (4 процесса) не быстрее "
            f"последовательного:\n"
            f"  sequential: {seq_time:.3f}s\n"
            f"  parallel:   {par_time:.3f}s"
        )

    def test_preserves_order(self):
        numbers = [10, 5, 15, 5]
        result = compute_parallel_pool(numbers, processes=2)
        expected = [17, 10, 41, 10]
        assert result == expected, (
            f"Порядок должен сохраняться: ожидали {expected}, получили {result}"
        )

    def test_empty(self):
        assert compute_parallel_pool([], processes=2) == []


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 3.2 — ThreadPool vs Pool
# ═══════════════════════════════════════════════════════════


class TestCompareThreadsAndProcesses:
    """ThreadPool должен быть медленнее Pool для CPU-bound."""

    def test_threads_are_slower_for_cpu(self):
        numbers = [200000, 250000, 300000, 350000]

        start = time.perf_counter()
        pool_result = compute_parallel_pool(numbers, processes=4)
        pool_time = time.perf_counter() - start

        start = time.perf_counter()
        thread_result = compute_with_threads(numbers, workers=4)
        thread_time = time.perf_counter() - start

        assert pool_result == thread_result, (
            "Результаты Pool и ThreadPool должны совпадать"
        )

        assert thread_time > pool_time * 1.5, (
            f"ThreadPool должен быть медленнее Pool для CPU-bound задач:\n"
            f"  multiprocessing.Pool: {pool_time:.3f}s\n"
            f"  ThreadPoolExecutor:   {thread_time:.3f}s\n"
            f"ThreadPoolExecutor должен быть хотя бы в 1.5× медленнее "
            f"из-за GIL"
        )
