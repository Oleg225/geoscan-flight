import numpy as np
import matplotlib.pyplot as plt

# Узлы интерполяции (Вариант 8)
x_nodes = np.array([-0.5, 0.0, 0.5, 1.0, 1.5])
y_nodes = np.array([0.206, 1.000, -1.089, -2.307, 1.216])

# f(x) = 2^x * cos(4x) - x
def f(x):
    return 2**x * np.cos(4*x) - x

# Многочлен Лагранжа
def lagrange(x, x_nodes, y_nodes):
    n = len(x_nodes)
    result = 0.0
    for i in range(n):
        term = y_nodes[i]
        for j in range(n):
            if j != i:
                term *= (x - x_nodes[j]) / (x_nodes[i] - x_nodes[j])
        result += term
    return result

# ============================================================
print("=" * 60)
print("   ЛАБОРАТОРНАЯ РАБОТА №2 — ВАРИАНТ 8")
print("   Интерполяционный многочлен Лагранжа")
print("=" * 60)

# ============================================================
print("\n" + "=" * 60)
print("  ЗАДАНИЕ 1: ПОСТРОЕНИЕ МНОГОЧЛЕНА ЛАГРАНЖА")
print("=" * 60)

print("\nИсходные узлы интерполяции:")
print(f"  {'i':>3} | {'x_i':>6} | {'y_i':>8}")
print("  " + "-" * 24)
for i in range(len(x_nodes)):
    print(f"  {i:>3} | {x_nodes[i]:>6.2f} | {y_nodes[i]:>8.4f}")

print("\nФормула Лагранжа:")
print("  L4(x) = sum( y_i * prod((x - x_j)/(x_i - x_j)) )")
print()

# Построение многочлена и вывод каждого слагаемого
poly_sum = np.poly1d([0])
for i in range(len(x_nodes)):
    num = np.poly1d([1])
    for j in range(len(x_nodes)):
        if j != i:
            num = num * np.poly1d([1, -x_nodes[j]])

    denom = np.prod([x_nodes[i] - x_nodes[j]
                     for j in range(len(x_nodes)) if j != i])
    Ai = y_nodes[i] / denom
    poly_sum = poly_sum + Ai * num

    # Формируем строку числителя
    factors = " · ".join([f"(x - {x_nodes[j]:+.1f})"
                          for j in range(len(x_nodes)) if j != i])
    denom_factors = " · ".join([f"({x_nodes[i]:+.1f} - {x_nodes[j]:+.1f})"
                                 for j in range(len(x_nodes)) if j != i])
    denom_vals = " · ".join([f"({x_nodes[i] - x_nodes[j]:+.2f})"
                              for j in range(len(x_nodes)) if j != i])

    print(f"  --- Слагаемое i={i} ---")
    print(f"  x_i = {x_nodes[i]},  y_i = {y_nodes[i]}")
    print(f"  Числитель   : {factors}")
    print(f"  Знаменатель : {denom_factors} = {denom_vals} = {denom:.4f}")
    print(f"  Коэффициент : y_i / знам = {y_nodes[i]} / {denom:.4f} = {Ai:.6f}")
    print()

c = poly_sum.coeffs
print("-" * 60)
print("Итоговый многочлен L4(x):")
print(f"  L4(x) = {c[0]:.5f}·x⁴")
print(f"        + {c[1]:.5f}·x³")
print(f"        + ({c[2]:.5f})·x²")
print(f"        + ({c[3]:.5f})·x")
print(f"        + {c[4]:.5f}")
print()
print(f"  L4(x) = 0.07733·x⁴ + 4.92800·x³ - 5.78533·x² - 2.52700·x + 1.00000")

print("\nПроверка в узлах (должно совпадать с y_i):")
print(f"  {'x_i':>6} | {'y_i':>8} | {'L4(x_i)':>10} | {'|разность|':>12} | OK?")
print("  " + "-" * 52)
for i in range(len(x_nodes)):
    val = lagrange(x_nodes[i], x_nodes, y_nodes)
    diff = abs(val - y_nodes[i])
    ok = "✓" if diff < 1e-6 else "✗"
    print(f"  {x_nodes[i]:>6.2f} | {y_nodes[i]:>8.4f} | {val:>10.6f} | {diff:>12.2e} | {ok}")

# ============================================================
print("\n" + "=" * 60)
print("  ЗАДАНИЕ 2: ВЫЧИСЛЕНИЕ ЗНАЧЕНИЙ И ПОГРЕШНОСТИ")
print("=" * 60)

