from typing import Dict, Any, List, Tuple

from survey.questions import SURVEY
from survey.text import intro


def get_text_and_opts(q, lang: str):
    if lang == "ru":
        return q.text_ru, q.options_ru
    return q.text_uz, q.options_uz


SECTION_RU = [
    ("I", 0, 4, "Характеристика респондента"),
    ("II", 5, 9, "Потребность в кредите и использование"),
    ("III", 10, 14, "Основные проблемы кредитования"),
    ("IV", 15, 19, "Институциональные и системные вопросы"),
    ("V", 20, 24, "Решения и предложения"),
    ("VI", 25, 29, "Итоговая оценка"),
]

SECTION_UZ = [
    ("I", 0, 4, "Respondentlarning tavsifi"),
    ("II", 5, 9, "Kreditga ehtiyoj va foydalanish"),
    ("III", 10, 14, "Kreditlashdagi asosiy muammolar"),
    ("IV", 15, 19, "Institutsional va tizimli muammolar"),
    ("V", 20, 24, "Yechimlar va takliflar"),
    ("VI", 25, 29, "Yakuniy baholash"),
]


def _section_for_index(lang: str, q_index: int) -> str:
    items = SECTION_RU if lang == "ru" else SECTION_UZ
    for roman, a, b, title in items:
        if a <= q_index <= b:
            return f"*{roman}. {title}*"
    return ""


def render_question(
    lang: str,
    q_index: int,
    answers: Dict[str, Any],
    multi_buf: Dict[str, Any],
    show_intro_header: bool = False
) -> Tuple[str, List[str], bool, List[int] | None, int | None]:
    q = SURVEY[q_index]
    q_text, opts = get_text_and_opts(q, lang)

    section = _section_for_index(lang, q_index)

    header = ""
    if show_intro_header:
        header = intro(lang) + "\n\n" + "—" * 18 + "\n\n"

    text = (
        f"{header}"
        f"{section}\n"
        f"🧾 *Savol / Вопрос:* {q_index+1}/{len(SURVEY)}\n\n"
        f"{q_text}"
    )

    if q.multi:
        selected = answers.get(q.key, multi_buf.get(q.key, []))
        hint = "🔸 Bir nechta tanlash mumkin. So‘ng ✅ Tayyor bosing." if lang == "uz" else "🔸 Можно выбрать несколько. Затем нажмите ✅ Готово."
        text += "\n\n" + hint

        if selected:
            selected_text = ", ".join([opts[i] for i in selected if i < len(opts)])
            text += "\n\n✅ " + ("Tanlangan" if lang == "uz" else "Выбрано") + f": *{selected_text}*"

        return text, opts, True, selected, None

    selected_opt = answers.get(q.key)
    if selected_opt is not None and selected_opt < len(opts):
        text += "\n\n✅ " + ("Tanlangan" if lang == "uz" else "Выбрано") + f": *{opts[selected_opt]}*"

    return text, opts, False, None, selected_opt
