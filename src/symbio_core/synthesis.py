from dataclasses import dataclass

@dataclass
class Synthesis:
    option_a: str
    option_b: str
    option_c: str
    tradeoffs: list[str]
    next_step: str

def golden_mean(option_a: str, option_b: str, shared_goal="снизить вред и сохранить полезные цели") -> Synthesis:
    a, b = option_a.strip(), option_b.strip()
    if not a or not b:
        raise ValueError("Both options are required")
    return Synthesis(a, b,
        f"Промежуточный вариант: сохранить проверяемые преимущества обоих подходов, ограничить необратимые шаги и начать с малого теста. Цель: {shared_goal}.",
        ["Компромисс может не удовлетворить сторонников крайних позиций.",
         "Нужны критерии успеха и условия остановки.",
         "Баланс не должен создавать ложное равенство, если факты поддерживают одну сторону."],
        "Сформулировать измеримый тест, критерий остановки и дату пересмотра.")
