from survey.questions import Question

PROJECT_TITLE = "Kichik va o’rta biznesni moliyalashtirishni takomillashtirish"


def thanks(lang: str) -> str:
    if lang == "ru":
        return (
            "✅ *Спасибо!* Опрос завершён.\n\n"
            "Ваш ответ принят. Это поможет улучшить анализ проблем кредитования МСБ.\n"
            f"📌 {PROJECT_TITLE}"
        )
    return (
        "✅ *Rahmat!* So‘rovnoma yakunlandi.\n\n"
        "Javobingiz qabul qilindi. Bu KO‘B kreditlash muammolarini tahlil qilishga yordam beradi.\n"
        f"📌 {PROJECT_TITLE}"
    )


def get_text_and_opts(q: Question, lang: str):
    """
    Возвращает текст вопроса и список вариантов под выбранный язык.
    Нужно для handlers/user.py (чтобы не было ImportError).
    """
    if lang == "ru":
        return q.text_ru, q.options_ru
    return q.text_uz, q.options_uz
