#!/usr/bin/env python3
"""
01_sync/02_io_vs_cpu.py — разница между I/O-bound и CPU-bound задачами.

Ключевая идея: тип задачи определяет, какой инструмент ускорения выбрать.
- I/O-bound: программа ждёт (сеть, диск, БД) — процессор свободен
- CPU-bound: программа считает (расчёты, обработка) — процессор занят

Запуск:
    python lectures/01_lecture/examples_new/01_sync/02_io_vs_cpu.py
"""

import time
import math


def io_bound_task(name: str, delay: float) -> str:
    """I/O-bound: в основном ждём (имитация запроса к API)."""
    time.sleep(delay)
    return f"[{name}] готов после {delay}с ожидания"


def cpu_bound_task(n: int) -> int:
    """CPU-bound: всё время считаем простые числа."""
    count = 0
    for num in range(2, n + 1):
        if all(num % i != 0 for i in range(2, int(math.sqrt(num)) + 1)):
            count += 1
    return count


def main() -> None:
    print("01_sync/02_io_vs_cpu: два типа задач")
    print("=" * 55)

    # -- I/O-bound --
    print("\n🔵 I/O-bound: 4 задачи по 1с ожидания")
    start = time.perf_counter()
    for i in range(4):
        io_bound_task(f"IO-{i}", 1.0)
    io_time = time.perf_counter() - start
    print(f"   ⏱  {io_time:.2f}с — процессор работал <0.01с, остальное простой\n")

    # -- CPU-bound --
    print("🔴 CPU-bound: считаем простые числа до 200 000")
    start = time.perf_counter()
    cpu_bound_task(200_000)
    cpu_time = time.perf_counter() - start
    print(f"   ⏱  {cpu_time:.2f}с — процессор загружен всё время\n")

    print("─" * 55)
    print("Вывод:")
    print("  I/O-bound: ускорение через threading или asyncio (ждём → переключаемся)")
    print("  CPU-bound: ускорение только через multiprocessing (считаем → параллелим)")
    print("  threading НЕ ускоряет CPU-bound из-за GIL (см. 02_threading/)")


if __name__ == "__main__":
    main()
