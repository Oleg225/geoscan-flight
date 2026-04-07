import asyncio
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    FSInputFile,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# =========================
# НАСТРОЙКИ
# =========================

BOT_TOKEN = ""  # <-- вставь токен от BotFather
ADMIN_IDS = {1103370984}  # <-- Telegram ID админа

DB_NAME = "p2p_bot.db"
MIN_USDT = 350.0  # сделки от 350$

# Папка для хранения QR-кодов
QR_CODES_DIR = "qr_codes"
os.makedirs(QR_CODES_DIR, exist_ok=True)

CURRENCIES = {
    "KZT": "KZT",
    "TJS": "TJS",
    "RUB": "RUB",
    "BYN": "BYN",
}

BANKS_BY_CURRENCY: Dict[str, List[str]] = {
    "KZT": ["Kaspi Bank", "Halyk Bank", "Freedom Bank Kazakhstan"],
    "TJS": ["DCbank", "Alif Bank"],
    "RUB": ["Sber", "T-Bank", "Alfa", "Ozon"],
    "BYN": ["MTBank", "Paritet Bank", "Prior Bank"],
}

NETWORKS = {
    "TRC20": "Tron (TRC20)",
    "ERC20": "Ethereum (ERC20)",
    "BEP20": "BNB Chain (BEP20)",
}

START_TEXT = (
    "Наш бот предлагает следующие возможности:\n\n"
    "Калькулятор обмена USDT на валюту с мгновенным расчётом суммы\n"
    "Актуальные курсы в боте по выбранным валютам (RUB/KZT/TJS/BYN)\n"
    "Поддержка популярных сетей: Tron (TRC20), Ethereum (ERC20), BNB Chain (BEP20)\n"
    "Прозрачные условия сделки и отсутствие скрытых комиссий\n"
    "Поддержка 24/7 для комфортного обмена\n\n"
    "Выберите действие:"
)

# =========================
# FSM СОСТОЯНИЯ
# =========================

class BuyStates(StatesGroup):
    currency = State()
    bank = State()
    network = State()
    amount_fiat = State()
    user_wallet = State()
    confirm = State()

class SellStates(StatesGroup):
    currency = State()
    network = State()
    amount_usdt = State()
    bank = State()
    user_bank_requisites = State()
    payment_proof = State()  # Новое состояние для фото подтверждения
    confirm = State()

class AdminStates(StatesGroup):
    set_rate_currency = State()
    set_rate_value = State()
    set_wallet_currency = State()
    set_wallet_value = State()
    set_wallet_qr = State()  # Новое состояние для загрузки QR-кода
    set_payout_currency = State()
    set_payout_value = State()


