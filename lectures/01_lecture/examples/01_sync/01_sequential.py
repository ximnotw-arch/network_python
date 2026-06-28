#!/usr/bin/env python3
"""
01_sync/01_sequential.py — базовый синхронный код: задачи выполняются строка за строкой.

Часть 1: имитация I/O через time.sleep()
Часть 2: реальные HTTP-запросы через httpx

Обе части показывают одну проблему: программа ждёт — процессор простаивает.
См. Fluent Python 2ed, гл. 20 (flags_sequential.py) — baseline 7.18s.

Запуск:
    python lectures/01_lecture/examples/01_sync/01_sequential.py
"""

import time
import sys

try:
    import httpx
except ImportError:
    print("Установите httpx: pip install httpx")
    sys.exit(1)

# Проверка сети: если httpbin недоступен — используем имитацию
ONLINE = True
try:
    httpx.get("https://httpbin.org/get", timeout=5)
except Exception:
    ONLINE = False


def make_request(url: str, delay: float) -> tuple[str, int, float]:
    """Реальный HTTP-запрос (или имитация, если сеть недоступна)."""
    if ONLINE:
        with httpx.Client() as client:
            resp = client.get(
                f"https://httpbin.org/delay/{delay}",
                timeout=30,
            )
            resp.raise_for_status()
            return url, len(resp.content), delay
    else:
        # Эмуляция через time.sleep
        time.sleep(delay)
        return url, 0, delay


def part1_simulation() -> None:
    """Часть 1: имитация I/O через time.sleep (как было раньше)."""
    print("  Часть 1: имитация I/O (time.sleep)")

    def step(name: str, delay: float) -> str:
        print(f"    [{name}] начал, работаю {delay}с...")
        time.sleep(delay)
        print(f"    [{name}] закончил")
        return f"{name} done"

    start = time.perf_counter()
    r1 = step("A", 1.0)
    r2 = step("B", 1.5)
    r3 = step("C", 0.5)
    elapsed = time.perf_counter() - start

    print(f"    Результаты: {r1}, {r2}, {r3}")
    print(f"  ⏱  {elapsed:.2f}с (сумма задержек = 3.0с)")
    print(f"  🟢 Процессор простаивал ~{elapsed - 0.001:.1f}с из {elapsed:.1f}с")
    print()


def part2_real_http() -> None:
    """Часть 2: реальные HTTP-запросы к httpbin.org (Ch20 baseline)."""
    print("  Часть 2: реальные HTTP-запросы (httpx)")

    delays = [1.0, 1.5, 0.5]
    urls = [f"req-{i}" for i in range(len(delays))]

    start = time.perf_counter()
    for url, d in zip(urls, delays):
        result_url, size, spent = make_request(url, d)
        print(f"    [{result_url}] {spent:.1f}с → {size} байт")
    elapsed = time.perf_counter() - start

    print(f"  ⏱  {elapsed:.2f}с (сумма задержек = {sum(delays)}с)")
    if ONLINE:
        print("  🟢 Реальные HTTP-запросы — процессор ждал ответа от сервера")
    print()


def main() -> None:
    print("01_sync/01_sequential: три задачи друг за другом")
    print("─" * 50)
    print()

    part1_simulation()
    part2_real_http()

    print("  Проблема в обоих случаях одна:")
    print("  CPU простаивает — программа блокируется на каждой операции.")
    print("  time.sleep() и httpx.get() — оба блокирующие вызовы.")
    print()


if __name__ == "__main__":
    main()