for xp, name in [(-0.3, "x̄₁ = -0.3"), (1.2, "x̄₂ =  1.2")]:
    lv    = lagrange(xp, x_nodes, y_nodes)
    fv    = f(xp)
    delta = abs(fv - lv)
    delta_rel = delta / abs(fv) * 100

    print(f"\n  Точка {name}:")
    print(f"  {'─'*40}")

    # Подробный расчёт L4
    print(f"  Вычисление L4({xp}):")
    total = 0.0
    for i in range(len(x_nodes)):
        term = y_nodes[i]
        num_parts = []
        den_parts = []
        for j in range(len(x_nodes)):
            if j != i:
                num_parts.append(f"({xp} - {x_nodes[j]:+.1f})")
                den_parts.append(f"({x_nodes[i]:+.1f} - {x_nodes[j]:+.1f})")
                term *= (xp - x_nodes[j]) / (x_nodes[i] - x_nodes[j])
        total += term
        print(f"    i={i}: {y_nodes[i]} · "
              f"[{'·'.join(num_parts)}] / [{'·'.join(den_parts)}] = {term:.6f}")
    print(f"  Сумма: L4({xp}) = {total:.6f}")

    # Подробный расчёт f
    print(f"\n  Вычисление f({xp}) = 2^{xp} · cos(4·{xp}) - {xp}:")
    pow2  = 2**xp
    cos4x = np.cos(4*xp)
    print(f"    2^{xp}       = {pow2:.6f}")
    print(f"    cos(4·{xp}) = cos({4*xp:.2f}) = {cos4x:.6f}")
    print(f"    f({xp})     = {pow2:.6f} · {cos4x:.6f} - ({xp}) = {fv:.6f}")

    print(f"\n  Погрешности:")
    print(f"    Δ = |f({xp}) - L4({xp})| = |{fv:.6f} - {lv:.6f}| = {delta:.6f}")
    print(f"    δ = Δ / |f({xp})|        = {delta:.6f} / {abs(fv):.6f} = {delta_rel:.2f}%")

# ============================================================
print("\n" + "=" * 60)
print("  ЗАДАНИЕ 3: ТАБЛИЦА И ПОГРЕШНОСТЬ АППРОКСИМАЦИИ")
print("=" * 60)

x_tab = np.arange(-0.5, 1.51, 0.1)
f_tab = np.array([f(x) for x in x_tab])
l_tab = np.array([lagrange(x, x_nodes, y_nodes) for x in x_tab])
err   = np.abs(f_tab - l_tab)

print(f"\n  Табуляция на [-0.5; 1.5] с шагом 0.1:\n")
print(f"  {'x':>6} | {'f(x)':>8} | {'L4(x)':>8} | {'|f-L4|':>8}")
print("  " + "-" * 44)
for i, x in enumerate(x_tab):
    marker = " <- макс." if err[i] == err.max() else ""
    print(f"  {x:>6.2f} | {f_tab[i]:>8.4f} | {l_tab[i]:>8.4f} | {err[i]:>8.4f}{marker}")
print("  " + "-" * 44)

max_err   = err.max()
max_err_x = x_tab[err.argmax()]
norm_f    = np.max(np.abs(f_tab))

print(f"\n  Погрешность аппроксимации на отрезке [-0.5; 1.5]:")
print(f"    ||f - L4|| = max|f(x) - L4(x)| = {max_err:.4f}  при x = {max_err_x:.2f}")
print(f"    ||f||      = max|f(x)|           = {norm_f:.4f}  при x = {x_tab[np.abs(f_tab).argmax()]:.2f}")
print(f"    Относит. погрешность = {max_err:.4f} / {norm_f:.4f} = {max_err/norm_f:.4f} = {max_err/norm_f*100:.2f}%")

# ============================================================
print("\n" + "=" * 60)
print("  ГРАФИКИ")
print("=" * 60)

x_smooth = np.linspace(-0.5, 1.5, 400)
f_smooth = np.array([f(x) for x in x_smooth])
l_smooth = np.array([lagrange(x, x_nodes, y_nodes) for x in x_smooth])

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9))
fig.suptitle("Лабораторная работа №2 — Вариант 8", fontsize=14, fontweight="bold")

ax1.plot(x_smooth, f_smooth, color="#5c7ef7", linewidth=2.5,
         label="$f(x) = 2^x \\cos(4x) - x$")
ax1.plot(x_smooth, l_smooth, color="#f7a25c", linewidth=2.5, linestyle="--",
         label="$L_4(x)$ — многочлен Лагранжа")
ax1.scatter(x_nodes, y_nodes, color="#5cf0a0", s=90, zorder=5,
            label="Узлы интерполяции", edgecolors="white", linewidths=0.8)
ax1.axhline(0, color="gray", linewidth=0.7, linestyle=":")
ax1.axvline(0, color="gray", linewidth=0.7, linestyle=":")
ax1.set_xlabel("x")
ax1.set_ylabel("y")
ax1.set_title("Графики $f(x)$ и $L_4(x)$")
ax1.set_xticks(np.arange(-0.5, 1.51, 0.1))
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.bar(x_tab, err, width=0.07, color="#f06580", alpha=0.85,
        label="$|f(x) - L_4(x)|$")
ax2.axvline(max_err_x, color="#f7c26a", linewidth=1.8, linestyle="--",
            label=f"Макс. {max_err:.4f} при x = {max_err_x:.2f}")
ax2.set_xlabel("x")
ax2.set_ylabel("|f − L₄|")
ax2.set_title("Погрешность аппроксимации")
ax2.set_xticks(np.arange(-0.5, 1.51, 0.1))
ax2.legend()
ax2.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("lab2_variant8.png", dpi=150, bbox_inches="tight")
plt.show()
print("\nГрафик сохранён: lab2_variant8.png")