# =========================
# БАЗА + МИГРАЦИЯ
# =========================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def migrate_rates_table(cur: sqlite3.Cursor):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rates'")
    if not cur.fetchone():
        return

    cur.execute("PRAGMA table_info(rates)")
    cols = [row[1] for row in cur.fetchall()]
    if "kind" in cols:
        return

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS rates_new (
            kind TEXT NOT NULL,
            currency TEXT NOT NULL,
            rate REAL NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (kind, currency)
        )
        """
    )

    cur.execute("SELECT currency, rate, updated_at FROM rates")
    old_rows = cur.fetchall()
    for r in old_rows:
        currency, rate, updated_at = r
        cur.execute(
            "INSERT OR REPLACE INTO rates_new(kind, currency, rate, updated_at) VALUES(?,?,?,?)",
            ("BUY", currency, rate, updated_at),
        )
        cur.execute(
            "INSERT OR REPLACE INTO rates_new(kind, currency, rate, updated_at) VALUES(?,?,?,?)",
            ("SELL", currency, rate, updated_at),
        )

    cur.execute("DROP TABLE rates")
    cur.execute("ALTER TABLE rates_new RENAME TO rates")

def init_db():
    conn = get_db()
    cur = conn.cursor()

    migrate_rates_table(cur)

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            created_at TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS rates (
            kind TEXT NOT NULL,
            currency TEXT NOT NULL,
            rate REAL NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (kind, currency)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS wallets (
            currency TEXT PRIMARY KEY,
            address TEXT NOT NULL,
            qr_code_path TEXT,
            updated_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS payout_details (
            currency TEXT PRIMARY KEY,
            details TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT,
            full_name TEXT,
            currency TEXT NOT NULL,
            bank TEXT NOT NULL,
            network TEXT NOT NULL,
            amount_fiat REAL,
            amount_usdt REAL,
            rate REAL NOT NULL,
            rate_kind TEXT NOT NULL,
            user_wallet TEXT,
            user_bank_requisites TEXT,
            payment_proof_file_id TEXT,
            status TEXT NOT NULL DEFAULT 'NEW',
            created_at TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()

def upsert_user(user_id: int, username: Optional[str], full_name: Optional[str]):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (user_id, username, full_name, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            full_name=excluded.full_name
        """,
        (user_id, username, full_name, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()

def set_rate(kind: str, currency: str, rate: float):
    kind = kind.upper()
    if kind not in ("BUY", "SELL"):
        raise ValueError("kind must be BUY or SELL")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO rates(kind, currency, rate, updated_at)
        VALUES(?, ?, ?, ?)
        ON CONFLICT(kind, currency) DO UPDATE SET
            rate=excluded.rate,
            updated_at=excluded.updated_at
        """,
        (kind, currency, rate, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()

def get_rate(kind: str, currency: str) -> Optional[Tuple[float, str]]:
    kind = kind.upper()
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT rate, updated_at FROM rates WHERE kind = ? AND currency = ?",
        (kind, currency),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return float(row["rate"]), row["updated_at"]

def set_wallet(currency: str, address: str, qr_code_path: Optional[str] = None):
    conn = get_db()
    cur = conn.cursor()
    
    if qr_code_path:
        cur.execute(
            """
            INSERT INTO wallets(currency, address, qr_code_path, updated_at)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(currency) DO UPDATE SET
                address=excluded.address,
                qr_code_path=excluded.qr_code_path,
                updated_at=excluded.updated_at
            """,
            (currency, address, qr_code_path, datetime.now().isoformat(timespec="seconds")),
        )
    else:
        cur.execute(
            """
            INSERT INTO wallets(currency, address, updated_at)
            VALUES(?, ?, ?)
            ON CONFLICT(currency) DO UPDATE SET
                address=excluded.address,
                updated_at=excluded.updated_at
            """,
            (currency, address, datetime.now().isoformat(timespec="seconds")),
        )
    conn.commit()
    conn.close()

def get_wallet(currency: str) -> Optional[Tuple[str, Optional[str], str]]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT address, qr_code_path, updated_at FROM wallets WHERE currency = ?", (currency,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return str(row["address"]), row["qr_code_path"], row["updated_at"]

def set_payout_details(currency: str, details: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO payout_details(currency, details, updated_at)
        VALUES(?, ?, ?)
        ON CONFLICT(currency) DO UPDATE SET
            details=excluded.details,
            updated_at=excluded.updated_at
        """,
        (currency, details, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()

def get_payout_details(currency: str) -> Optional[Tuple[str, str]]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT details, updated_at FROM payout_details WHERE currency = ?", (currency,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return str(row["details"]), row["updated_at"]

def save_order(
    kind: str,
    user_id: int,
    username: Optional[str],
    full_name: Optional[str],
    currency: str,
    bank: str,
    network: str,
    rate_kind: str,
    rate: float,
    amount_fiat: Optional[float],
    amount_usdt: Optional[float],
    user_wallet: Optional[str],
    user_bank_requisites: Optional[str],
    payment_proof_file_id: Optional[str] = None,
) -> int:
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO orders(
            kind, user_id, username, full_name,
            currency, bank, network,
            amount_fiat, amount_usdt, rate, rate_kind,
            user_wallet, user_bank_requisites, payment_proof_file_id,
            status, created_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            kind, user_id, username, full_name,
            currency, bank, network,
            amount_fiat, amount_usdt, rate, rate_kind,
            user_wallet, user_bank_requisites, payment_proof_file_id,
            "NEW", datetime.now().isoformat(timespec="seconds")
        ),
    )
    oid = cur.lastrowid
    conn.commit()
    conn.close()
    return int(oid)

def update_order_payment_proof(order_id: int, file_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE orders SET payment_proof_file_id = ? WHERE id = ?",
        (file_id, order_id),
    )
    conn.commit()
    conn.close()

def fetch_latest_orders(limit: int = 20) -> List[sqlite3.Row]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def format_order(r: sqlite3.Row) -> str:
    user_line = f"Пользователь: {r['full_name'] or ''} (@{r['username']}) [id {r['user_id']}]\n"
    head = f"Заявка #{r['id']} | {r['kind']} | {r['status']}\n"
    core = (
        f"Валюта: {r['currency']} | Банк: {r['bank']}\n"
        f"Сеть: {NETWORKS.get(r['network'], r['network'])}\n"
        f"Курс {r['rate_kind']}: {r['rate']} {r['currency']} за 1 USDT\n"
    )
    if r["kind"] == "BUY":
        core += f"Сумма: {r['amount_fiat']} {r['currency']} -> {r['amount_usdt']} USDT\n"
        core += f"Кошелек клиента: {r['user_wallet'] or '—'}\n"
    else:
        core += f"Продажа: {r['amount_usdt']} USDT -> {r['amount_fiat']} {r['currency']}\n"
        core += f"Реквизиты клиента: {r['user_bank_requisites'] or '—'}\n"
        if r['payment_proof_file_id']:
            core += "Фото подтверждения: есть\n"
    core += f"Время: {r['created_at']}\n"
    return head + user_line + core


# =========================
# КЛАВИАТУРЫ
# =========================

def main_menu_kb(is_admin: bool) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="Купить USDT", callback_data="menu_buy"),
            InlineKeyboardButton(text="Продать USDT", callback_data="menu_sell"),
        ],
        [InlineKeyboardButton(text="Узнать курс", callback_data="menu_rates")],
    ]
    if is_admin:
        rows.append([InlineKeyboardButton(text="Админ панель", callback_data="menu_admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def currencies_kb(prefix: str) -> InlineKeyboardMarkup:
    rows = []
    for code, title in CURRENCIES.items():
        rows.append([InlineKeyboardButton(text=title, callback_data=f"{prefix}{code}")])
    rows.append([InlineKeyboardButton(text="Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def banks_kb(currency: str, prefix: str) -> InlineKeyboardMarkup:
    rows = []
    for b in BANKS_BY_CURRENCY.get(currency, []):
        rows.append([InlineKeyboardButton(text=b, callback_data=f"{prefix}{b}")])
    rows.append([InlineKeyboardButton(text="Назад", callback_data="back_currency")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def networks_kb(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=NETWORKS["TRC20"], callback_data=f"{prefix}TRC20")],
            [InlineKeyboardButton(text=NETWORKS["ERC20"], callback_data=f"{prefix}ERC20")],
            [InlineKeyboardButton(text=NETWORKS["BEP20"], callback_data=f"{prefix}BEP20")],
            [InlineKeyboardButton(text="Назад", callback_data="back_currency")],
        ]
    )

def confirm_kb(prefix_yes: str, prefix_no: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Подтвердить", callback_data=prefix_yes),
                InlineKeyboardButton(text="Отмена", callback_data=prefix_no),
            ]
        ]
    )

def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Курс BUY", callback_data="admin_set_rate_buy"),
                InlineKeyboardButton(text="Курс SELL", callback_data="admin_set_rate_sell"),
            ],
            [
                InlineKeyboardButton(text="Адрес USDT", callback_data="admin_set_wallet"),
                InlineKeyboardButton(text="QR код USDT", callback_data="admin_set_wallet_qr"),
            ],
            [InlineKeyboardButton(text="Реквизиты FIAT", callback_data="admin_set_payout")],
            [InlineKeyboardButton(text="Заявки", callback_data="admin_orders")],
            [InlineKeyboardButton(text="Назад", callback_data="back_main")],
        ]
    )

