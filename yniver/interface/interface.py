import tkinter as tk
from tkinter import messagebox
import math

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# f(x) = e^(2x) - x - 2 = 0
def f(x):   return math.exp(2*x) - x - 2
def df(x):  return 2*math.exp(2*x) - 1
def d2f(x): return 4*math.exp(2*x)

EPS      = 0.001
MAX_ITER = 10000

# ── Отделение корней ──────────────────────────────────────────────────────────
def separate_roots(x_min=-5.0, x_max=5.0, steps=1000):
    h = (x_max - x_min) / steps
    intervals = []
    xp = x_min
    try: fp = f(xp)
    except: fp = None
    for i in range(1, steps + 1):
        xc = x_min + i * h
        try: fc = f(xc)
        except: fp = None; xp = xc; continue
        if fp is not None and fp * fc < 0:
            intervals.append((round(xp, 4), round(xc, 4)))
        fp = fc; xp = xc
    return intervals

# ── Численные методы ──────────────────────────────────────────────────────────
def bisection(a, b, eps=EPS):
    if f(a)*f(b) > 0:
        raise ValueError("f(a) и f(b) одного знака")
    n = 0
    while (b - a)/2 > eps:
        mid = (a + b)/2
        if f(mid) == 0: break
        if f(a)*f(mid) < 0: b = mid
        else: a = mid
        n += 1
        if n > MAX_ITER: break
    return (a+b)/2, n

def bisection_trace(a, b, eps=EPS):
    if f(a)*f(b) > 0:
        raise ValueError("f(a) и f(b) одного знака")
    history = []
    n = 0
    while (b - a)/2 > eps:
        mid = (a + b)/2
        history.append((a, b, mid))
        if f(mid) == 0: break
        if f(a)*f(mid) < 0: b = mid
        else: a = mid
        n += 1
        if n > MAX_ITER: break
    history.append((a, b, (a+b)/2))
    return history

def chord(a, b, eps=EPS):
    if f(a)*f(b) > 0:
        raise ValueError("f(a) и f(b) одного знака")
    n = 0
    x = a - f(a)*(b-a)/(f(b)-f(a))
    while True:
        if f(a)*f(x) < 0: b = x
        else: a = x
        x_new = a - f(a)*(b-a)/(f(b)-f(a))
        n += 1
        if abs(x_new - x) < eps or n > MAX_ITER: break
        x = x_new
    return x_new, n

def newton(a, b, eps=EPS):
    x = a if f(a)*d2f(a) > 0 else b
    n = 0
    while True:
        dfx = df(x)
        if dfx == 0: raise ValueError("Производная равна нулю")
        x_new = x - f(x)/dfx
        n += 1
        if abs(x_new - x) < eps or n > MAX_ITER: break
        x = x_new
    return x_new, n

def combined(a, b, eps=EPS):
    if f(a)*f(b) > 0:
        raise ValueError("f(a) и f(b) одного знака")
    xc = a if f(a)*d2f(a) < 0 else b
    xt = a if f(a)*d2f(a) > 0 else b
    n = 0
    while True:
        xc_new = xc - f(xc)*(xt-xc)/(f(xt)-f(xc))
        xt_new = xt - f(xt)/df(xt)
        n += 1
        if abs(xt_new - xc_new) < eps or n > MAX_ITER: break
        xc, xt = xc_new, xt_new
    return (xt_new + xc_new)/2, n

def fixed_point(a, b, eps=EPS):
    mid = (a + b)/2
    if mid < 0:
        lam = 1.0 / (2*math.exp(2*max(abs(a), abs(b))) + 1)
        x = mid; n = 0
        while True:
            x_new = x - lam*f(x); n += 1
            if abs(x_new - x) < eps or n > MAX_ITER: break
            x = x_new
        return x_new, n
    else:
        x = mid; n = 0
        while True:
            x_new = math.log(x + 2)/2; n += 1
            if abs(x_new - x) < eps or n > MAX_ITER: break
            x = x_new
        return x_new, n

