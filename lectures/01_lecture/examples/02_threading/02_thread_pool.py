#!/usr/bin/env python3
"""
02_threading/02_thread_pool.py — пул потоков (ThreadPoolExecutor).

Часть 1: executor.map() — как обычный map(), но конкурентно
Часть 2: executor.submit() + as_completed() — результаты по мере готовности
Часть 3: Race condition через ThreadPoolExecutor — разделяемое состояние

Запуск:
    python lectures/01_lecture/examples/02_threading/02_thread_pool.py
"""

import time
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import httpx
except ImportError:
    print("Установите httpx: pip install httpx")
    sys.exit(1)

# Проверка сети
ONLINE = True
try:
    httpx.get("https://httpbin.org/get", timeout=5)
except Exception:
    ONLINE = False


def fetch_url(url: str) -> tuple[str, float]:
    """Загрузка URL с имитацией или реальным HTTP."""
    if ONLINE:
        delay = float(url.split("/delay/")[1])
        with httpx.Client() as client:
            resp = client.get(url, timeout=30)
            resp.raise_for_status()
            return url, delay
    else:
        delay = hash(url) % 3 + 0.5  # от 0.5 до 3.5 с
        time.sleep(delay)
        return url, delay


def part1_executor_map() -> None:
    """executor.map() — как обычный map(), параллельно выполняется."""
    print("  Часть 1: executor.map()")

    if ONLINE:
        urls = [f"https://httpbin.org/delay/{d}" for d in [1.0, 0.8, 1.2, 0.5]]
    else:
        urls = [
            "https://api.example.com/users",
            "https://api.example.com/products",
            "https://api.example.com/orders",
            "https://api.example.com/settings",
        ]

    # Sync baseline
    start = time.perf_counter()
    for url in urls:
        fetch_url(url)
    sync_time = time.perf_counter() - start
    print(f"    🐢 Sync (последовательно): {sync_time:.2f}с")

    # ThreadPoolExecutor.map()
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = pool.map(fetch_url, urls)
    pool_time = time.perf_counter() - start

    for url, delay in results:
        print(f"    ✓ {url:45s} — {delay:.1f}с")
    print(f"    🚀 ThreadPool.map (4 workers): {pool_time:.2f}с")
    print(f"    📊 Ускорение: {sync_time / pool_time:.1f}×")
    print()


def part2_as_completed() -> None:
    """executor.submit() + as_completed() — результаты по мере готовности.

    Future → URL словарь позволяет понять, какая задача завершилась.
    """
    print("  Часть 2: executor.submit() + as_completed()")

    if ONLINE:
        delays = [1.0, 0.5, 1.5, 0.8, 0.3]
        urls = [f"https://httpbin.org/delay/{d}" for d in delays]
    else:
        urls = [
            "https://api.example.com/a",
            "https://api.example.com/b",
            "https://api.example.com/c",
            "https://api.example.com/d",
        ]

    with ThreadPoolExecutor(max_workers=4) as pool:
        future_to_url = {pool.submit(fetch_url, url): url for url in urls}

        print(f"    Запущено {len(future_to_url)} задач, ждём результаты:\n")

        # as_completed отдаёт Future по мере завершения (не в порядке запуска)
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                _, delay = future.result()
                print(f"    ✅ {url:45s} — готов за {delay:.1f}с")
            except Exception as exc:
                print(f"    ❌ {url:45s} — ошибка: {exc}")

    print()
    print("    💡 as_completed отдаёт результаты по мере готовности,")
    print("       а не в порядке запуска. Быстрые запросы приходят первыми.")


def part3_race_condition() -> None:
    """Race condition с ThreadPoolExecutor — разделяемое состояние.

    Потоки из пула одновременно инкрементируют общий счётчик.
    `shared += 1` — это ТРИ шага (read → add → write), между которыми
    может вмешаться другой поток и прочитать устаревшее значение.

    В CPython переключение потоков может произойти в любой момент.
    Если между read и write случилось переключение — один инкремент
    потерян. `time.sleep(0)` форсирует переключение, делая гонку
    видимой (как если бы между read и write был сетевой запрос).
    """
    print("  Часть 3: Race condition в ThreadPoolExecutor\n")

    N = 20_000
    expected = N * 4

    # Без гонки: каждый поток работает со своим счётчиком
    def sum_chunk(n: int) -> int:
        total = 0
        for _ in range(n):
            total += 1
        return total

    with ThreadPoolExecutor(max_workers=4) as pool:
        partials = list(pool.map(sum_chunk, [N] * 4))
    print(f"    ✅ Без гонки (локальные суммы): {sum(partials)} = {expected}")
    print()

    # Race condition: все потоки инкрементят ОДИН счётчик
    # Между чтением `shared` и записью может переключиться другой поток
    shared: int = 0

    def sum_race(n: int) -> None:
        nonlocal shared
        for _ in range(n):
            current = shared  # read
            time.sleep(0)  # yeild GIL — может переключиться другой поток
            shared = current + 1  # write

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(sum_race, [N] * 4))
    print(f"    ❌ С гонкой (общий счётчик): {shared} ≠ {expected}")
    print(f"       Потеряно: {expected - shared}")
    print()

    # С Lock — всё корректно
    locked: int = 0
    lock = threading.Lock()

    def sum_locked(n: int) -> None:
        nonlocal locked
        for _ in range(n):
            with lock:
                locked += 1

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(sum_locked, [N] * 4))
    print(f"    ✅ С Lock (общий счётчик): {locked} = {expected}")
    print()

    print("    💡 ThreadPoolExecutor.map/submit НЕ защищает от гонок —")
    print("       потоки всё равно делят память. `shared += 1` — это")
    print("       LOAD → ADD → STORE. Между ними может вмешаться")
    print("       другой поток и прочитать устаревшее значение.")
    print("       Lock или раздельные данные — единственный выход.")
    print()
    print("    💡 time.sleep(0) здесь форсирует переключение контекста.")
    print("       В реальном коде роль sleep играют I/O-операции,")
    print("       обращения к сети/диску. Без них GIL в Python 3.14+")
    print("       редко переключается на горячих циклах, но логическая")
    print("       неатомарность `shared += 1` никуда не делась.")


def main() -> None:
    print("02_threading/02_thread_pool: пул потоков (ThreadPoolExecutor)")
    print("=" * 55)
    print()

    # part1_executor_map()
    # part2_as_completed()
    part3_race_condition()

    print("📌 Три вывода:")
    print("   executor.map() — порядок сохранён, но ждём все")
    print("   executor.submit() + as_completed() — по готовности, с dict-to-future")
    print("   ThreadPoolExecutor не спасает от race condition — нужен Lock")


if __name__ == "__main__":
    main()
