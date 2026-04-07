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

# --- Таблица ---
x_tab = np.arange(-0.5, 1.51, 0.1)
f_tab  = np.array([f(x) for x in x_tab])
l_tab  = np.array([lagrange(x, x_nodes, y_nodes) for x in x_tab])
err    = np.abs(f_tab - l_tab)

print(f"{'x':>6} | {'f(x)':>8} | {'L4(x)':>8} | {'|f-L4|':>8}")
print("-" * 42)
for i, x in enumerate(x_tab):
    marker = " <- макс." if err[i] == err.max() else ""
    print(f"{x:>6.2f} | {f_tab[i]:>8.4f} | {l_tab[i]:>8.4f} | {err[i]:>8.4f}{marker}")
print("-" * 42)
print(f"\nМакс. погрешность : {err.max():.4f} при x = {x_tab[err.argmax()]:.2f}")
print(f"||f(x)||           = {np.max(np.abs(f_tab)):.4f}")
print(f"Относит. погрешн. = {err.max() / np.max(np.abs(f_tab)) * 100:.2f}%")

# --- График ---
x_smooth = np.linspace(-0.5, 1.5, 400)
f_smooth = np.array([f(x) for x in x_smooth])
l_smooth = np.array([lagrange(x, x_nodes, y_nodes) for x in x_smooth])

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9))
fig.suptitle("Лабораторная работа №2 — Вариант 8", fontsize=14, fontweight="bold")

# -- Верхний график: f(x) и L4(x) --
ax1.plot(x_smooth, f_smooth, color="#5c7ef7", linewidth=2.5, label="$f(x) = 2^x \\cos(4x) - x$")
ax1.plot(x_smooth, l_smooth, color="#f7a25c", linewidth=2.5, linestyle="--", label="$L_4(x)$ — многочлен Лагранжа")
ax1.scatter(x_nodes, y_nodes, color="#5cf0a0", s=80, zorder=5, label="Узлы интерполяции")
ax1.axhline(0, color="gray", linewidth=0.7, linestyle=":")
ax1.axvline(0, color="gray", linewidth=0.7, linestyle=":")
ax1.set_xlabel("x")
ax1.set_ylabel("y")
ax1.set_title("Графики $f(x)$ и $L_4(x)$")
ax1.legend()
ax1.grid(True, alpha=0.3)

# -- Нижний график: погрешность |f - L4| --
ax2.bar(x_tab, err, width=0.08, color="#f06580", alpha=0.85, label="$|f(x) - L_4(x)|$")
ax2.axvline(x_tab[err.argmax()], color="#f7c26a", linewidth=1.5,
            linestyle="--", label=f"Макс. при x = {x_tab[err.argmax()]:.2f}")
ax2.set_xlabel("x")
ax2.set_ylabel("|f − L₄|")
ax2.set_title("Погрешность аппроксимации")
ax2.legend()
ax2.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("lab2_variant8.png", dpi=150, bbox_inches="tight")
plt.show()
print("\nГрафик сохранён: lab2_variant8.png")