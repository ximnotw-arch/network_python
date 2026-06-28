"""
Домашнее задание 4: Asyncio 🔄

Нужно обработать 1000 входящих HTTP-запросов.
ThreadPoolExecutor создаёт 1000 потоков — слишком много памяти.
Asyncio позволяет держать тысячи соединений в одном потоке.

Задания:
    4.1 — Базовый async/await
    4.2 — Параллельный запуск через asyncio.gather
    4.3 — Смешивание sync и async (asyncio.to_thread)

📖 См. лекцию 1, раздел 5 (Asyncio) и примеры:
   lectures/01_lecture/examples/04_asyncio/01_basic_coroutine.py
   lectures/01_lecture/examples/04_asyncio/02_gather.py
   lectures/01_lecture/examples/04_asyncio/03_tasks.py
"""


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 4.1 — Первая корутина
# ═══════════════════════════════════════════════════════════


async def fetch_one_async(url: str) -> str:
    """Асинхронно 'скачать' URL.

    Вместо time.sleep() используйте await asyncio.sleep().

    Требования:
        - Функция объявлена через async def
        - Возвращает f"data:{url}"
    """
    # TODO: реализуйте
    raise NotImplementedError


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 4.2 — Параллельный запуск
# ═══════════════════════════════════════════════════════════


async def fetch_all_async(urls: list[str]) -> list[str]:
    """Скачать все URL конкурентно.

    Требования:
        - Запустить fetch_one_async для каждого URL конкурентно
        - Вернуть результаты в порядке urls
    """
    # TODO: реализуйте
    raise NotImplementedError


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 4.3 — Смешивание sync и async (повышенная сложность)
# ═══════════════════════════════════════════════════════════


def blocking_compute(x: int) -> int:
    """CPU-bound функция: проверка на простоту.

    НЕ ИЗМЕНЯТЬ. Это синхронная блокирующая функция.
    """
    import math
    import time

    time.sleep(0.01)  # имитация тяжёлого вычисления
    for i in range(2, int(math.sqrt(x)) + 1):
        if x % i == 0:
            return 0
    return x  # простое число


async def async_process_numbers(numbers: list[int], max_workers: int = 4) -> list[int]:
    """Обработать числа, выгружая CPU-bound код в пул потоков.

    blocking_compute — блокирующая функция. Её нельзя вызывать
    напрямую в корутине — она заблокирует весь event loop.
    Нужно выгрузить её в отдельный поток через asyncio.to_thread().

    Требования:
        - Не блокировать event loop — выгрузить blocking_compute в пул потоков
        - Использовать asyncio.to_thread() или loop.run_in_executor()
        - max_workers: размер пула потоков
        - Результаты в порядке numbers
    """
    # TODO: реализуйте
    raise NotImplementedError
