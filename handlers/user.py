from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from db.repo import (
    set_lang_and_reset,
    get_progress,
    save_progress,
    finalize_response,
    has_submission,
)
from survey.questions import SURVEY, get_section_title, get_survey_header
from survey.text import get_text_and_opts, thanks
from ui.keyboards import kb_lang, kb_single

router = Router()


def already_done_text(lang: str) -> str:
    if lang == "ru":
        return (
            "✅ *Спасибо!* Вы уже проходили этот опрос.\n\n"
            "📌 Повторное прохождение недоступно.\n"

        )
    return (
        "✅ *Rahmat!* Siz bu so‘rovnomadan allaqachon o‘tib bo‘lgansiz.\n\n"
        "📌 Qayta topshirish mumkin emas.\n"

    )


@router.message(CommandStart())
async def start(message: Message):
    # если уже сдавал — не даём начать заново
    if await has_submission(message.from_user.id):
        # язык берём из progress если есть, иначе uz
        lang, _, _, _ = await get_progress(message.from_user.id)
        await message.answer(already_done_text(lang), reply_markup=None)
        return

    await message.answer("Til / Язык:", reply_markup=kb_lang())


@router.message(Command("restart"))
async def restart(message: Message):
    if await has_submission(message.from_user.id):
        lang, _, _, _ = await get_progress(message.from_user.id)
        await message.answer(already_done_text(lang), reply_markup=None)
        return

    await message.answer("Til / Язык:", reply_markup=kb_lang())


@router.callback_query(F.data.startswith("lang:"))
async def on_lang(call: CallbackQuery):
    user_id = call.from_user.id

    # если уже сдавал — блокируем выбор языка
    if await has_submission(user_id):
        lang, _, _, _ = await get_progress(user_id)
        await call.answer()
        try:
            await call.message.edit_text(already_done_text(lang))
        except Exception:
            await call.bot.send_message(call.message.chat.id, already_done_text(lang))
        return

    lang = call.data.split(":")[1]
    await set_lang_and_reset(user_id, lang)

    try:
        await call.message.delete()
    except Exception:
        pass

    await call.answer()

    await send_question(
        user_id=user_id,
        chat_id=call.message.chat.id,
        bot=call.bot,
        q_index=0,
        edit_msg_id=None,
    )


async def send_question(user_id: int, chat_id: int, bot, q_index: int | None, edit_msg_id: int | None):
    # если уже сдавал — не показываем вопросы
    if await has_submission(user_id):
        lang, _, _, _ = await get_progress(user_id)
        if edit_msg_id:
            try:
                await bot.edit_message_text(
                    already_done_text(lang),
                    chat_id=chat_id,
                    message_id=edit_msg_id,
                    reply_markup=None,
                )
                return
            except Exception:
                pass
        await bot.send_message(chat_id, already_done_text(lang), reply_markup=None)
        return

    lang, cur_q_index, answers, last_msg_id = await get_progress(user_id)

    if q_index is not None:
        cur_q_index = q_index

    # если индекс вышел за пределы
    if cur_q_index >= len(SURVEY):
        if all(q.key in answers for q in SURVEY):
            saved = await finalize_response(user_id, lang, answers)
            if saved:
                await bot.send_message(chat_id, thanks(lang), reply_markup=None)
            else:
                await bot.send_message(chat_id, already_done_text(lang), reply_markup=None)
            return

        # найдём первый неотвеченный
        for i, q in enumerate(SURVEY):
            if q.key not in answers:
                cur_q_index = i
                break

    q = SURVEY[cur_q_index]
    q_text, opts = get_text_and_opts(q, lang)

    selected_opt = answers.get(q.key)
    all_answered = all(sq.key in answers for sq in SURVEY)

    header = get_survey_header(lang)
    section = get_section_title(cur_q_index, lang)

    lines = []
    lines.append(header)
    lines.append("────────────────────")
    lines.append(f"📋 *Savol / Вопрос:* {cur_q_index + 1}/{len(SURVEY)}")
    if section:
        lines.append(f"🧩 *{section}*")
    lines.append("────────────────────")
    lines.append(q_text)

    if isinstance(selected_opt, int):
        try:
            lines.append("")
            lines.append(
                "✅ *"
                + ("Tanlangan" if lang == "uz" else "Выбрано")
                + f":* {opts[selected_opt]}"
            )
        except Exception:
            pass

    text = "\n".join(lines)

    inline = kb_single(
        q_index=cur_q_index,
        opts=opts,
        selected_opt=selected_opt if isinstance(selected_opt, int) else None,
        total=len(SURVEY),
        all_answered=all_answered,
    )

    # всегда пытаемся редактировать текущее сообщение (чтобы не было "пустых")
    if edit_msg_id:
        try:
            await bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=edit_msg_id,
                reply_markup=inline,
            )
            await save_progress(user_id, lang, cur_q_index, answers, edit_msg_id)
            return
        except Exception:
            pass

    # если не удалось редактировать — тогда удалим старое и отправим новое
    if last_msg_id:
        try:
            await bot.delete_message(chat_id, last_msg_id)
        except Exception:
            pass

    msg = await bot.send_message(chat_id, text, reply_markup=inline)
    await save_progress(user_id, lang, cur_q_index, answers, msg.message_id)


