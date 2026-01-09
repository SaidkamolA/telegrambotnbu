from collections import Counter, defaultdict
from typing import Dict, Tuple, Any, List

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile

from config import ADMIN_IDS
from db.repo import load_all_responses
from survey.questions import SURVEY, SECTION_TITLES
from utils.long_text import send_long_text
from utils.excel import build_excel_stats

router = Router()
TOTAL_Q = len(SURVEY)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def compute_stats(responses: List[Tuple[str, Dict[str, Any]]]):
    totals = Counter()
    stats: Dict[str, Dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))

    for lang, answers in responses:
        totals["all"] += 1
        totals[lang] += 1

        for q in SURVEY:
            if q.key not in answers:
                continue

            val = answers[q.key]

            # ✅ совместимость со старыми ответами, где сохранялся list
            if isinstance(val, list):
                for opt_idx in val:
                    if isinstance(opt_idx, int):
                        stats["all"][q.key][opt_idx] += 1
                        stats[lang][q.key][opt_idx] += 1
            else:
                if isinstance(val, int):
                    stats["all"][q.key][val] += 1
                    stats[lang][q.key][val] += 1

    return totals, stats


def _pick_lang(text: str | None) -> str:
    args = (text or "").split()
    if len(args) > 1 and args[1].lower() in ("ru", "uz"):
        return args[1].lower()
    return "uz"


def _section_title(q_num: int, lang: str) -> str | None:
    last = None
    for start_q, titles in SECTION_TITLES.items():
        if q_num >= start_q:
            last = titles.get(lang)
    return last


def _safe_opt(opts: List[str], idx: int) -> str:
    if 0 <= idx < len(opts):
        return opts[idx]
    return f"option[{idx}]"


# ---------- SHORT (TOP) ----------

def format_stats_short(totals, stats, lang: str) -> str:
    total = int(totals.get("all", 0))
    lines = [
        "🏦 *STATISTIKA (TOP)*",
        f"Jami respondentlar: *{total}*",
        "──────────────",
    ]

    for i, q in enumerate(SURVEY):
        counter = stats["all"].get(q.key, Counter())
        q_total = sum(counter.values())

        q_text = q.text_ru if lang == "ru" else q.text_uz
        opts = q.options_ru if lang == "ru" else q.options_uz

        lines.append(f"*{i+1}.* {q_text}")

        if q_total == 0:
            lines.append("➡️ Javob yo‘q")
            lines.append("")
            continue

        top_idx, top_cnt = counter.most_common(1)[0]
        share = (top_cnt / q_total) * 100
        lines.append(f"➡️ *{_safe_opt(opts, top_idx)}* — {top_cnt} ({share:.2f}%)")
        lines.append("")

    return "\n".join(lines)


# ---------- FULL (BLOCKS) ----------

def format_stats_full(totals, stats, lang: str) -> str:
    total = int(totals.get("all", 0))
    lines = [
        "🏦 *STATISTIKA (FULL)*",
        f"Jami respondentlar: *{total}*",
        "",
    ]

    current_section = None

    for i, q in enumerate(SURVEY):
        q_num = i + 1
        sec = _section_title(q_num, lang)

        if sec != current_section and sec:
            current_section = sec
            lines.append("━━━━━━━━━━━━━━━━━━━━")
            lines.append(f"🧩 *{sec}*")
            lines.append("━━━━━━━━━━━━━━━━━━━━")
            lines.append("")

        q_text = q.text_ru if lang == "ru" else q.text_uz
        opts = q.options_ru if lang == "ru" else q.options_uz

        counter = stats["all"].get(q.key, Counter())
        q_total = sum(counter.values())

        lines.append(f"*{q_num}.* {q_text}")

        if q_total == 0:
            lines.append("➡️ Javob yo‘q")
            lines.append("")
            continue

        top_idx, top_cnt = counter.most_common(1)[0]
        top_share = (top_cnt / q_total) * 100
        lines.append(f"➡️ TOP: *{_safe_opt(opts, top_idx)}* — {top_cnt} ({top_share:.2f}%)")
        lines.append("📌 Taqsimot:")

        for idx in range(len(opts)):
            c = int(counter.get(idx, 0))
            p = (c / q_total) * 100
            lines.append(f"  • {opts[idx]} — {c} ({p:.2f}%)")

        lines.append("")

    return "\n".join(lines)


# ---------- COMMANDS ----------

@router.message(Command("stats"))
async def stats_alias(message: Message):
    await stats_short(message)


@router.message(Command("stats_short"))
async def stats_short(message: Message):
    if not is_admin(message.from_user.id):
        return

    lang = _pick_lang(message.text)
    responses = await load_all_responses()
    totals, stats = compute_stats(responses)

    text = format_stats_short(totals, stats, lang)
    await send_long_text(message, text)


@router.message(Command("stats_full"))
async def stats_full(message: Message):
    if not is_admin(message.from_user.id):
        return

    lang = _pick_lang(message.text)
    responses = await load_all_responses()
    totals, stats = compute_stats(responses)

    text = format_stats_full(totals, stats, lang)
    await send_long_text(message, text)


@router.message(Command("export_stats"))
async def export_stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    responses = await load_all_responses()
    totals, stats = compute_stats(responses)

    path = build_excel_stats(totals, stats)
    await message.answer_document(
        FSInputFile(path, filename="survey_stats.xlsx"),
        caption="📎 Survey Statistics (1–30, anonymous)",
    )
