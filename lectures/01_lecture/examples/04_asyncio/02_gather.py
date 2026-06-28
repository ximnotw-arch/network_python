#!/usr/bin/env python3
"""
04_asyncio/02_gather.py — конкурентный запуск через asyncio.gather.

gather запускает несколько корутин конкурентно и ждёт все результаты.
Если одна упадёт с ошибкой — остальные отменяются (если не return_exceptions=True).

Запуск:
    python lectures/01_lecture/examples_new/04_asyncio/02_gather.py
"""

import asyncio


async def greet(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"Hello, {name}!"


async def main() -> None:
    print("04_asyncio/02_gather: asyncio.gather")
    print("=" * 55)

    start = asyncio.get_event_loop().time()

    results = await asyncio.gather(
        greet("Alice", 1.0),
        greet("Bob", 0.8),
        greet("Charlie", 1.2),
        greet("Diana", 0.5),
    )

    elapsed = asyncio.get_event_loop().time() - start
    for r in results:
        print(f"   {r}")
    print(f"⏱  {elapsed:.2f}с — против ~3.5с последовательно")

    # return_exceptions — не останавливаться на первой ошибке
    print("\n   С return_exceptions=True:")

    async def failing() -> str:
        await asyncio.sleep(0.2)
        raise ValueError("упс!")

    safe_results = await asyncio.gather(
        greet("Good", 0.3),
        failing(),
        greet("AlsoGood", 0.1),
        return_exceptions=True,
    )
    for r in safe_results:
        print(f"   {r!r}")

    print("\n💡 gather = запустить всё, подождать всё, собрать результаты.")


asyncio.run(main())