# ── GUI ───────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Численное решение нелинейного уравнения  x + 2 = e^(2x)")
        self.resizable(False, False)
        self._build()

    def _build(self):
        F = ("Courier New", 10)
        FB = ("Courier New", 10, "bold")
        pad = dict(padx=8, pady=3)

        # ── Заголовок ─────────────────────────────────────────────────────────
        tk.Label(self, text="f(x) = e^(2x) - x - 2 = 0",
                 font=("Courier New", 12, "bold")).pack(pady=(10, 2))
        tk.Label(self, text="f'(x) = 2*e^(2x) - 1     f''(x) = 4*e^(2x)",
                 font=F).pack(pady=(0, 6))
        tk.Frame(self, height=1, bg="gray").pack(fill="x", padx=8)

        # ── Отделение корней ──────────────────────────────────────────────────
        frm1 = tk.LabelFrame(self, text=" Отделение корней ", font=FB)
        frm1.pack(fill="x", **pad)

        row = tk.Frame(frm1); row.pack(fill="x", padx=6, pady=4)
        tk.Button(row, text="Выполнить", font=F,
                  command=self._separate).pack(side="left")
        self.lbl_roots = tk.Label(row, text="", font=F, justify="left")
        self.lbl_roots.pack(side="left", padx=10)

        # ── Числовое решение ──────────────────────────────────────────────────
        frm2 = tk.LabelFrame(self, text=" Численное решение ", font=FB)
        frm2.pack(fill="x", **pad)

        # Отрезок и точность
        r0 = tk.Frame(frm2); r0.pack(fill="x", padx=6, pady=(6,2))
        tk.Label(r0, text="Отрезок:  a =", font=F).pack(side="left")
        self.va = tk.StringVar(value="-2")
        tk.Entry(r0, textvariable=self.va, width=7, font=F).pack(side="left", padx=2)
        tk.Label(r0, text="b =", font=F).pack(side="left", padx=(8,0))
        self.vb = tk.StringVar(value="-1")
        tk.Entry(r0, textvariable=self.vb, width=7, font=F).pack(side="left", padx=2)
        tk.Label(r0, text="  ε =", font=F).pack(side="left", padx=(8,0))
        self.ve = tk.StringVar(value="0.001")
        tk.Entry(r0, textvariable=self.ve, width=8, font=F).pack(side="left", padx=2)

        # Методы: (название, функция, индекс, показывать кнопку графика)
        methods = [
            ("Метод бисекций",        bisection,    0, True),
            ("Метод хорд",            chord,        1, False),
            ("Метод касательных",     newton,       2, False),
            ("Комбинированный метод", combined,     3, False),
            ("Метод итераций",        fixed_point,  4, False),
        ]
        self.res_vars = []
        for name, fn, idx, has_plot in methods:
            r = tk.Frame(frm2); r.pack(fill="x", padx=6, pady=2)
            tk.Button(r, text=name, font=F, width=24,
                      command=lambda fn=fn, i=idx: self._run(fn, i)
                      ).pack(side="left")
            if has_plot:
                tk.Button(r, text="График", font=F,
                          command=self._plot_bisection).pack(side="left", padx=4)
            rv = tk.StringVar(value="")
            tk.Label(r, textvariable=rv, font=FB, anchor="w",
                     width=35).pack(side="left", padx=6)
            self.res_vars.append(rv)

        # Кнопка — все методы
        tk.Frame(self, height=1, bg="gray").pack(fill="x", padx=8, pady=(6,0))
        btn_row = tk.Frame(self); btn_row.pack(pady=6)
        tk.Button(btn_row, text="Решить всеми методами", font=FB,
                  command=self._run_all).pack()

        # Статус
        self.lbl_status = tk.Label(self, text="", font=("Courier New", 9),
                                   fg="gray", anchor="w")
        self.lbl_status.pack(fill="x", padx=8, pady=(0,4))

    # ── Вспомогательные ───────────────────────────────────────────────────────
    def _get_ab(self):
        try:
            a   = float(self.va.get().replace(",", "."))
            b   = float(self.vb.get().replace(",", "."))
            eps = float(self.ve.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Ошибка", "Введите числа в поля a, b, ε")
            return None, None, None
        if a >= b:
            messagebox.showerror("Ошибка", "Нужно: a < b")
            return None, None, None
        return a, b, eps

    def _run(self, fn, idx):
        a, b, eps = self._get_ab()
        if a is None: return
        try:
            x, n = fn(a, b, eps)
            self.res_vars[idx].set(f"x = {x:.6f}   итераций: {n}")
            self.lbl_status.config(text=f"f({x:.6f}) = {f(x):.2e}")
        except Exception as e:
            self.res_vars[idx].set(f"Ошибка: {e}")

    def _run_all(self):
        a, b, eps = self._get_ab()
        if a is None: return
        fns = [bisection, chord, newton, combined, fixed_point]
        for i, fn in enumerate(fns):
            try:
                x, n = fn(a, b, eps)
                self.res_vars[i].set(f"x = {x:.6f}   итераций: {n}")
            except Exception as e:
                self.res_vars[i].set(f"Ошибка: {e}")
        self.lbl_status.config(
            text=f"a={a}  b={b}  ε={eps}  |  все методы выполнены")

    def _separate(self):
        ivs = separate_roots(-5, 5)
        if ivs:
            txt = "Корни найдены на отрезках:  " + \
                  "   ".join(f"[{a}; {b}]" for a, b in ivs)
        else:
            txt = "Корни не найдены на [-5; 5]"
        self.lbl_roots.config(text=txt)

    # ── График бисекции ───────────────────────────────────────────────────────
    def _plot_bisection(self):
        if not HAS_MPL:
            messagebox.showerror("Ошибка",
                "Установите matplotlib:\n"
                "C:/Users/User/AppData/Local/Programs/Python/Python313/"
                "python.exe -m pip install matplotlib")
            return
        a, b, eps = self._get_ab()
        if a is None: return
        try:
            history = bisection_trace(a, b, eps)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e)); return

        win = tk.Toplevel(self)
        win.title("Метод бисекций — график")
        win.geometry("950x560")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(f"Метод бисекций   [a={a}, b={b}]   ε={eps}",
                     fontsize=11)

        # --- левый: кривая и итерации ---
        x0 = history[0][0] - 0.3
        x1 = history[0][1] + 0.3
        xs = [x0 + (x1-x0)*i/400 for i in range(401)]
        ys = []
        for xv in xs:
            try: ys.append(f(xv))
            except: ys.append(float("nan"))

        # обрезаем y для читаемости
        finite = [v for v in ys if not math.isnan(v)]
        ylim = (max(-8, min(finite)), min(8, max(finite)))

        ax1.plot(xs, ys, "b-", linewidth=1.5, label="f(x) = e^(2x)-x-2")
        ax1.axhline(0, color="black", linewidth=0.8)
        ax1.axvline(0, color="black", linewidth=0.5, linestyle=":")
        ax1.set_ylim(ylim)
        ax1.set_xlabel("x")
        ax1.set_ylabel("f(x)")
        ax1.set_title("Сужение отрезка по итерациям")
        ax1.grid(True, linestyle=":", alpha=0.5)

        cmap = plt.cm.RdYlGn
        n = len(history)
        bracket_widths = []

        for i, (ai, bi, mid) in enumerate(history):
            c = cmap(i / max(n-1, 1))
            # полоска текущего отрезка
            ax1.axvspan(ai, bi, alpha=0.12, color=c)
            # точка середины
            try: fmid = f(mid)
            except: fmid = float("nan")
            if not math.isnan(fmid) and ylim[0] <= fmid <= ylim[1]:
                sz = 10 if i == n-1 else 5
                mk = "*" if i == n-1 else "o"
                ax1.plot(mid, fmid, mk, color=c, markersize=sz, zorder=5)
                ax1.plot([mid, mid], [0, fmid], color=c,
                         linewidth=0.5, linestyle="--", alpha=0.6)
            bracket_widths.append(bi - ai)

        root = history[-1][2]
        ax1.annotate(f"x* ≈ {root:.5f}",
                     xy=(root, 0), xytext=(root+0.05, ylim[1]*0.3),
                     arrowprops=dict(arrowstyle="->", color="red"),
                     fontsize=9, color="red")
        ax1.legend(fontsize=9)

        # цветовая полоска
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(1, n))
        sm.set_array([])
        cb = fig.colorbar(sm, ax=ax1, fraction=0.03, pad=0.02)
        cb.set_label("итерация", fontsize=8)

        # --- правый: сходимость ---
        iters = list(range(1, n+1))
        ax2.semilogy(iters, bracket_widths, "b-o", markersize=4,
                     linewidth=1.4, label="|b - a|")
        ax2.axhline(eps, color="red", linestyle="--",
                    linewidth=1.2, label=f"ε = {eps}")
        ax2.set_xlabel("Итерация")
        ax2.set_ylabel("|b - a|  (лог. шкала)")
        ax2.set_title("Скорость сходимости")
        ax2.legend(fontsize=9)
        ax2.grid(True, linestyle=":", alpha=0.5)

        # таблица значений под графиком
        tbl_data = []
        for i, (ai, bi, mid) in enumerate(history):
            try: fmid = f(mid)
            except: fmid = float("nan")
            tbl_data.append([i+1,
                              f"{ai:.5f}", f"{bi:.5f}", f"{mid:.5f}",
                              f"{fmid:.5f}", f"{bi-ai:.5f}"])

        fig.tight_layout(rect=[0, 0, 1, 0.95])

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        tb = NavigationToolbar2Tk(canvas, win)
        tb.update()

        # строка с итогом
        info = (f"Итераций: {n}   |   "
                f"x* = {root:.7f}   |   "
                f"f(x*) = {f(root):.3e}   |   "
                f"|b-a| финал = {history[-1][1]-history[-1][0]:.6f}")
        tk.Label(win, text=info, font=("Courier New", 9),
                 anchor="w").pack(fill="x", padx=6, pady=2)


if __name__ == "__main__":
    App().mainloop()