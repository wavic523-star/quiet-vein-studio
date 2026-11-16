#!/usr/bin/env python3
"""Режет выгрузку плана (markdown) на файлы снимка в canon/.

Запуск: python3 tools/canon_snapshot.py <plan.md> <версия плана> "<дата выгрузки>"
Скрипт только читает plan.md и пишет в canon/. Сеть не нужна.
"""
import re
import sys
from pathlib import Path

PLAN_URL = "https://claude.ai/artifact/PYAV7Z6Ak4zjBRFodgk38j"

# Заголовок второго уровня плана -> файл снимка. Журнал и «Источники» не берём.
SECTIONS = [
    (r"^Что есть сейчас", "plan-state.md"),
    (r"^Решения за вами", "decisions.md"),
    (r"^Этап \d", "stages.md"),
    (r"^События и календарь", "events-monetization.md"),
    (r"^Монетизация", "events-monetization.md"),
    (r"^Метрики", "events-monetization.md"),
    (r"^Библиотеки", "libraries.md"),
    (r"^Не делаем", "not-doing-later.md"),
    (r"^Позже", "not-doing-later.md"),
    (r"^Порядок шага и агенты", "step-order-agents.md"),
    (r"^Рабочие планы", "work-plans.md"),
    (r"^Лор-библия", "lore-bible.md"),
]


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    plan, rev, date = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    out_dir = Path(__file__).resolve().parent.parent / "canon"
    out_dir.mkdir(exist_ok=True)
    chunks: dict[str, list[str]] = {"plan-state.md": ["## Вступление", ""]}
    target = "plan-state.md"  # текст до первого раздела: вердикт и цель
    for line in plan.read_text(encoding="utf-8").splitlines():
        if target == "plan-state.md" and (line.startswith("# ") or "@" in line):
            continue  # заголовок документа и строка с автором в снимок не идут
        m = re.match(r"^## (.+)$", line)
        if m:
            target = None
            for pattern, name in SECTIONS:
                if re.match(pattern, m.group(1)):
                    target = name
                    break
        if target:
            chunks.setdefault(target, []).append(line)
    header = (
        f"> Снимок плана. Версия плана: {rev}. Выгрузка: {date}.\n"
        f"> Только чтение. Источник правды — план: {PLAN_URL}\n"
        f"> Если снимок и план расходятся, действует план. Править этот файл нельзя.\n\n"
    )
    for name, lines in chunks.items():
        (out_dir / name).write_text(header + "\n".join(lines).rstrip() + "\n", encoding="utf-8")
        print(f"{name}: {len(lines)} строк")
    (out_dir / "SNAPSHOT.txt").write_text(f"rev={rev}\ndate={date}\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
