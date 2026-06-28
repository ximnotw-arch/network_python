#!/usr/bin/env python3
"""
04_asyncio/01_basic_coroutine.py — база: корутины и await.

asyncio — кооперативная многозадачность в одном потоке.
Программа САМА решает, когда переключиться — в точках await.

Запуск:
    python lectures/01_lecture/examples_new/04_asyncio/01_basic_coroutine.py
"""

import asyncio


async def greet(name: str, delay: float) -> str:
    """Простая корутина: ждёт и возвращает приветствие."""
    print(f"   [greet-{name}] начало (жду {delay}с)")
    await asyncio.sleep(delay)  # не блокирует event loop!
    print(f"   [greet-{name}] конец")
    return f"Hello, {name}!"


async def main() -> None:
    print("04_asyncio/01_basic_coroutine: базовый await")
    print("=" * 50)

    # Прямой await — последовательно, как обычная функция
    result = await greet("Python", 0.5)
    print(f"   Результат: {result}")
    print("   (один await — никакого параллелизма)\n")

    # А вот asyncio.gather — уже конкурентно:
    print("   А теперь 3 корутины через gather:")
    results = await asyncio.gather(
        greet("Alice", 1.0),
        greet("Bob", 0.8),
        greet("Charlie", 1.2),
    )
    print(f"   Результаты: {results}")
    print("   asyncio.gather запускает их конкурентно, а не последовательно!")

    print("\n💡 Ключевое отличие от threading:")
    print("   Нет потоков — всё в одном потоке.")
    print("   await asyncio.sleep() — не блокирует, а 'уступает' управление.")


asyncio.run(main())
