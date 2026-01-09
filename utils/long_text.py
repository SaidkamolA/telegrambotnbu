from aiogram.types import Message

async def send_long_text(message: Message, text: str, chunk_size: int = 3800):
    if len(text) <= chunk_size:
        await message.answer(text)
        return

    parts = []
    buf = ""
    for line in text.split("\n"):
        if len(buf) + len(line) + 1 > chunk_size:
            parts.append(buf)
            buf = line
        else:
            buf = buf + "\n" + line if buf else line
    if buf:
        parts.append(buf)

    for p in parts:
        await message.answer(p)
