from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def kb_lang() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="UZ 🇺🇿", callback_data="lang:uz")
    kb.button(text="RU 🇷🇺", callback_data="lang:ru")
    kb.adjust(2)
    return kb.as_markup()


def kb_single(
    q_index: int,
    opts: list[str],
    selected_opt: int | None,
    total: int,
    all_answered: bool,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    # варианты ответа
    for i, opt in enumerate(opts):
        text = ("✅ " + opt) if (selected_opt is not None and i == selected_opt) else opt
        kb.button(text=text, callback_data=f"ans:{q_index}:{i}")

    # раскладка вариантов
    if len(opts) <= 3:
        kb.adjust(len(opts))
    else:
        kb.adjust(1)

    # навигация (inline) — НЕ СПАМИТ ЧАТ
    nav = InlineKeyboardBuilder()
    if q_index > 0:
        nav.button(text="⬅️ Назад", callback_data=f"nav:prev:{q_index}")
    if q_index < total - 1:
        nav.button(text="➡️ Вперёд", callback_data=f"nav:next:{q_index}")
    nav.adjust(2)

    # добавляем ряд навигации
    for row in nav.export():
        kb.row(*row)

    # кнопка завершения — только если все отвечены
    if all_answered:
        kb.row()
        kb.button(text="✅ Завершить", callback_data="nav:finish")

    return kb.as_markup()
