from dataclasses import dataclass
from typing import List


# =========================
# Question model
# =========================

@dataclass
class Question:
    key: str
    text_uz: str
    text_ru: str
    options_uz: List[str]
    options_ru: List[str]
    multi: bool = False


# =========================
# Section titles
# =========================

SECTION_TITLES = {
    1: {
        "uz": "I. Respondentlarning ijtimoiy-iqtisodiy va institutsional tavsifi",
        "ru": "I. Социально-экономическая и институциональная характеристика респондентов",
    },
    6: {
        "uz": "II. Kreditga ehtiyoj va foydalanish xususiyatlari",
        "ru": "II. Потребности в кредите и особенности его использования",
    },
    11: {
        "uz": "III. Kreditlashdagi asosiy muammolar",
        "ru": "III. Основные проблемы кредитования",
    },
    16: {
        "uz": "IV. Institutsional va tizimli muammolar",
        "ru": "IV. Институциональные и системные проблемы",
    },
    21: {
        "uz": "V. Yechimlar va takliflar",
        "ru": "V. Решения и предложения",
    },
    26: {
        "uz": "VI. Yakuniy baholash",
        "ru": "VI. Итоговая оценка",
    },
}


def get_section_title(q_index: int, lang: str) -> str | None:
    q_num = q_index + 1
    last_title = None
    for start_q, titles in SECTION_TITLES.items():
        if q_num >= start_q:
            last_title = titles.get(lang)
    return last_title


def get_survey_header(lang: str) -> str:
    """
    Заголовок опроса убран по требованию.
    Чтобы handlers не ломались — возвращаем пустую строку.
    """
    return ""


# =========================
# Survey questions (30)
# =========================

