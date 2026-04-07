import pandas as pd
import matplotlib.pyplot as plt
import math

# ─────────────────────────────────────────────
# Задание: импорт файла
# ─────────────────────────────────────────────
# В Google Colab путь: /content/1.txt
# Здесь используем локальный путь
PATH = '/home/claude/1.txt'

df = pd.read_csv(PATH, encoding='utf-16-le', sep='\t', index_col=0)

# ─────────────────────────────────────────────
# pd.head — вывод 7 строк
# ─────────────────────────────────────────────
print("=== pd.head(7) ===")
print(df.head(7))
print()

# ─────────────────────────────────────────────
# pd.describe — статистические характеристики
# ─────────────────────────────────────────────
print("=== pd.describe() ===")
print(df.describe())
print()

# ─────────────────────────────────────────────
# Собственные функции расчёта параметров
# ─────────────────────────────────────────────

def my_count(data):
    """Количество элементов"""
    return len(data)

def my_mean(data):
    """Среднее арифметическое"""
    return sum(data) / len(data)

def my_std(data):
    """Стандартное отклонение (как в pandas — ddof=1)"""
    m = my_mean(data)
    variance = sum((x - m) ** 2 for x in data) / (len(data) - 1)
    return math.sqrt(variance)

def my_min(data):
    """Минимальное значение"""
    result = data[0]
    for x in data:
        if x < result:
            result = x
    return result

def my_max(data):
    """Максимальное значение"""
    result = data[0]
    for x in data:
        if x > result:
            result = x
    return result

def my_percentile(data, p):
    """Квантиль p (0..100)"""
    sorted_data = sorted(data)
    n = len(sorted_data)
    index = (p / 100) * (n - 1)
    lower = int(index)
    upper = lower + 1
    if upper >= n:
        return sorted_data[-1]
    frac = index - lower
    return sorted_data[lower] + frac * (sorted_data[upper] - sorted_data[lower])

# Проверка на простой последовательности
test = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
print("=== Проверка функций на тестовой последовательности [10..100] ===")
print(f"count : {my_count(test)}")
print(f"mean  : {my_mean(test)}")
print(f"std   : {my_std(test):.4f}")
print(f"min   : {my_min(test)}")
print(f"25%   : {my_percentile(test, 25)}")
print(f"50%   : {my_percentile(test, 50)}")
print(f"75%   : {my_percentile(test, 75)}")
print(f"max   : {my_max(test)}")
print()

# ─────────────────────────────────────────────
# Основная функция: расчёт параметров для всех дисциплин
# ─────────────────────────────────────────────

def my_describe(dataframe):
    """
    Аналог pd.describe().
    Возвращает DataFrame с параметрами для каждой дисциплины.
    """
    columns = list(dataframe.columns)          # 12.1 список столбцов

    counts, means, stds = [], [], []
    mins, q25s, q50s, q75s, maxs = [], [], [], [], []

    for col in columns:                        # 12.2 цикл по столбцам
        data = list(dataframe[col])
        counts.append(my_count(data))
        means.append(round(my_mean(data), 6))
        stds.append(round(my_std(data), 6))
        mins.append(my_min(data))
        q25s.append(my_percentile(data, 25))
        q50s.append(my_percentile(data, 50))
        q75s.append(my_percentile(data, 75))
        maxs.append(my_max(data))

    # 12.3 создать DataFrame как у pd.describe
    result = pd.DataFrame(
        [counts, means, stds, mins, q25s, q50s, q75s, maxs],
        index=['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'],
        columns=columns
    )
    return result

print("=== my_describe() — собственная функция ===")
print(my_describe(df))
print()

# ─────────────────────────────────────────────
# График зависимости оценок по датам
# ─────────────────────────────────────────────

plt.figure(figsize=(14, 6))
for col in df.columns:
    plt.plot(df.index, df[col], label=col, marker='o', markersize=3)

plt.title('Динамика оценок по дисциплинам')
plt.xlabel('Дата')
plt.ylabel('Оценка')
plt.legend()

# 13.2 — каждая вторая дата, повёрнутая на 90°
plt.xticks(df.index[::2], rotation=90)
plt.tight_layout()
plt.savefig('/home/claude/plot_lines.png', dpi=120)
plt.close()
print("График сохранён: plot_lines.png")

# ─────────────────────────────────────────────
# Гистограмма распределения оценок (14)
# ─────────────────────────────────────────────

# Собираем все оценки из всех дисциплин в один список
all_scores = []
for col in df.columns:
    all_scores.extend(list(df[col]))

# 14.1 четыре диапазона
bins = [0, 25, 50, 75, 100]
labels = ['0–25', '26–50', '51–75', '76–100']
frequencies = [0, 0, 0, 0]

for score in all_scores:
    if score <= 25:
        frequencies[0] += 1
    elif score <= 50:
        frequencies[1] += 1
    elif score <= 75:
        frequencies[2] += 1
    else:
        frequencies[3] += 1

# Накопленная частота
cumulative = []
total = 0
for f in frequencies:
    total += f
    cumulative.append(total)

plt.figure(figsize=(8, 5))
plt.bar(labels, cumulative, color=['#4e79a7', '#f28e2b', '#e15759', '#76b7b2'], edgecolor='black')
plt.title('Гистограмма распределения оценок (накопленная частота)')
plt.xlabel('Диапазон оценок')
plt.ylabel('Накопленная частота')
for i, v in enumerate(cumulative):
    plt.text(i, v + 1, str(v), ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig('/home/claude/plot_histogram.png', dpi=120)
plt.close()
print("Гистограмма сохранена: plot_histogram.png")
print()
print("Частоты по диапазонам:", dict(zip(labels, frequencies)))
print("Накопленные частоты:  ", dict(zip(labels, cumulative)))
