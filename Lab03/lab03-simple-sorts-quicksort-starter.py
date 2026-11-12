#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import math
import random
import statistics
import sys
import time
import traceback
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Сортировка пузырьком. Ожидаемая сложность: TODO (обосновать в отчёте).

    Подсказка: досрочный выход, если за проход не было ни одного обмена, —
    именно он даёт лучший случай на упорядоченном входе.
    """
    a = list(a)
    n = len(a)
    comparisons = 0
    swaps = 0
    for i in range(n-1):
        swapped = False
        for j in range(n-1-i):
            comparisons += 1
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return a, comparisons, swaps


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Сортировка вставками. Ожидаемая сложность: TODO (лучший/худший случаи)."""
    a = list(a)
    comparisons = 0
    shifts = 0
    for i in range(1, len(a)):
        current = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if a[j] > current:
                a[j+1] = a[j]
                shifts += 1
                j -= 1
            else:
                break
        a[j+1] = current
    return a, comparisons, shifts


def selection_sort(a: list) -> tuple[list, int, int]:
    """Сортировка выбором. Ожидаемая сложность: TODO (почему не зависит от входа?)."""
    a = list(a)
    n = len(a)
    comparisons = 0
    swaps = 0
    for i in range(n-1):
        smallest = i
        for j in range(i+1, n):
            comparisons += 1
            if a[j] < a[smallest]:
                smallest = j
        if smallest != i:
            a[i], a[smallest] = a[smallest], a[i]
            swaps += 1
    return a, comparisons, swaps


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """QuickSort с выбором опорного через rng.randrange. Возвращает новый список.

    Ожидаемая сложность: в среднем TODO, в худшем случае TODO (обосновать
    в отчёте, объяснить роль рандомизации). rng передаётся снаружи, чтобы
    запуск был воспроизводим по seed варианта.
    """
    if rng is None:
        rng = random.Random()
    a = list(a)
    stack = [(0, len(a))]
    while stack:
        lo, hi = stack.pop()
        if hi - lo < 2:
            continue
        pivot = a[rng.randrange(lo, hi)]
        lt, i, gt = lo, lo, hi
        while i < gt:
            if a[i] < pivot:
                a[lt], a[i] = a[i], a[lt]
                lt += 1
                i += 1
            elif a[i] > pivot:
                gt -= 1
                a[gt], a[i] = a[i], a[gt]
            else:
                i += 1
        if lt - lo > hi - gt:
            stack.append((lo, lt))
            stack.append((gt, hi))
        else:
            stack.append((gt, hi))
            stack.append((lo, lt))
    return a


# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


class Keyed:
    __slots__ = ("key", "label")

    def __init__(self, key, label):
        self.key = key
        self.label = label

    def __lt__(self, other):
        return self.key < other.key

    def __gt__(self, other):
        return self.key > other.key

    def __le__(self, other):
        return self.key <= other.key

    def __ge__(self, other):
        return self.key >= other.key

    def __eq__(self, other):
        return self.key == other.key

    def __repr__(self):
        return f"({self.key}, {self.label!r})"


STABILITY_PAIRS = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]


def labels_by_key(items: list) -> dict:
    groups = {}
    for item in items:
        groups.setdefault(item.key, []).append(item.label)
    return groups


def is_stable(fn) -> tuple[bool, dict]:
    pairs = [Keyed(k, lab) for k, lab in STABILITY_PAIRS]
    result = fn(pairs)
    got = labels_by_key(result)
    want = labels_by_key(pairs)
    return got == want, got


def stability_demo() -> None:
    """Показать, какие из четырёх сортировок стабильны.

    План: взять массив пар (ключ, метка) с повторяющимися ключами, например
    [(2, "a"), (1, "b"), (2, "c"), (1, "d")], отсортировать каждой сортировкой
    по ключу (сравнение только по p[0]!) и напечатать порядок меток при равных
    ключах. Вывод о стабильности каждой сортировки включить в отчёт.
    """
    print("\nstability_demo:")
    print(f"  вход: {STABILITY_PAIRS}")
    print(f"  исходный порядок меток при равных ключах: "
          f"{labels_by_key([Keyed(k, lab) for k, lab in STABILITY_PAIRS])}")
    for name, fn in ALGORITHMS.items():
        stable, got = is_stable(fn)
        verdict = "стабильна" if stable else "НЕ стабильна"
        print(f"  {name:<15} {got}  -> {verdict}")


# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def check_algorithm(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(is_sorted(res), f"нарушен порядок на {a}: получено {res}")
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        res = fn(list(a))
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")


def check_input_untouched() -> None:
    for name, fn in ALGORITHMS.items():
        a = [3, 1, 2, 5, 4]
        fn(a)
        expect(a == [3, 1, 2, 5, 4], f"{name}: изменён входной список")


def check_counters() -> None:
    """Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе."""
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    expect(comparisons == 10,
           f"selection_sort: неверный счётчик сравнений — {comparisons}, ожидалось 10")

    n = 50
    ordered = list(range(n))
    reverse = ordered[::-1]
    full = n * (n - 1) // 2

    _, c, s = bubble_sort(ordered)
    expect((c, s) == (n - 1, 0), f"bubble_sort на упорядоченном: ({c}, {s}), ожидалось ({n - 1}, 0)")
    _, c, s = bubble_sort(reverse)
    expect((c, s) == (full, full), f"bubble_sort на обратном: ({c}, {s}), ожидалось ({full}, {full})")

    _, c, s = insertion_sort(ordered)
    expect((c, s) == (n - 1, 0), f"insertion_sort на упорядоченном: ({c}, {s}), ожидалось ({n - 1}, 0)")
    _, c, s = insertion_sort(reverse)
    expect((c, s) == (full, full), f"insertion_sort на обратном: ({c}, {s}), ожидалось ({full}, {full})")

    for data in (ordered, reverse, random.Random(1).sample(range(1000), n)):
        _, c, s = selection_sort(data)
        expect(c == full, f"selection_sort: {c} сравнений, ожидалось {full}")
        expect(s <= n - 1, f"selection_sort: {s} обменов, больше n-1 = {n - 1}")

    rng = random.Random(2)
    for _ in range(50):
        a = [rng.randint(0, 20) for _ in range(rng.randint(0, 40))]
        inversions = sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])
        _, _, bs = bubble_sort(a)
        _, _, sh = insertion_sort(a)
        expect(bs == inversions, f"bubble_sort: обменов {bs}, инверсий {inversions} на {a}")
        expect(sh == inversions, f"insertion_sort: сдвигов {sh}, инверсий {inversions} на {a}")


def check_stability() -> None:
    for name in ("bubble_sort", "insertion_sort"):
        stable, got = is_stable(ALGORITHMS[name])
        expect(stable, f"{name} должна быть стабильной, получено {got}")
    stable, got = is_stable(ALGORITHMS["selection_sort"])
    expect(not stable, f"selection_sort ожидалась нестабильной на демонстрационном входе, получено {got}")


def check_quick_deterministic() -> None:
    a = [random.Random(3).randint(-50, 50) for _ in range(200)]
    expect(quick_sort(a, random.Random(59)) == quick_sort(a, random.Random(59)),
           "quick_sort: разный результат при одинаковом seed")
    big = list(range(20_000, 0, -1))
    expect(quick_sort(big, random.Random(0)) == sorted(big), "quick_sort: ошибка на большом обратном входе")


def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_algorithm(fn)) for name, fn in ALGORITHMS.items()]
    checks.append(("вход не меняется", check_input_untouched))
    checks.append(("счётчики", check_counters))
    checks.append(("стабильность", check_stability))
    checks.append(("quick_sort: seed и глубина", check_quick_deterministic))
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:  # noqa: BLE001 — падение реализации тоже результат проверки
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    # TODO: добавить собственные проверки (стабильность, счётчики пузырька и вставок)
    #       и описать их в отчёте.
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5
COUNTED = {"bubble_sort": bubble_sort, "insertion_sort": insertion_sort, "selection_sort": selection_sort}


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия: сортировка не должна получать свой результат
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def loglog_slope(sizes: list[int], times: list[float]) -> float:
    xs = [math.log(n) for n in sizes]
    ys = [math.log(max(t, 1e-9)) for t in times]
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den


