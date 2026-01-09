import json
from typing import Dict, Any, Optional, Tuple, List

import aiosqlite

DB_PATH = "survey.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # текущий прогресс (можно проходить, пока не завершил)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER PRIMARY KEY,
            lang TEXT NOT NULL DEFAULT 'uz',
            q_index INTEGER NOT NULL DEFAULT 0,
            answers_json TEXT NOT NULL DEFAULT '{}',
            last_msg_id INTEGER
        );
        """)

        # старые ответы (оставляем, чтобы ничего не сломать)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            lang TEXT NOT NULL,
            answers_json TEXT NOT NULL
        );
        """)

        # ✅ НОВОЕ: финальная сдача (строго 1 раз на user_id)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            user_id INTEGER PRIMARY KEY,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            lang TEXT NOT NULL,
            answers_json TEXT NOT NULL
        );
        """)

        await db.commit()


async def set_lang_and_reset(user_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO progress(user_id, lang, q_index, answers_json, last_msg_id) "
            "VALUES(?, ?, 0, '{}', NULL)",
            (user_id, lang),
        )
        await db.commit()


async def get_progress(user_id: int) -> Tuple[str, int, Dict[str, Any], Optional[int]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT lang, q_index, answers_json, last_msg_id FROM progress WHERE user_id=?",
            (user_id,),
        )
        row = await cur.fetchone()

        if not row:
            await db.execute(
                "INSERT OR REPLACE INTO progress(user_id, lang, q_index, answers_json, last_msg_id) "
                "VALUES(?, 'uz', 0, '{}', NULL)",
                (user_id,),
            )
            await db.commit()
            return "uz", 0, {}, None

        lang, q_index, answers_json, last_msg_id = row
        try:
            answers = json.loads(answers_json)
        except Exception:
            answers = {}

        return lang, int(q_index), answers, last_msg_id


async def save_progress(
    user_id: int,
    lang: str,
    q_index: int,
    answers: Dict[str, Any],
    last_msg_id: Optional[int],
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO progress(user_id, lang, q_index, answers_json, last_msg_id) "
            "VALUES(?, ?, ?, ?, ?)",
            (user_id, lang, q_index, json.dumps(answers, ensure_ascii=False), last_msg_id),
        )
        await db.commit()


# ✅ Проверка: уже сдавал или нет
async def has_submission(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT 1 FROM submissions WHERE user_id=? LIMIT 1",
            (user_id,),
        )
        row = await cur.fetchone()
        return row is not None


# ✅ Финализация: сохраняем строго 1 раз
async def finalize_response(user_id: int, lang: str, answers: Dict[str, Any]) -> bool:
    """
    Возвращает:
    True  -> сохранено (первый раз)
    False -> уже сдавал ранее (не сохраняем повторно)
    """
    payload = json.dumps(answers, ensure_ascii=False)

    async with aiosqlite.connect(DB_PATH) as db:
        # если уже есть submissions.user_id -> повторно не вставится
        cur = await db.execute(
            "INSERT OR IGNORE INTO submissions(user_id, lang, answers_json) VALUES(?, ?, ?)",
            (user_id, lang, payload),
        )
        await db.commit()

        saved = cur.rowcount == 1

        # старую таблицу responses можно НЕ трогать, но если хочешь —
        # можем сохранять туда только если saved == True
        if saved:
            await db.execute(
                "INSERT INTO responses(lang, answers_json) VALUES(?, ?)",
                (lang, payload),
            )
            await db.commit()

        # прогресс удаляем в любом случае (чтобы не зависало)
        await db.execute("DELETE FROM progress WHERE user_id=?", (user_id,))
        await db.commit()

    return saved


async def load_all_responses() -> List[Tuple[str, Dict[str, Any]]]:
    out: List[Tuple[str, Dict[str, Any]]] = []
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT lang, answers_json FROM submissions")
        rows = await cur.fetchall()

        for lang, answers_json in rows:
            try:
                out.append((lang, json.loads(answers_json)))
            except Exception:
                pass

    return out
