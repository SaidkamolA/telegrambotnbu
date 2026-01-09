from dataclasses import dataclass
from typing import List

@dataclass
class Question:
    key: str
    text_uz: str
    text_ru: str
    options_uz: List[str]
    options_ru: List[str]
    multi: bool = False
