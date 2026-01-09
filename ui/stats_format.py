from collections import Counter
from typing import Dict

from survey.questions import SURVEY


PROJECT_TITLE_UZ = "Kichik va o’rta biznesni moliyalashtirishni takomillashtirish"
PROJECT_TITLE_RU = "Совершенствование финансирования малого и среднего бизнеса"


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


def _sections(lang: str):
    return SECTION_RU if lang == "ru" else SECTION_UZ


def _section_title(lang: str, q_index0: int) -> str:
    for roman, a, b, title in _sections(lang):
        if a <= q_index0 <= b:
            return f"{roman}. {title}"
    return ""


def _q_text(q, lang: str) -> str:
    return q.text_ru if lang == "ru" else q.text_uz


def _opt_text(q, opt_idx: int, lang: str) -> str:
    opts = q.options_ru if lang == "ru" else q.options_uz
    if 0 <= opt_idx < len(opts):
        return opts[opt_idx]
    return f"option[{opt_idx}]"


def format_stats_short(
    totals: Counter,
    stats: Dict[str, Dict[str, Counter]],
    lang: str = "uz"
) -> str:
    total_all = int(totals.get("all", 0))
    total_ru = int(totals.get("ru", 0))
    total_uz = int(totals.get("uz", 0))
    denom = max(total_all, 1)

    title = (
        f"📊 {PROJECT_TITLE_UZ}"
        if lang == "uz"
        else f"📊 {PROJECT_TITLE_RU}"
    )

    lines = [
        title,
        f"{'Jami' if lang == 'uz' else 'Всего'}: {total_all} (RU: {total_ru}, UZ: {total_uz})",
        "━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    for i0, q in enumerate(SURVEY):
        counter = stats.get("all", {}).get(q.key, Counter())
        qn = i0 + 1

        if not counter:
            lines.append(
                f"{qn}. {_q_text(q, lang)} — "
                + ("javob yo‘q" if lang == "uz" else "нет ответов")
            )
            continue

        top_idx, top_cnt = counter.most_common(1)[0]
        share = (top_cnt / denom) * 100
        opt = _opt_text(q, top_idx, lang)

        lines.append(f"{qn}. {opt} — {top_cnt} ({share:.2f}%)")

    return "\n".join(lines)


def format_stats_full(
    totals: Counter,
    stats: Dict[str, Dict[str, Counter]],
    lang: str = "uz"
) -> str:
    total_all = int(totals.get("all", 0))
    total_ru = int(totals.get("ru", 0))
    total_uz = int(totals.get("uz", 0))
    denom = max(total_all, 1)

    title = (
        f"📊 {PROJECT_TITLE_UZ}"
        if lang == "uz"
        else f"📊 {PROJECT_TITLE_RU}"
    )

    lines = [
        title,
        f"{'Jami respondentlar' if lang == 'uz' else 'Всего респондентов'}: {total_all}",
        f"RU: {total_ru}   |   UZ: {total_uz}",
        "━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    current_section = None

    for idx0, q in enumerate(SURVEY):
        sec = _section_title(lang, idx0)
        if sec != current_section:
            current_section = sec
            lines.append(f"*{sec}*")
            lines.append("")

        counter = stats.get("all", {}).get(q.key, Counter())
        q_number = idx0 + 1

        if not counter:
            lines.append(f"{q_number}️⃣ {_q_text(q, lang)}")
            lines.append(
                "▪️ " + ("Javob yo‘q" if lang == "uz" else "Нет ответов")
            )
            lines.append("")
            continue

        top_idx, top_cnt = counter.most_common(1)[0]
        share = (top_cnt / denom) * 100
        opt = _opt_text(q, top_idx, lang)

        lines.append(f"{q_number}️⃣ {_q_text(q, lang)}")
        lines.append(f"▪️ *{opt}*")
        lines.append(
            f"▪️ {top_cnt} "
            + ("respondent" if lang == "uz" else "чел.")
            + f" ({share:.2f}%)"
        )
        lines.append("")

    lines.append(
        "📌 "
        + (
            "Izoh: foizlar jami respondentlar bo‘yicha."
            if lang == "uz"
            else "Примечание: проценты от общего числа респондентов."
        )
    )

    lines.append(
        "📌 "
        + (PROJECT_TITLE_UZ if lang == "uz" else PROJECT_TITLE_RU)
    )

    return "\n".join(lines)