def admin_currency_kb(prefix: str) -> InlineKeyboardMarkup:
    return currencies_kb(prefix=prefix)

# =========================
# БОТ
# =========================

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# =========================
# ХЕЛПЕРЫ
# =========================

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def try_parse_amount(text: str) -> Optional[float]:
    if not text:
        return None
    t = text.strip().replace(" ", "").replace(",", ".")
    allowed = set("0123456789.")
    if any(ch not in allowed for ch in t):
        return None
    if t.count(".") > 1:
        return None
    try:
        v = float(t)
        if v <= 0:
            return None
        return v
    except Exception:
        return None

def rate_required_text(currency: str, kind: str) -> str:
    return (
        f"Курс {kind} для {currency} ещё не задан админом.\n"
        "Попробуйте позже или выберите другую валюту."
    )

async def broadcast_rate_change(kind: str, currency: str, rate: float):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    ids = [int(r["user_id"]) for r in cur.fetchall()]
    conn.close()

    label = "Покупка" if kind == "BUY" else "Продажа"
    text = f"Курс обновлён ({label}): {currency} = {rate} за 1 USDT"
    for uid in ids:
        try:
            await bot.send_message(uid, text)
        except Exception:
            pass


# =========================
# /start + назад
# =========================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    upsert_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(
        START_TEXT,
        reply_markup=main_menu_kb(is_admin=is_admin(message.from_user.id)),
    )

@dp.callback_query(F.data == "back_main")
async def back_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    upsert_user(call.from_user.id, call.from_user.username, call.from_user.full_name)
    await call.message.answer("Меню:", reply_markup=main_menu_kb(is_admin=is_admin(call.from_user.id)))
    await call.answer()

