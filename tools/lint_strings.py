#!/usr/bin/env python3
"""Механическая проверка игровых строк в черновике шага.

Читает таблицы markdown, где есть колонки «ключ» (или ID) и «текст», в файлах
папки шага или в названных файлах. Проверяет то, что не требует суждения:
ключ по схеме и не занят, текст английский, длина не больше самой длинной
строки того же вида в каноне, стоп-слова детской аудитории и давления.
Суждение (голос героя, загадки) остаётся контролёру.

Запуск: python3 tools/lint_strings.py drafts/<шаг> [файл ...]
Код возврата 1, если есть ошибки. Предупреждения кода не меняют.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = re.compile(r"^(nail|flint|spark|rue|echo|journal|event|curio|board|ui)\.[a-z0-9]+(\.[a-z0-9]+)*$")
CYR = re.compile(r"[А-Яа-яЁё]")
STOP = ["kill", "blood", "dead", "death", "die ", "dies", "gun", "knife", "weapon", "scary", "terrif", "horror",
        "bet ", "jackpot", "gamble", "lucky spin", "casino",
        "hurry", "last chance", "only today", "limited time", "never again", "forever gone", "before it's gone",
        "buy now", "robux", "echoes", "http", "www.", "discord", "tiktok", "youtube"]


def kind(key: str) -> str:
    p = key.split(".")
    if p[0] == "journal":
        return "journal"
    if p[0] == "echo":
        return "note"
    if len(p) > 1 and p[1] == "goal":
        return "goal"
    if len(p) > 2 and p[1].startswith("q") and p[2].startswith("s"):
        return "step"
    return "line"


def tables(text: str):
    """Отдаёт (ключ, текст, номер строки) из таблиц с колонками ключ/ID и текст."""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|\s*:?-{3,}", lines[i + 1]):
            head = [c.strip().lower() for c in lines[i].strip().strip("|").split("|")]
            kc = next((n for n, c in enumerate(head) if c in ("ключ", "id", "key")), None)
            tc = next((n for n, c in enumerate(head) if c in ("текст", "text", "текст (en)")), None)
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                if kc is not None and tc is not None:
                    cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                    if len(cells) > max(kc, tc):
                        yield cells[kc].strip("`"), cells[tc], j + 1
                j += 1
            i = j
        else:
            i += 1


def clean(t: str) -> str:
    t = re.sub(r"\[[^\]]*\]", "", t)            # метки источников
    t = re.sub(r"\(предложено\)", "", t)
    return t.strip().strip('"“”«»').strip()


def measured(key: str, t: str) -> str:
    """Что меряется по длине: у страницы журнала — текст без названия («Название / текст»)."""
    if kind(key) == "journal" and " / " in t:
        return t.split(" / ", 1)[1].strip()
    return t


def main(argv):
    if not argv:
        sys.exit(__doc__)
    files = []
    for a in argv:
        p = pathlib.Path(a)
        if not p.is_absolute():
            p = ROOT / p
        files += sorted(f for f in p.glob("*.md") if f.name not in ("brief.md", "pack.md", "review.md", "decision.md")) if p.is_dir() else [p]

    canon = {}
    for p in [ROOT / "canon" / "lore-bible.md"] + sorted((ROOT / "bibles").rglob("*.md")):
        for k, t, _ in tables(p.read_text(encoding="utf-8")):
            if KEY.match(k):
                canon[k] = clean(t)
    limit = {}
    for k, t in canon.items():
        limit[kind(k)] = max(limit.get(kind(k), 0), len(measured(k, t)))

    errors, warns, n = [], [], 0
    seen = {}
    for f in files:
        rel = f.relative_to(ROOT) if ROOT in f.parents else f
        for k, raw, ln in tables(f.read_text(encoding="utf-8")):
            if not re.match(r"^[a-z]+\.", k):
                continue
            n += 1
            t = clean(raw)
            where = f"{rel}:{ln} {k}"
            if not KEY.match(k):
                errors.append(f"{where}: ключ не по схеме")
            if k in canon and canon[k] != t:
                errors.append(f"{where}: ключ занят в каноне с другим текстом")
            if k in seen and seen[k][0] != t:
                errors.append(f"{where}: ключ повторён с другим текстом ({seen[k][1]})")
            seen.setdefault(k, (t, str(rel)))
            if CYR.search(t):
                errors.append(f"{where}: в тексте кириллица")
            low = " " + t.lower() + " "
            for w in STOP:
                if w in low:
                    errors.append(f"{where}: стоп-слово «{w.strip()}»")
            lim = limit.get(kind(k))
            if lim and len(measured(k, t)) > lim:
                warns.append(f"{where}: {len(measured(k, t))} знаков, самая длинная строка вида «{kind(k)}» в каноне — {lim}")
    print(f"файлов: {len(files)}, строк: {n}, ошибок: {len(errors)}, предупреждений: {len(warns)}")
    print("мерки длины по канону: " + ", ".join(f"{k} {v}" for k, v in sorted(limit.items())))
    for e in errors:
        print("  ОШИБКА " + e)
    for w in warns:
        print("  внимание " + w)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
