#!/usr/bin/env python3
"""
02_threading/01_simple_thread.py — базовый запуск и join потока.

Сравнение: синхронный вызов vs поток.
В синхронном варианте ждём 3+2 = 5 секунд.
С потоком оба делаются «одновременно» — ~3 секунды.

Запуск:
    python lectures/01_lecture/examples_new/02_threading/01_simple_thread.py
"""

import threading
import time


def make_coffee(name: str, delay: float) -> None:
    print(f"  [{name}] ☕ Начал варить кофе (займёт {delay}с)")
    time.sleep(delay)
    print(f"  [{name}] ☕ Кофе готов!")


def read_news(name: str, delay: float) -> None:
    print(f"  [{name}] 📰 Начал читать новости (займёт {delay}с)")
    time.sleep(delay)
    print(f"  [{name}] 📰 Новости прочитаны!")


def main() -> None:
    print("02_threading/01_simple_thread: синхронно vs поток")
    print("=" * 55)

    # --- Синхронно ---
    print("\n🐢 Синхронно — делаем по порядку:")
    start = time.perf_counter()
    make_coffee("sync", 3)
    read_news("sync", 2)
    sync_time = time.perf_counter() - start
    print(f"   ⏱  {sync_time:.2f}с — пока варился кофе, новости не читались\n")

    # --- С потоками ---
    print("🚀 С потоками — параллельно:")
    t1 = threading.Thread(target=make_coffee, args=("th-1", 3))
    t2 = threading.Thread(target=read_news, args=("th-2", 2))

    start = time.perf_counter()
    t1.start()
    t2.start()
    t1.join()  # ждём кофе
    t2.join()  # ждём новости
    thread_time = time.perf_counter() - start
    print(f"   ⏱  {thread_time:.2f}с — кофе варился, пока читались новости!\n")

    print(f"📊 Ускорение: {sync_time / thread_time:.1f}")


if __name__ == "__main__":
    main()