def plot_results(results: dict, out_dir: Path) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    paths = []
    classes = ["упорядоченный", "случайный", "обратный"]
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    for ax, cls in zip(axes, classes):
        for name, by_class in results.items():
            sizes, times = by_class[cls]
            ax.loglog(sizes, times, "o-", label=f"{name} (k={loglog_slope(sizes, times):.2f})")
        ref_n = SIZES_QUADRATIC
        base = results["selection_sort"][cls][1][0]
        ax.loglog(ref_n, [base * (n / ref_n[0]) ** 2 for n in ref_n], "k--", alpha=0.4, label="O(n²)")
        qn = SIZES_QUICK
        qbase = results["quick_sort"][cls][1][0]
        ax.loglog(qn, [qbase * (n * math.log(n)) / (qn[0] * math.log(qn[0])) for n in qn],
                  "k:", alpha=0.4, label="O(n log n)")
        ax.set_title(f"вход: {cls}")
        ax.set_xlabel("n")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("время, с (медиана)")
    fig.suptitle("ЛР3: время сортировок, log-log")
    fig.tight_layout()
    path = out_dir / "lab03_loglog.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    paths.append(path)

    fig2, axes2 = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    for ax, cls in zip(axes2, classes):
        for name in COUNTED:
            sizes, times = results[name][cls]
            ax.loglog(sizes, times, "o-", label=name)
        ax.set_title(f"простые сортировки, вход: {cls}")
        ax.set_xlabel("n")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    axes2[0].set_ylabel("время, с (медиана)")
    fig2.tight_layout()
    path2 = out_dir / "lab03_simple.png"
    fig2.savefig(path2, dpi=150)
    plt.close(fig2)
    paths.append(path2)
    return paths


def run_benchmarks(seed: int) -> None:
    """Замеры всех алгоритмов на трёх классах входов; результат — таблица в stdout."""
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    results = {}
    counters = []
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        results[name] = {}
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                t = bench(fn, data)
                results[name].setdefault(cls, ([], []))
                results[name][cls][0].append(n)
                results[name][cls][1].append(t)
                print(f"  n={n:>7}  вход={cls:<13} t={t:.6f} c")
                if name in COUNTED:
                    _, c, s = COUNTED[name](data)
                    counters.append((name, n, cls, c, s))
    # TODO: построить log-log графики (matplotlib) по классам входов;
    # TODO: сопоставить наклоны с O(n^2) и O(n log n), объяснить расхождения
    #       (в т. ч. лучший случай вставок и поведение пузырька на упорядоченном входе);
    # TODO: включить в отчёт таблицы счётчиков сравнений/обменов.

    print("\nНаклоны log-log (k в t ~ n^k):")
    print(f"  {'алгоритм':<15} {'упорядоченный':>14} {'случайный':>10} {'обратный':>9}")
    for name, by_class in results.items():
        ks = [loglog_slope(*by_class[cls]) for cls in ("упорядоченный", "случайный", "обратный")]
        print(f"  {name:<15} {ks[0]:>14.2f} {ks[1]:>10.2f} {ks[2]:>9.2f}")

    print("\nСчётчики простых сортировок (сравнения / обмены или сдвиги):")
    print(f"  {'алгоритм':<15} {'n':>6} {'вход':<13} {'сравнения':>12} {'обмены':>12}")
    for name, n, cls, c, s in counters:
        print(f"  {name:<15} {n:>6} {cls:<13} {c:>12} {s:>12}")

    try:
        paths = plot_results(results, Path(__file__).resolve().parent)
    except ImportError:
        print("\nmatplotlib не установлен: графики не построены")
    else:
        print("\nГрафики сохранены:")
        for p in paths:
            print(f"  {p}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