SURVEY: List[Question] = [

    Question("q1",
        "1) Korxonangiz faoliyat turi:",
        "1) Вид деятельности вашей компании:",
        ["Ishlab chiqarish", "Savdo", "Xizmat ko‘rsatish", "Qishloq xo‘jaligi", "Boshqa"],
        ["Производство", "Торговля", "Услуги", "Сельское хозяйство", "Другое"]
    ),

    Question("q2",
        "2) Korxona faoliyat yuritayotgan hudud:",
        "2) Регион деятельности компании:",
        ["Toshkent shahri", "Samarqand viloyati", "Surxondaryo viloyati", "Viloyat / shahar markazi", "Tuman / qishloq"],
        ["г. Ташкент", "Самаркандская область", "Сурхандарьинская область", "Центр области / города", "Район / село"]
    ),

    Question("q3",
        "3) Korxona yuridik maqomi:",
        "3) Юридический статус компании:",
        ["Yakka tartibdagi tadbirkor", "MChJ", "Fermer xo‘jaligi", "Boshqa"],
        ["ИП", "ООО", "Фермерское хозяйство", "Другое"]
    ),

    Question("q4",
        "4) Faoliyat yuritish muddati:",
        "4) Срок деятельности:",
        ["1 yilgacha", "1–3 yil", "3–5 yil", "5 yildan ortiq"],
        ["До 1 года", "1–3 года", "3–5 лет", "Более 5 лет"]
    ),

    Question("q5",
        "5) So‘nggi 3 yil ichida bank kreditidan foydalangansizmi?",
        "5) Пользовались ли банковским кредитом за последние 3 года?",
        ["Ha", "Yo‘q"],
        ["Да", "Нет"]
    ),

    Question("q6",
        "6) Kreditga asosiy ehtiyojingiz qaysi yo‘nalishda?",
        "6) Основная потребность в кредите:",
        ["Aylanma mablag‘", "Asosiy vositalar", "Texnologiya yangilash", "Eksport / import", "Innovatsion loyiha"],
        ["Оборотные средства", "Основные средства", "Обновление технологий", "Экспорт / импорт", "Инновационный проект"]
    ),

    Question("q7",
        "7) Kredit olishda asosiy maqsad nima?",
        "7) Основная цель кредита:",
        ["Ishlab chiqarishni kengaytirish", "Moliyaviy barqarorlik", "Yangi bozorlar", "Likvidlik muammosini hal qilish"],
        ["Расширение производства", "Финансовая стабильность", "Новые рынки", "Решение проблем ликвидности"]
    ),

    Question("q8",
        "8) Kredit muddati siz uchun qanchalik mos?",
        "8) Насколько подходит срок кредита?",
        ["Juda mos", "Qisman mos", "Mos emas"],
        ["Полностью подходит", "Частично", "Не подходит"]
    ),

    Question("q9",
        "9) Kredit foiz stavkasi biznes rentabelligiga mos keladimi?",
        "9) Соответствует ли ставка рентабельности бизнеса?",
        ["To‘liq mos", "Qisman mos", "Mutlaqo mos emas"],
        ["Полностью", "Частично", "Совсем не соответствует"]
    ),

    Question("q10",
        "10) Kredit ajratish jarayoni siz uchun:",
        "10) Процесс получения кредита:",
        ["Juda murakkab", "O‘rtacha", "Oddiy"],
        ["Очень сложный", "Средний", "Простой"]
    ),

    Question("q11",
        "11) Kredit olishdagi eng katta muammo:",
        "11) Самая большая проблема при получении кредита:",
        ["Garov yetishmasligi", "Yuqori foiz stavkasi", "Hujjatlar murakkabligi", "Bank talablari mos emas", "Rad sababi tushuntirilmaydi"],
        ["Недостаток залога", "Высокая ставка", "Сложные документы", "Требования банка не подходят", "Причины отказа не объясняют"]
    ),

    Question("q12",
        "12) Garov qiymati kredit summasiga nisbatan:",
        "12) Стоимость залога относительно суммы кредита:",
        ["Juda yuqori", "O‘rtacha", "Qoniqarli"],
        ["Очень высокая", "Средняя", "Приемлемая"]
    ),

    Question("q13",
        "13) Garov ta’minoti sifatida qaysi aktiv?",
        "13) Какой актив можете предоставить в залог?",
        ["Ko‘chmas mulk", "Asbob-uskunalar", "Tovar zaxiralari", "Intellektual mulk", "Garov yo‘q"],
        ["Недвижимость", "Оборудование", "Товарные запасы", "Интеллектуальная собственность", "Залога нет"]
    ),

    Question("q14",
        "14) Moliyaviy hisobotlar muammomi?",
        "14) Финансовая отчетность — проблема?",
        ["Ha, katta muammo", "Qisman", "Muammo emas"],
        ["Да, большая проблема", "Частично", "Не проблема"]
    ),

    Question("q15",
        "15) Risk baholash real faoliyatni aks ettiradimi?",
        "15) Оценка риска отражает реальную деятельность?",
        ["Ha", "Qisman", "Yo‘q"],
        ["Да", "Частично", "Нет"]
    ),

    Question("q16",
        "16) Davlat kafolatlari yoki subsidiyalar mavjudmi?",
        "16) Есть ли госгарантии или субсидии?",
        ["Ha", "Bilmayman", "Yo‘q"],
        ["Да", "Не знаю", "Нет"]
    ),

    Question("q17",
        "17) Bank xodimlari malakasi qoniqtiradimi?",
        "17) Устраивает ли квалификация сотрудников банка?",
        ["To‘liq", "Qisman", "Yo‘q"],
        ["Полностью", "Частично", "Нет"]
    ),

    Question("q18",
        "18) KO‘B uchun maxsus kredit mahsulotlari yetarlimi?",
        "18) Достаточно ли спецкредитов для МСБ?",
        ["Ha", "Qisman", "Yo‘q"],
        ["Да", "Частично", "Нет"]
    ),

    Question("q19",
        "19) Raqamli kreditlash tizimlari ishlayaptimi?",
        "19) Работают ли цифровые кредитные системы?",
        ["Samarali", "Qisman", "Umuman yo‘q"],
        ["Эффективно", "Частично", "Не работают"]
    ),

    Question("q20",
        "20) Kredit rad etilganda sabablar tushuntiriladimi?",
        "20) Объясняют ли причины отказа?",
        ["Ha", "Qisman", "Yo‘q"],
        ["Да", "Частично", "Нет"]
    ),

    Question("q21",
        "21) Kreditlashni eng ko‘p yengillashtiruvchi chora:",
        "21) Самая эффективная мера для упрощения кредитования:",
        ["Foiz stavkasini pasaytirish", "Garov talabini yumshatish", "Davlat kafolati", "Raqamli kreditlash", "Skoringni takomillashtirish"],
        ["Снижение ставок", "Смягчение залога", "Госгарантии", "Цифровое кредитование", "Улучшение скоринга"]
    ),

    Question("q22",
        "22) Garovsiz kredit qanchalik muhim?",
        "22) Насколько важен кредит без залога?",
        ["Juda muhim", "Muhim", "Ahamiyatsiz"],
        ["Очень важно", "Важно", "Не важно"]
    ),

    Question("q23",
        "23) Cash-flow asosiy mezon bo‘lishi kerakmi?",
        "23) Должен ли cash-flow быть основным критерием?",
        ["Ha", "Qisman", "Yo‘q"],
        ["Да", "Частично", "Нет"]
    ),

    Question("q24",
        "24) KO‘B uchun alohida skoring modeli zarurmi?",
        "24) Нужна ли отдельная скоринговая модель для МСБ?",
        ["Ha", "Qisman", "Yo‘q"],
        ["Да", "Частично", "Нет"]
    ),

    Question("q25",
        "25) Davlat–bank–tadbirkor hamkorligi samaralimi?",
        "25) Эффективно ли сотрудничество государство–банк–бизнес?",
        ["Ha", "Qisman", "Yo‘q"],
        ["Да", "Частично", "Нет"]
    ),

    Question("q26",
        "26) Amaldagi kreditlash tizimi KO‘B rivojiga xizmat qiladimi?",
        "26) Текущая система кредитования способствует развитию МСБ?",
        ["Ha", "Qisman", "Yo‘q"],
        ["Да", "Частично", "Нет"]
    ),

    Question("q27",
        "27) Kreditlash sharoitlari yaxshilansa biznesingiz:",
        "27) Если условия улучшатся, бизнес:",
        ["Kengayadi", "Barqarorlashadi", "O‘zgarmaydi"],
        ["Расширится", "Стабилизируется", "Не изменится"]
    ),

    Question("q28",
        "28) Kredit mablag‘laridan foydalanish samaradorligi:",
        "28) Эффективность использования кредитных средств:",
        ["Yuqori", "O‘rtacha", "Past"],
        ["Высокая", "Средняя", "Низкая"]
    ),

    Question("q29",
        "29) Banklar bilan hamkorlik darajangiz:",
        "29) Уровень сотрудничества с банками:",
        ["Yuqori ishonch", "O‘rtacha", "Past"],
        ["Высокое доверие", "Среднее", "Низкое"]
    ),

    Question("q30",
        "30) Eng muhim tizimli yechim:",
        "30) Самое важное системное решение:",
        ["Skoring va raqamlashtirish", "Davlat kafolatlari", "Foiz siyosati", "Bank siyosatini isloh qilish", "Kompleks yondashuv"],
        ["Скоринг и цифровизация", "Госгарантии", "Процентная политика", "Реформа политики банков", "Комплексный подход"]
    ),
]