@dp.callback_query(F.data == "back_currency")
async def back_currency(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()
    if st and st.startswith(BuyStates.__name__):
        await state.set_state(BuyStates.currency)
        await call.message.answer("Покупка USDT\n\nВыберите валюту оплаты:", reply_markup=currencies_kb("buy_cur_"))
    elif st and st.startswith(SellStates.__name__):
        await state.set_state(SellStates.currency)
        await call.message.answer("Продажа USDT\n\nВыберите валюту получения:", reply_markup=currencies_kb("sell_cur_"))
    else:
        await state.clear()
        await call.message.answer("Меню:", reply_markup=main_menu_kb(is_admin=is_admin(call.from_user.id)))
    await call.answer()


# =========================
# УЗНАТЬ КУРС
# =========================

@dp.callback_query(F.data == "menu_rates")
async def menu_rates(call: CallbackQuery):
    lines = ["Актуальные курсы (за 1 USDT):", ""]
    for cur in CURRENCIES.keys():
        buy = get_rate("BUY", cur)
        sell = get_rate("SELL", cur)

        buy_txt = f"{buy[0]} {cur}" if buy else "—"
        sell_txt = f"{sell[0]} {cur}" if sell else "—"

        lines.append(f"{cur}:")
        lines.append(f"BUY: {buy_txt}")
        lines.append(f"SELL: {sell_txt}")
        lines.append("")

    lines.append(f"Минимальная сделка: {MIN_USDT} USDT")
    await call.message.answer("\n".join(lines))
    await call.answer()


# =========================
# BUY FLOW
# =========================

@dp.callback_query(F.data == "menu_buy")
async def buy_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    upsert_user(call.from_user.id, call.from_user.username, call.from_user.full_name)
    await state.set_state(BuyStates.currency)
    await call.message.answer("Покупка USDT\n\nШаг 1/5: выберите валюту оплаты:", reply_markup=currencies_kb("buy_cur_"))
    await call.answer()

@dp.callback_query(BuyStates.currency, F.data.startswith("buy_cur_"))
async def buy_choose_currency(call: CallbackQuery, state: FSMContext):
    cur = call.data.replace("buy_cur_", "")
    await state.update_data(currency=cur)
    await state.set_state(BuyStates.bank)
    await call.message.answer(f"Шаг 2/5: выберите банк ({cur}):", reply_markup=banks_kb(cur, "buy_bank_"))
    await call.answer()

@dp.callback_query(BuyStates.bank, F.data.startswith("buy_bank_"))
async def buy_choose_bank(call: CallbackQuery, state: FSMContext):
    bank = call.data.replace("buy_bank_", "")
    await state.update_data(bank=bank)
    await state.set_state(BuyStates.network)
    await call.message.answer("Шаг 3/5: выберите сеть получения USDT:", reply_markup=networks_kb("buy_net_"))
    await call.answer()

@dp.callback_query(BuyStates.network, F.data.startswith("buy_net_"))
async def buy_choose_network(call: CallbackQuery, state: FSMContext):
    net = call.data.replace("buy_net_", "")
    await state.update_data(network=net)

    data = await state.get_data()
    cur = data["currency"]

    rate_info = get_rate("BUY", cur)
    if not rate_info:
        await state.clear()
        await call.message.answer(rate_required_text(cur, "BUY"), reply_markup=main_menu_kb(is_admin=is_admin(call.from_user.id)))
        await call.answer()
        return

    rate, _ = rate_info
    min_fiat = rate * MIN_USDT

    payout = get_payout_details(cur)
    payout_text = payout[0] if payout else "Админ ещё не добавил реквизиты для оплаты."

    await state.update_data(rate=rate)
    await state.set_state(BuyStates.amount_fiat)

    await call.message.answer(
        "Шаг 4/5: введите сумму в вашей валюте.\n\n"
        f"Банк: {data['bank']}\n"
        f"Сеть: {NETWORKS.get(net, net)}\n"
        f"Курс BUY: {rate} {cur} за 1 USDT\n"
        f"Минимум: {MIN_USDT}$ ≈ {min_fiat:.2f} {cur}\n\n"
        f"Реквизиты для оплаты ({cur}):\n{payout_text}\n\n"
        "Введите сумму строго числом.\n"
        "Пример: 10000 или 10000.50"
    )
    await call.answer()

@dp.message(BuyStates.amount_fiat)
async def buy_amount_fiat(message: Message, state: FSMContext):
    upsert_user(message.from_user.id, message.from_user.username, message.from_user.full_name)

    amount = try_parse_amount(message.text)
    if amount is None:
        await message.answer(
            "Неверный формат суммы.\n"
            "Введите строго числом.\n"
            "Пример: 10000 или 10000.50"
        )
        return

    data = await state.get_data()
    cur = data["currency"]

    rate_info = get_rate("BUY", cur)
    if not rate_info:
        await state.clear()
        await message.answer(rate_required_text(cur, "BUY"), reply_markup=main_menu_kb(is_admin=is_admin(message.from_user.id)))
        return

    rate, _ = rate_info
    min_fiat = rate * MIN_USDT

    if amount < min_fiat:
        await message.answer(
            f"Сумма слишком маленькая.\n"
            f"Минимум: {min_fiat:.2f} {cur} (это {MIN_USDT}$)\n\n"
            "Введите сумму больше.\n"
            "Пример: 30000"
        )
        return

    usdt = amount / rate
    await state.update_data(amount_fiat=round(amount, 2), amount_usdt=round(usdt, 6), rate=rate)
    await state.set_state(BuyStates.user_wallet)

    await message.answer(
        "Шаг 5/5: отправьте адрес кошелька для получения USDT.\n\n"
        f"Вы получите примерно: {usdt:.6f} USDT\n"
        f"Сеть: {NETWORKS.get(data['network'], data['network'])}\n\n"
        "Пример:\n"
        "TRC20: TX... (начинается на T)\n"
        "ERC20: 0x... (начинается на 0x)\n"
        "BEP20: 0x... (обычно тоже 0x)\n\n"
        "Отправьте адрес одним сообщением."
    )

@dp.message(BuyStates.user_wallet)
async def buy_user_wallet(message: Message, state: FSMContext):
    wallet = (message.text or "").strip()
    if len(wallet) < 10:
        await message.answer(
            "Неверный формат кошелька.\n"
            "Отправьте адрес одним сообщением.\n"
            "Пример: TX... или 0x..."
        )
        return

    data = await state.get_data()

    await state.update_data(user_wallet=wallet)
    await state.set_state(BuyStates.confirm)

    await message.answer(
        "Подтверждение заявки (BUY)\n\n"
        f"Валюта: {data['currency']}\n"
        f"Банк: {data['bank']}\n"
        f"Сеть: {NETWORKS.get(data['network'], data['network'])}\n"
        f"Курс BUY: {data['rate']} {data['currency']}/USDT\n"
        f"Сумма: {data['amount_fiat']} {data['currency']}\n"
        f"Получите: ~{data['amount_usdt']} USDT\n"
        f"Ваш кошелёк: {wallet}\n\n"
        "Если всё верно — подтвердите.",
        reply_markup=confirm_kb("buy_yes", "buy_no"),
    )

@dp.callback_query(BuyStates.confirm, F.data == "buy_no")
async def buy_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Отменено.", reply_markup=main_menu_kb(is_admin=is_admin(call.from_user.id)))
    await call.answer()

@dp.callback_query(BuyStates.confirm, F.data == "buy_yes")
async def buy_confirm(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    oid = save_order(
        kind="BUY",
        user_id=call.from_user.id,
        username=call.from_user.username,
        full_name=call.from_user.full_name,
        currency=data["currency"],
        bank=data["bank"],
        network=data["network"],
        rate_kind="BUY",
        rate=float(data["rate"]),
        amount_fiat=float(data["amount_fiat"]),
        amount_usdt=float(data["amount_usdt"]),
        user_wallet=data["user_wallet"],
        user_bank_requisites=None,
    )

    await state.clear()
    await call.message.answer(
        f"Заявка создана: #{oid}\n"
        "Админ свяжется с вами для подтверждения и деталей перевода.",
        reply_markup=main_menu_kb(is_admin=is_admin(call.from_user.id)),
    )

    notify = (
        "Новая заявка BUY\n\n"
        f"#{oid}\n"
        f"Пользователь: {call.from_user.full_name} (@{call.from_user.username}) [id {call.from_user.id}]\n"
        f"Валюта: {data['currency']} | Банк: {data['bank']}\n"
        f"Сеть: {NETWORKS.get(data['network'], data['network'])}\n"
        f"Курс BUY: {data['rate']} {data['currency']}/USDT\n"
        f"Сумма: {data['amount_fiat']} {data['currency']} -> ~{data['amount_usdt']} USDT\n"
        f"Кошелёк клиента: {data['user_wallet']}\n"
        f"Время: {datetime.now().isoformat(timespec='seconds')}"
    )
    for aid in ADMIN_IDS:
        try:
            await bot.send_message(aid, notify)
        except Exception:
            pass

    await call.answer()


# =========================
# SELL FLOW
# =========================

@dp.callback_query(F.data == "menu_sell")
async def sell_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    upsert_user(call.from_user.id, call.from_user.username, call.from_user.full_name)
    await state.set_state(SellStates.currency)
    await call.message.answer(
        "Продажа USDT\n\n"
        "Шаг 1/7: выберите валюту, в которой хотите получить оплату:",
        reply_markup=currencies_kb("sell_cur_"),
    )
    await call.answer()

@dp.callback_query(SellStates.currency, F.data.startswith("sell_cur_"))
async def sell_choose_currency(call: CallbackQuery, state: FSMContext):
    cur = call.data.replace("sell_cur_", "")
    await state.update_data(currency=cur)
    await state.set_state(SellStates.network)
    await call.message.answer(
        "Шаг 2/7: выберите сеть, в которой вы переведёте USDT.\n\n"
        f"Валюта получения: {cur}",
        reply_markup=networks_kb("sell_net_"),
    )
    await call.answer()

@dp.callback_query(SellStates.network, F.data.startswith("sell_net_"))
async def sell_choose_network(call: CallbackQuery, state: FSMContext):
    net = call.data.replace("sell_net_", "")
    await state.update_data(network=net)

    data = await state.get_data()
    cur = data["currency"]

    rate_info = get_rate("SELL", cur)
    if not rate_info:
        await state.clear()
        await call.message.answer(
            rate_required_text(cur, "SELL"),
            reply_markup=main_menu_kb(is_admin=is_admin(call.from_user.id)),
        )
        await call.answer()
        return

    rate, _ = rate_info

    wallet_info = get_wallet(cur)
    if not wallet_info:
        await state.clear()
        await call.message.answer(
            f"Админ ещё не добавил кошелёк для валюты {cur}.",
            reply_markup=main_menu_kb(is_admin=is_admin(call.from_user.id)),
        )
        await call.answer()
        return

    address, qr_path, _ = wallet_info

    await state.update_data(rate=rate, wallet_address=address, qr_path=qr_path)
    await state.set_state(SellStates.amount_usdt)

    # Отправляем QR код если он есть
    if qr_path and os.path.exists(qr_path):
        photo = FSInputFile(qr_path)
        await call.message.answer_photo(
            photo=photo,
            caption=f"QR код кошелька для перевода USDT ({cur})"
        )

    await call.message.answer(
        "Шаг 3/7: переведите USDT на кошелёк ниже и укажите сумму.\n\n"
        f"Курс SELL: {rate} {cur} за 1 USDT\n"
        f"Минимум сделки: {MIN_USDT} USDT\n"
        f"Сеть: {NETWORKS.get(net, net)}\n\n"
        "Кошелёк для перевода USDT:\n"
        f"<code>{address}</code>\n\n"
        "Введите, сколько USDT вы переведёте (строго числом).\n"
        "Пример: 200 или 200.5"
    )
    await call.answer()

@dp.message(SellStates.amount_usdt)
async def sell_amount_usdt(message: Message, state: FSMContext):
    upsert_user(message.from_user.id, message.from_user.username, message.from_user.full_name)

    amount_usdt = try_parse_amount(message.text)
    if amount_usdt is None:
        await message.answer(
            "Неверный формат суммы.\n"
            "Введите строго числом.\n"
            "Пример: 200 или 200.5"
        )
        return

    if amount_usdt < MIN_USDT:
        await message.answer(
            f"Минимум сделки: {MIN_USDT} USDT.\n"
            f"Введите сумму не меньше {MIN_USDT}.\n"
            "Пример: 350"
        )
        return

    data = await state.get_data()
    cur = data["currency"]

    rate_info = get_rate("SELL", cur)
    if not rate_info:
        await state.clear()
        await message.answer(
            rate_required_text(cur, "SELL"),
            reply_markup=main_menu_kb(is_admin=is_admin(message.from_user.id)),
        )
        return

    rate, _ = rate_info
    amount_fiat = amount_usdt * rate

    await state.update_data(
        amount_usdt=round(amount_usdt, 6),
        amount_fiat=round(amount_fiat, 2),
        rate=rate,
    )

    await state.set_state(SellStates.bank)

    await message.answer(
        "Шаг 4/7: выберите банк, на который хотите получить выплату.\n\n"
        f"Вы получите примерно: {amount_fiat:.2f} {cur}\n"
        f"Курс SELL: {rate} {cur}/USDT\n\n"
        "Выберите банк:",
        reply_markup=banks_kb(cur, "sell_bank_"),
    )

@dp.callback_query(SellStates.bank, F.data.startswith("sell_bank_"))
async def sell_choose_bank(call: CallbackQuery, state: FSMContext):
    bank = call.data.replace("sell_bank_", "")
    await state.update_data(bank=bank)
    await state.set_state(SellStates.user_bank_requisites)

    data = await state.get_data()
    cur = data["currency"]

    await call.message.answer(
        "Шаг 5/7: отправьте реквизиты для получения денег.\n\n"
        f"Банк: {bank}\n"
        f"Валюта: {cur}\n\n"
        "Введите реквизиты одним сообщением.\n"
        "Пример (карта): 2200123456789012\n"
        "Пример (ФИО+карта): Иван Иванов, 2200123456789012\n"
        "Пример (IBAN): KZ000000000000000000",
    )
    await call.answer()

@dp.message(SellStates.user_bank_requisites)
async def sell_user_requisites(message: Message, state: FSMContext):
    req = (message.text or "").strip()
    if len(req) < 10:
        await message.answer(
            "Реквизиты слишком короткие.\n"
            "Отправьте подробнее.\n"
            "Пример: Иван Иванов, 2200123456789012"
        )
        return

    await state.update_data(user_bank_requisites=req)
    await state.set_state(SellStates.payment_proof)

    await message.answer(
        "Шаг 6/7: отправьте фото подтверждения перевода USDT.\n\n"
        "Сделайте скриншот или фото экрана с подтверждением транзакции.\n"
        "Это поможет админу быстрее обработать вашу заявку."
    )

@dp.message(SellStates.payment_proof, F.photo)
async def sell_payment_proof(message: Message, state: FSMContext):
    # Получаем file_id самого большого фото
    photo = message.photo[-1]
    file_id = photo.file_id
    
    await state.update_data(payment_proof_file_id=file_id)
    await state.set_state(SellStates.confirm)

    data = await state.get_data()
    wallet_info = get_wallet(data["currency"])
    address, qr_path, _ = wallet_info if wallet_info else (None, None, None)

    await message.answer(
        "Шаг 7/7: подтвердите заявку (SELL)\n\n"
        f"Валюта: {data['currency']}\n"
        f"Банк: {data['bank']}\n"
        f"Сеть: {NETWORKS.get(data['network'], data['network'])}\n"
        f"Курс SELL: {data['rate']} {data['currency']}/USDT\n"
        f"Вы переводите: {data['amount_usdt']} USDT\n"
        f"Вы получите: ~{data['amount_fiat']} {data['currency']}\n"
        f"Ваши реквизиты: {data['user_bank_requisites']}\n\n"
        "Фото подтверждения получено.\n\n"
        "Кошелёк админа для перевода USDT:\n"
        f"<code>{address}</code>\n\n"
        "Если всё верно — подтвердите.",
        reply_markup=confirm_kb("sell_yes", "sell_no"),
    )

@dp.message(SellStates.payment_proof)
async def sell_payment_proof_invalid(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте фото подтверждения перевода.")

@dp.callback_query(SellStates.confirm, F.data == "sell_no")
async def sell_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Отменено.", reply_markup=main_menu_kb(is_admin=is_admin(call.from_user.id)))
    await call.answer()

@dp.callback_query(SellStates.confirm, F.data == "sell_yes")
async def sell_confirm(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    oid = save_order(
        kind="SELL",
        user_id=call.from_user.id,
        username=call.from_user.username,
        full_name=call.from_user.full_name,
        currency=data["currency"],
        bank=data["bank"],
        network=data["network"],
        rate_kind="SELL",
        rate=float(data["rate"]),
        amount_fiat=float(data["amount_fiat"]),
        amount_usdt=float(data["amount_usdt"]),
        user_wallet=None,
        user_bank_requisites=data["user_bank_requisites"],
        payment_proof_file_id=data.get("payment_proof_file_id"),
    )

    await state.clear()
    await call.message.answer(
        f"Заявка создана: #{oid}\n"
        "Админ свяжется с вами для подтверждения и деталей оплаты.",
        reply_markup=main_menu_kb(is_admin=is_admin(call.from_user.id)),
    )

    wallet_info = get_wallet(data["currency"])
    address, qr_path, _ = wallet_info if wallet_info else (None, None, None)

    # Отправляем уведомление админу с фото подтверждения
    for aid in ADMIN_IDS:
        try:
            notify = (
                "Новая заявка SELL\n\n"
                f"#{oid}\n"
                f"Пользователь: {call.from_user.full_name} (@{call.from_user.username}) [id {call.from_user.id}]\n"
                f"Валюта: {data['currency']} | Банк: {data['bank']}\n"
                f"Сеть: {NETWORKS.get(data['network'], data['network'])}\n"
                f"Курс SELL: {data['rate']} {data['currency']}/USDT\n"
                f"USDT: {data['amount_usdt']} -> {data['amount_fiat']} {data['currency']}\n"
                f"Реквизиты клиента: {data['user_bank_requisites']}\n\n"
                "Кошелёк админа для депозита USDT:\n"
                f"{address}\n"
                f"Время: {datetime.now().isoformat(timespec='seconds')}"
            )
            
            # Отправляем текстовое уведомление
            await bot.send_message(aid, notify)
            
            # Отправляем фото подтверждения если оно есть
            if data.get("payment_proof_file_id"):
                await bot.send_photo(
                    aid,
                    data["payment_proof_file_id"],
                    caption=f"Фото подтверждения перевода для заявки #{oid}"
                )
        except Exception as e:
            print(f"Ошибка отправки уведомления админу: {e}")

    await call.answer()


# =========================
# АДМИН
# =========================

@dp.callback_query(F.data == "menu_admin")
async def admin_menu(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return
    await state.clear()
    await call.message.answer("Админ-панель:", reply_markup=admin_menu_kb())
    await call.answer()

@dp.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("Нет доступа")
        return
    await state.clear()
    await message.answer("Админ-панель:", reply_markup=admin_menu_kb())

@dp.callback_query(F.data.in_({"admin_set_rate_buy", "admin_set_rate_sell"}))
async def admin_set_rate(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return
    kind = "BUY" if call.data.endswith("_buy") else "SELL"
    await state.update_data(rate_kind=kind)
    await state.set_state(AdminStates.set_rate_currency)
    await call.message.answer(f"Выберите валюту для курса {kind}:", reply_markup=admin_currency_kb("admin_rate_cur_"))
    await call.answer()

@dp.callback_query(AdminStates.set_rate_currency, F.data.startswith("admin_rate_cur_"))
async def admin_rate_choose_currency(call: CallbackQuery, state: FSMContext):
    cur = call.data.replace("admin_rate_cur_", "")
    await state.update_data(currency=cur)
    await state.set_state(AdminStates.set_rate_value)
    data = await state.get_data()
    kind = data["rate_kind"]
    await call.message.answer(
        f"Введите курс {kind} для {cur}.\n"
        "Формат: сколько этой валюты за 1 USDT.\n"
        "Пример: 75"
    )
    await call.answer()

@dp.message(AdminStates.set_rate_value)
async def admin_rate_set_value(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    val = try_parse_amount(message.text)
    if val is None:
        await message.answer("Введите число. Пример: 75")
        return

    data = await state.get_data()
    cur = data["currency"]
    kind = data["rate_kind"]

    set_rate(kind, cur, float(val))
    await state.clear()

    await message.answer(f"Курс {kind} обновлён: {cur} = {val} за 1 USDT", reply_markup=admin_menu_kb())
    await broadcast_rate_change(kind, cur, float(val))

@dp.callback_query(F.data == "admin_set_wallet")
async def admin_set_wallet(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return
    await state.set_state(AdminStates.set_wallet_currency)
    await call.message.answer("Выберите валюту (адрес USDT для SELL):", reply_markup=admin_currency_kb("admin_wallet_cur_"))
    await call.answer()

@dp.callback_query(AdminStates.set_wallet_currency, F.data.startswith("admin_wallet_cur_"))
async def admin_wallet_choose_currency(call: CallbackQuery, state: FSMContext):
    cur = call.data.replace("admin_wallet_cur_", "")
    await state.update_data(currency=cur)
    await state.set_state(AdminStates.set_wallet_value)
    await call.message.answer(
        f"Отправьте адрес кошелька USDT для {cur}.\n"
        "Это адрес, куда пользователи будут переводить USDT при продаже."
    )
    await call.answer()

@dp.message(AdminStates.set_wallet_value)
async def admin_wallet_set_value(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    addr = (message.text or "").strip()
    if len(addr) < 10:
        await message.answer("Слишком коротко. Отправьте адрес ещё раз.")
        return

    data = await state.get_data()
    cur = data["currency"]

    set_wallet(cur, addr)
    await state.clear()
    await message.answer(f"Адрес USDT сохранён для {cur}:\n{addr}", reply_markup=admin_menu_kb())

@dp.callback_query(F.data == "admin_set_wallet_qr")
async def admin_set_wallet_qr(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return
    await state.set_state(AdminStates.set_wallet_currency)
    await call.message.answer(
        "Выберите валюту для загрузки QR кода кошелька:",
        reply_markup=admin_currency_kb("admin_wallet_qr_cur_")
    )
    await call.answer()

@dp.callback_query(AdminStates.set_wallet_currency, F.data.startswith("admin_wallet_qr_cur_"))
async def admin_wallet_qr_choose_currency(call: CallbackQuery, state: FSMContext):
    cur = call.data.replace("admin_wallet_qr_cur_", "")
    await state.update_data(currency=cur)
    await state.set_state(AdminStates.set_wallet_qr)
    await call.message.answer(
        f"Отправьте фото QR кода кошелька USDT для {cur}.\n"
        "Этот QR код будут видеть пользователи при создании заявки на продажу."
    )
    await call.answer()

@dp.message(AdminStates.set_wallet_qr, F.photo)
async def admin_wallet_qr_set(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    data = await state.get_data()
    cur = data["currency"]

    # Получаем информацию о текущем кошельке
    wallet_info = get_wallet(cur)
    if not wallet_info:
        await message.answer(
            f"Сначала добавьте адрес кошелька для {cur} через меню 'Адрес USDT'"
        )
        return

    address, _, _ = wallet_info

    # Сохраняем фото
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    
    # Создаем уникальное имя файла
    qr_filename = f"qr_{cur}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    qr_path = os.path.join(QR_CODES_DIR, qr_filename)
    
    # Скачиваем файл
    await bot.download_file(file.file_path, qr_path)

    # Обновляем запись в БД с путем к QR коду
    set_wallet(cur, address, qr_path)
    
    await state.clear()
    await message.answer(f"QR код для {cur} успешно сохранён.", reply_markup=admin_menu_kb())

@dp.message(AdminStates.set_wallet_qr)
async def admin_wallet_qr_invalid(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте фото QR кода.")

@dp.callback_query(F.data == "admin_set_payout")
async def admin_set_payout(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return
    await state.set_state(AdminStates.set_payout_currency)
    await call.message.answer("Выберите валюту для реквизитов FIAT (BUY):", reply_markup=admin_currency_kb("admin_payout_cur_"))
    await call.answer()

@dp.callback_query(AdminStates.set_payout_currency, F.data.startswith("admin_payout_cur_"))
async def admin_payout_choose_currency(call: CallbackQuery, state: FSMContext):
    cur = call.data.replace("admin_payout_cur_", "")
    await state.update_data(currency=cur)
    await state.set_state(AdminStates.set_payout_value)
    await call.message.answer(
        f"Отправьте реквизиты для {cur}.\n"
        "Можно одним сообщением. Пример:\n"
        "Банк: Сбер\n"
        "Карта: 0000000000000000\n"
        "Получатель: Иван И."
    )
    await call.answer()

@dp.message(AdminStates.set_payout_value)
async def admin_payout_set_value(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    details = (message.text or "").strip()
    if len(details) < 5:
        await message.answer("Слишком коротко. Отправьте реквизиты подробнее.")
        return

    data = await state.get_data()
    cur = data["currency"]

    set_payout_details(cur, details)
    await state.clear()
    await message.answer(f"Реквизиты для {cur} сохранены.", reply_markup=admin_menu_kb())

@dp.callback_query(F.data == "admin_orders")
async def admin_orders(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return
    rows = fetch_latest_orders(limit=20)
    if not rows:
        await call.message.answer("Заявок пока нет.")
        await call.answer()
        return
    
    await call.message.answer("Последние заявки (до 20):")
    for r in rows:
        order_text = format_order(r)
        await call.message.answer(order_text)
        
        # Если есть фото подтверждения, отправляем его
        if r["payment_proof_file_id"]:
            await call.message.answer_photo(
                r["payment_proof_file_id"],
                caption=f"Фото подтверждения для заявки #{r['id']}"
            )
    await call.answer()


# =========================
# MAIN
# =========================

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())