@router.callback_query(F.data.startswith("ans:"))
async def on_single_answer(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    # если уже сдавал — просто покажем сообщение
    if await has_submission(user_id):
        lang, _, _, _ = await get_progress(user_id)
        await call.answer()
        try:
            await call.message.edit_text(already_done_text(lang))
        except Exception:
            pass
        return

    _, q_index_str, opt_index_str = call.data.split(":")
    q_index = int(q_index_str)
    opt_index = int(opt_index_str)

    lang, _, answers, _ = await get_progress(user_id)

    q = SURVEY[q_index]
    answers[q.key] = opt_index

    await save_progress(user_id, lang, q_index, answers, call.message.message_id)
    await call.answer()

    next_index = q_index + 1

    if next_index < len(SURVEY):
        await send_question(user_id, chat_id, call.bot, q_index=next_index, edit_msg_id=call.message.message_id)
        return

    # конец опроса
    if all(sq.key in answers for sq in SURVEY):
        saved = await finalize_response(user_id, lang, answers)
        try:
            if saved:
                await call.message.edit_text(thanks(lang), reply_markup=None)
            else:
                await call.message.edit_text(already_done_text(lang), reply_markup=None)
        except Exception:
            pass
        return

    # если вдруг кто-то пропустил — идём на первый пропущенный
    for i, sq in enumerate(SURVEY):
        if sq.key not in answers:
            await send_question(user_id, chat_id, call.bot, q_index=i, edit_msg_id=call.message.message_id)
            break


@router.callback_query(F.data.startswith("nav:prev:"))
async def on_nav_prev(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if await has_submission(user_id):
        lang, _, _, _ = await get_progress(user_id)
        await call.answer()
        try:
            await call.message.edit_text(already_done_text(lang), reply_markup=None)
        except Exception:
            pass
        return

    q_index = int(call.data.split(":")[2])
    await call.answer()
    if q_index > 0:
        await send_question(user_id, chat_id, call.bot, q_index=q_index - 1, edit_msg_id=call.message.message_id)


@router.callback_query(F.data.startswith("nav:next:"))
async def on_nav_next(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if await has_submission(user_id):
        lang, _, _, _ = await get_progress(user_id)
        await call.answer()
        try:
            await call.message.edit_text(already_done_text(lang), reply_markup=None)
        except Exception:
            pass
        return

    q_index = int(call.data.split(":")[2])
    await call.answer()
    if q_index < len(SURVEY) - 1:
        await send_question(user_id, chat_id, call.bot, q_index=q_index + 1, edit_msg_id=call.message.message_id)


@router.callback_query(F.data == "nav:finish")
async def on_nav_finish(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if await has_submission(user_id):
        lang, _, _, _ = await get_progress(user_id)
        await call.answer()
        try:
            await call.message.edit_text(already_done_text(lang), reply_markup=None)
        except Exception:
            pass
        return

    lang, _, answers, _ = await get_progress(user_id)

    if not all(q.key in answers for q in SURVEY):
        missing = [i + 1 for i, q in enumerate(SURVEY) if q.key not in answers]
        await call.answer("Не отвечены: " + ", ".join(map(str, missing)), show_alert=True)
        return

    saved = await finalize_response(user_id, lang, answers)
    await call.answer()

    try:
        if saved:
            await call.message.edit_text(thanks(lang), reply_markup=None)
        else:
            await call.message.edit_text(already_done_text(lang), reply_markup=None)
    except Exception:
        if saved:
            await call.bot.send_message(chat_id, thanks(lang), reply_markup=None)
        else:
            await call.bot.send_message(chat_id, already_done_text(lang), reply_markup=None)
