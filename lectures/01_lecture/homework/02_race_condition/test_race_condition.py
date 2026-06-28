"""Тесты к ДЗ 2: Race Condition и Lock."""

import sys
import os
import threading
import pytest

# Загружаем локальный task.py, а не закешированный из соседнего каталога
sys.path.insert(0, os.path.dirname(__file__))
if "task" in sys.modules:
    del sys.modules["task"]

from task import (
    increment_with_race,
    increment_safe,
    BankAccount,
    InsufficientFundsError,
)


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 2.1 — Имитация гонки
# ═══════════════════════════════════════════════════════════


class TestIncrementWithRace:
    """Тесты для increment_with_race()."""

    def test_race_condition_occurs(self):
        """Гонка должна проявляться: результат < 2 × times на 2 потоках."""
        counter = [0]
        times = 1000

        t1 = threading.Thread(target=increment_with_race, args=(counter, times))
        t2 = threading.Thread(target=increment_with_race, args=(counter, times))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert counter[0] < 2 * times, (
            f"Гонка не проявилась! Ожидали counter < {2 * times}, "
            f"получили {counter[0]}. Возможно, реализация "
            f"не создаёт race condition"
        )

    def test_single_thread_works(self):
        """Один поток — никакой гонки нет."""
        counter = [0]
        increment_with_race(counter, 100)
        assert counter[0] == 100, (
            f"Один поток должен дать 100 инкрементов, получили {counter[0]}"
        )


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 2.2 — Исправление через Lock
# ═══════════════════════════════════════════════════════════


class TestIncrementSafe:
    """Тесты для increment_safe()."""

    def test_no_race_condition(self):
        """С Lock гонки быть не должно."""
        counter = [0]
        lock = threading.Lock()
        times = 2000

        t1 = threading.Thread(target=increment_safe, args=(counter, times, lock))
        t2 = threading.Thread(target=increment_safe, args=(counter, times, lock))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert counter[0] == 2 * times, (
            f"С Lock должно быть ровно {2 * times}, "
            f"получили {counter[0]} — гонка не устранена"
        )

    def test_single_thread(self):
        """Один поток с Lock."""
        counter = [0]
        lock = threading.Lock()
        increment_safe(counter, 100, lock)
        assert counter[0] == 100

    def test_three_threads(self):
        """Три потока — тоже без гонки."""
        counter = [0]
        lock = threading.Lock()
        threads = [
            threading.Thread(target=increment_safe, args=(counter, 500, lock))
            for _ in range(3)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert counter[0] == 1500, (
            f"Три потока по 500: ожидали 1500, получили {counter[0]}"
        )


# ═══════════════════════════════════════════════════════════
# ЗАДАНИЕ 2.3 — Банковский счёт
# ═══════════════════════════════════════════════════════════


class TestBankAccount:
    """Тесты для BankAccount."""

    def test_deposit_and_balance(self):
        acc = BankAccount()
        acc.deposit(100)
        assert acc.get_balance() == 100.0, (
            f"Баланс после deposit(100): ожидали 100, получили {acc.get_balance()}"
        )

    def test_deposit_multiple(self):
        acc = BankAccount()
        acc.deposit(50)
        acc.deposit(30)
        assert acc.get_balance() == 80.0

    def test_withdraw_success(self):
        acc = BankAccount(100)
        acc.withdraw(40)
        assert acc.get_balance() == 60.0

    def test_withdraw_insufficient_funds(self):
        acc = BankAccount(50)
        with pytest.raises(InsufficientFundsError):
            acc.withdraw(100)
        assert acc.get_balance() == 50.0, (
            f"При InsufficientFundsError баланс не должен меняться: "
            f"ожидали 50, получили {acc.get_balance()}"
        )

    def test_initial_balance(self):
        acc = BankAccount(1000)
        assert acc.get_balance() == 1000.0

    def test_default_initial_balance(self):
        acc = BankAccount()
        assert acc.get_balance() == 0.0

    def test_deposit_zero(self):
        acc = BankAccount()
        acc.deposit(0)
        assert acc.get_balance() == 0.0

    def test_withdraw_zero(self):
        acc = BankAccount(100)
        acc.withdraw(0)
        assert acc.get_balance() == 100.0

    def test_thread_safety(self):
        """Множество потоков — без гонки."""
        acc = BankAccount(0)
        threads = [threading.Thread(target=acc.deposit, args=(10,)) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert acc.get_balance() == 100.0, (
            f"10 потоков по deposit(10): ожидали 100, "
            f"получили {acc.get_balance()} — возможна гонка"
        )

    def test_deposit_withdraw_concurrent(self):
        """Одновременный deposit и withdraw — без гонки."""
        acc = BankAccount(100)
        errors = []

        def depositer():
            for _ in range(20):
                acc.deposit(10)

        def withdrawer():
            for _ in range(20):
                try:
                    acc.withdraw(10)
                except InsufficientFundsError:
                    errors.append("fail")

        t1 = threading.Thread(target=depositer)
        t2 = threading.Thread(target=withdrawer)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert acc.get_balance() == 100.0, (
            f"20 deposit(10) + 20 withdraw(10): ожидали 100, "
            f"получили {acc.get_balance()} — возможна гонка"
        )

    def test_withdraw_exact_balance(self):
        """Снятие всех средств."""
        acc = BankAccount(100)
        acc.withdraw(100)
        assert acc.get_balance() == 0.0
