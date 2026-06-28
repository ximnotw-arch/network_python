#!/usr/bin/env python3
"""
04_asyncio/03_tasks.py — фоновые задачи (asyncio.create_task).

create_task запускает корутину в фоне — она выполняется конкурентно
с остальным кодом, пока мы не дойдём до await.

Разница с gather: задачи запускаются по одной, и между их запусками
можно делать что-то ещё.

Запуск:
    python lectures/01_lecture/examples_new/04_asyncio/03_tasks.py
"""

import asyncio


async def background_counter(name: str, n: int) -> str:
    """Фоновая задача, которая 'считает' с задержками."""
    for i in range(n):
        print(f"   [{name}] шаг {i + 1}/{n}")
        await asyncio.sleep(0.3)
    return f"{name} завершён"


async def main() -> None:
    print("04_asyncio/03_tasks: asyncio.create_task")
    print("=" * 55)

    # Запускаем две фоновые задачи
    task_a = asyncio.create_task(background_counter("A", 3))
    task_b = asyncio.create_task(background_counter("B", 2))

    # Пока задачи работают, можно делать что-то ещё
    print("   [main] Задачи запущены в фоне, жду их завершения...\n")
    await asyncio.sleep(0.2)
    print("   [main] Ещё успеваю что-то сделать, пока задачи крутятся!\n")

    # Ждём обе задачи
    results = await asyncio.gather(task_a, task_b)
    print(f"\n   {results[0]}, {results[1]}")

    print("\n💡 create_task: задача стартует немедленно и бежит в фоне.")
    print("   Пока она выполняется — мы можем делать другую работу.")
    print("   В threading так не получится — там join() блокирует.")


asyncio.run(main())
