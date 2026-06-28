#!/usr/bin/env python3
"""
04_asyncio/04_threading_and_asyncio.py — сочетание threading и asyncio.

Asyncio отлично справляется с I/O-bound задачами (тысячи корутин).
Но что делать, если в asyncio-программе появился блокирующий код?

  time.sleep() → блокирует весь event loop (все корутины встанут!)

Решение: выгрузить блокирующий код в пул потоков. Event loop продолжит
работать, а блокирующая функция выполнится в отдельном потоке вне GIL.

Три способа:
1. asyncio.to_thread(fn, arg) — простой, пул по умолчанию
2. loop.run_in_executor(pool, fn, arg) — явный пул с max_workers
3. run_in_executor() + ProcessPoolExecutor — для CPU-bound (обход GIL)

Запуск:
    python lectures/01_lecture/examples/04_asyncio/04_threading_and_asyncio.py
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


# ═══════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ
# ═══════════════════════════════════════════════════════════


def blocking_io(name: str, delay: float) -> str:
    """Блокирующая I/O-bound функция (time.sleep отпускает GIL)."""
    time.sleep(delay)
    return f"[{name}] done in {delay}s"


def blocking_cpu(n: int) -> int:
    """Блокирующая CPU-bound функция (GIL не отпускает)."""
    total = 0
    for i in range(2, n + 1):
        is_prime = True
        for j in range(2, int(i**0.5) + 1):
            if i % j == 0:
                is_prime = False
                break
        if is_prime:
            total += i
    return total


async def heartbeat(name: str, interval: float) -> None:
    """Фоновая корутина — тикает, пока идёт блокирующая работа."""
    try:
        while True:
            await asyncio.sleep(interval)
            print(f"   ♥ [{name}] event loop жив!")
    except asyncio.CancelledError:
        pass


# ═══════════════════════════════════════════════════════════
# ДЕМОНСТРАЦИЯ 1: asyncio.to_thread
# ═══════════════════════════════════════════════════════════


async def demo_to_thread() -> None:
    """Выгрузка блокирующего кода через asyncio.to_thread()."""
    print("\n" + "─" * 60)
    print("1. asyncio.to_thread() — блокирующий код в пуле потоков")
    print("   (time.sleep() отпускает GIL, потоки работают параллельно)")
    print("─" * 60)

    # Запускаем heartbeat — он докажет, что event loop не блокируется
    heart = asyncio.create_task(heartbeat("1", 0.2))

    start = time.perf_counter()

    # 3 блокирующих вызова — каждый "спит" по 1 секунде
    # to_thread выгружает их в ThreadPoolExecutor, event loop продолжается
    results = await asyncio.gather(
        asyncio.to_thread(blocking_io, "A", 1.0),
        asyncio.to_thread(blocking_io, "B", 0.8),
        asyncio.to_thread(blocking_io, "C", 1.2),
    )

    elapsed = time.perf_counter() - start
    heart.cancel()

    for r in results:
        print(f"   → {r}")
    print(f"⏱  {elapsed:.2f}с — потоки работали конкурентно!")
    print("   Если бы вызывать blocking_io без to_thread,")
    print("   event loop заблокировался бы на ~3с без heartbeat")


# ═══════════════════════════════════════════════════════════
# ДЕМОНСТРАЦИЯ 2: loop.run_in_executor с ограничением потоков
# ═══════════════════════════════════════════════════════════


async def demo_run_in_executor() -> None:
    """Явный ThreadPoolExecutor через loop.run_in_executor()."""
    print("\n" + "─" * 60)
    print("2. loop.run_in_executor() — явный пул с max_workers=2")
    print("   (контролируем число потоков, не перегружаем систему)")
    print("─" * 60)

    loop = asyncio.get_running_loop()
    heart = asyncio.create_task(heartbeat("2", 0.3))
    delays = [("X", 1.5), ("Y", 1.0), ("Z", 0.8), ("W", 1.2)]

    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks = [
            loop.run_in_executor(pool, blocking_io, name, delay)
            for name, delay in delays
        ]
        results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start
    heart.cancel()

    for r in results:
        print(f"   → {r}")
    print(f"⏱  {elapsed:.2f}с — максимум 2 потока одновременно")
    print("   Все 4 задачи выполнились за 2 волны по 2 потока")


# ═══════════════════════════════════════════════════════════
# ДЕМОНСТРАЦИЯ 3: ProcessPoolExecutor для CPU-bound
# ═══════════════════════════════════════════════════════════


async def demo_process_pool() -> None:
    """ProcessPoolExecutor — обход GIL для CPU-bound кода."""
    print("\n" + "─" * 60)
    print("3. loop.run_in_executor() + ProcessPoolExecutor")
    print("   (CPU-bound код — ThreadPool не поможет, нужны процессы)")
    print("─" * 60)

    loop = asyncio.get_running_loop()
    numbers = [200_000, 250_000, 300_000, 350_000]

    # ThreadPool — GIL не отпускается, толку нет
    heart_t = asyncio.create_task(heartbeat("thr", 0.3))
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        thread_results = await asyncio.gather(
            *[loop.run_in_executor(pool, blocking_cpu, n) for n in numbers]
        )
    thread_time = time.perf_counter() - start
    heart_t.cancel()

    # ProcessPool — реальный параллелизм (может не работать в песочнице)
    try:
        heart_p = asyncio.create_task(heartbeat("prc", 0.3))
        start = time.perf_counter()
        with ProcessPoolExecutor(max_workers=4) as pool:
            proc_results = await asyncio.gather(
                *[loop.run_in_executor(pool, blocking_cpu, n) for n in numbers]
            )
        proc_time = time.perf_counter() - start
        heart_p.cancel()

        print(f"   ThreadPool:  {thread_time:.2f}с (GIL — последовательно)")
        print(f"   ProcessPool: {proc_time:.2f}с (параллельно на ядрах)")
        print(f"   Ускорение:   {thread_time / max(proc_time, 0.001):.1f}×")
        print(f"   Результаты совпадают: {thread_results == proc_results}")
    except Exception as e:
        print(f"   ThreadPool:  {thread_time:.2f}с (GIL — последовательно)")
        print(f"   ProcessPool: не запустился ({e})")
        print("   (ProcessPoolExecutor ограничен в изолированном окружении)")
    print("   💡 ProcessPoolExecutor даёт реальный параллелизм CPU —")
    print("      каждый процесс имеет свой GIL и работает на отдельном ядре")


# ═══════════════════════════════════════════════════════════
# ДЕМОНСТРАЦИЯ 4: Сравнение — синхронный vs to_thread vs run_in_executor
# ═══════════════════════════════════════════════════════════


async def demo_comparison() -> None:
    """Сравнение трёх подходов с блокирующим кодом."""
    print("\n" + "─" * 60)
    print("4. Сравнение подходов")
    print("─" * 60)

    # Синхронно
    start = time.perf_counter()
    sync_results = [blocking_io("A", 0.5), blocking_io("B", 0.4), blocking_io("C", 0.3)]
    sync_time = time.perf_counter() - start

    # to_thread
    start = time.perf_counter()
    thread_results = await asyncio.gather(
        asyncio.to_thread(blocking_io, "A", 0.5),
        asyncio.to_thread(blocking_io, "B", 0.4),
        asyncio.to_thread(blocking_io, "C", 0.3),
    )
    thread_time = time.perf_counter() - start

    # run_in_executor с 2 потоками
    loop = asyncio.get_running_loop()
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:
        exec_results = await asyncio.gather(
            *[
                loop.run_in_executor(pool, blocking_io, *args)
                for args in [("A", 0.5), ("B", 0.4), ("C", 0.3)]
            ]
        )
    exec_time = time.perf_counter() - start

    print(f"   sync (time.sleep):   {sync_time:.2f}с — ждём всё подряд")
    print(f"   to_thread (default): {thread_time:.2f}с — конкурентно")
    print(f"   run_in_executor(2):  {exec_time:.2f}с — 2 потока")
    assert sync_results == thread_results == exec_results


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════


async def main() -> None:
    print("=" * 60)
    print("04_asyncio/04_threading_and_asyncio.py")
    print("Сочетание threading и asyncio")
    print("=" * 60)

    await demo_to_thread()
    await demo_run_in_executor()
    await demo_process_pool()
    await demo_comparison()

    print("\n" + "─" * 60)
    print("💡 ИТОГ:")
    print("   • asyncio.to_thread() — быстрый способ выгрузить блокирующий код")
    print("   • run_in_executor + ThreadPoolExecutor — контроль числа потоков")
    print("   • run_in_executor + ProcessPoolExecutor — настоящий параллелизм CPU")
    print("   • Event loop остаётся отзывчивым — heartbeat не замирает")
    print("─" * 60)


asyncio.run(main())
