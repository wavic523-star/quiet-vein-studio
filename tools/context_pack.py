#!/usr/bin/env python3
"""Собирает пакет контекста шага: drafts/<шаг>/pack.md.

Зачем: роль читает один файл вместо всего снимка канона. Текст разделов
переносится дословно, поэтому метки [canon:файл#заголовок] остаются верными.

Запуск из корня репозитория:
  python3 tools/context_pack.py drafts/<шаг> \
      --canon "lore-bible.md#Герои" --canon "events-monetization.md#События и календарь" \
      --heroes rue,nail --owner E-1,E-3,О-16 --bible story/arc.md

Только чтение canon/, bibles/, decisions/, docs/ и запись одного файла pack.md.
Сеть не нужна.
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY_RE = re.compile(r"\b(?:nail|flint|spark|rue|echo|journal|event|curio|board|ui|promo)\.[a-z0-9]+(?:\.[a-z0-9]+)*\b")
HERO_NAMES = {
    "nail": ["Old Nail", "Старый Гвоздь", "Гвоздь", "nail."],
    "flint": ["Flint", "Кремень", "flint."],
    "spark": ["Spark", "Искра", "Искры", "spark."],
    "rue": ["Aunt Rue", "Лукерья", "Лукерьи", "rue."],
    "echo": ["Echo", "Эхо", "echo."],
}


def section(path: pathlib.Path, head: str):
    """Возвращает (заголовок, текст раздела) по началу заголовка."""
    lines = path.read_text(encoding="utf-8").split("\n")
    for i, line in enumerate(lines):
        if line.startswith("#") and line.lstrip("#").strip().startswith(head):
            level = len(line) - len(line.lstrip("#"))
            out = [line]
            for nxt in lines[i + 1:]:
                if nxt.startswith("#") and len(nxt) - len(nxt.lstrip("#")) <= level:
                    break
                out.append(nxt)
            return line.lstrip("#").strip(), "\n".join(out).rstrip()
    return None, None


def hero_rows(text: str, names):
    rows = []
    for line in text.split("\n"):
        if line.startswith("|") and any(n in line for n in names):
            rows.append(line)
    return rows


def owner_entries(ids):
    owner = (ROOT / "decisions" / "OWNER.md").read_text(encoding="utf-8")
    esc = (ROOT / "decisions" / "ESCALATIONS.md").read_text(encoding="utf-8")
    out = []
    for i in ids:
        i = i.strip()
        if not i:
            continue
        if i[0] in "EЕ":
            num = i.split("-")[1]
            m = re.search(r"###\s*[EЕ]-" + num + r"\b(.*?)(?=\n###\s|\Z)", esc, re.S)
            if m:
                body = m.group(1)
                what = re.search(r"\*\*Что решаем и зачем:\*\*\s*(.*)", body)
                ans = re.search(r"\*\*Ответ владельца:\*\*\s*(.*)", body)
                opts = re.search(r"\*\*Варианты:\*\*\s*(.*)", body)
                out.append(f"- **E-{num}.** {what.group(1) if what else ''}\n  Варианты: {opts.group(1) if opts else ''}\n  Ответ владельца: {ans.group(1) if ans else 'нет'}")
            else:
                out.append(f"- **{i}** — не найдено")
        else:
            num = i.split("-")[1]
            m = re.search(r"^\|\s*[ОO]-" + num + r"\s*\|.*$", owner, re.M)
            out.append(("- " + m.group(0)) if m else f"- **{i}** — не найдено")
    return out


# Наборы разделов канона по маршрутам методички (docs/GUIDE.md, раздел 3).
# «Не делаем до запуска» входит всегда: короткий и нужен любой роли.
PRESETS = {
    "event": ["lore-bible.md#ТЗ лор-слоя", "events-monetization.md#События и календарь",
              "events-monetization.md#Монетизация", "lore-bible.md#Главы и грайнд",
              "lore-bible.md#Правила текста", "lore-bible.md#Герои", "lore-bible.md#Голоса героев",
              "stages.md#Этап 5"],
    "hero": ["lore-bible.md#Герои", "lore-bible.md#Облик героев", "lore-bible.md#Голоса героев",
             "lore-bible.md#Петля, загадки", "lore-bible.md#Рост героя", "lore-bible.md#Карта точек",
             "lore-bible.md#Виральные крючки", "stages.md#Этап 5"],
    "arc": ["lore-bible.md#Основа сюжета", "lore-bible.md#Главы и грайнд", "lore-bible.md#Петля, загадки",
            "lore-bible.md#Герои", "lore-bible.md#ТЗ лор-слоя", "events-monetization.md#События и календарь",
            "stages.md#Этап 5"],
    "quest": ["lore-bible.md#Рост героя", "lore-bible.md#Голоса героев", "lore-bible.md#Главы и грайнд",
              "lore-bible.md#Карта точек", "lore-bible.md#Правила текста"],
    "writing": ["lore-bible.md#Правила текста", "lore-bible.md#Герои", "lore-bible.md#Голоса героев"],
    # Коммерческие маршруты (drafts/2026-11-16-commerce-orchestra/design.md, раздел 6).
    # Принятые документы bibles/commerce/ добавляются ключом --bible.
    "commerce": ["events-monetization.md#Монетизация", "events-monetization.md#События и календарь",
                 "events-monetization.md#Метрики", "not-doing-later.md#Не делаем до запуска",
                 "not-doing-later.md#Позже", "lore-bible.md#Редкие предметы",
                 "lore-bible.md#Виральные крючки", "lore-bible.md#ТЗ лор-слоя", "stages.md#Этап 5"],
}
ALWAYS = ["not-doing-later.md#Не делаем до запуска"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step")
    ap.add_argument("--canon", action="append", default=[], help="файл#начало заголовка")
    ap.add_argument("--bible", action="append", default=[], help="путь под bibles/, целиком")
    ap.add_argument("--heroes", default="", help="nail,flint,spark,rue,echo")
    ap.add_argument("--owner", default="", help="E-1,О-16")
    ap.add_argument("--no-keys", action="store_true")
    ap.add_argument("--preset", choices=sorted(PRESETS), help="набор разделов канона по маршруту")
    a = ap.parse_args()
    specs = (PRESETS.get(a.preset, []) if a.preset else []) + a.canon + ALWAYS
    seen = set()
    a.canon = [x for x in specs if not (x in seen or seen.add(x))]

    step = pathlib.Path(a.step)
    if not step.is_absolute():
        step = ROOT / step
    if not (step / "brief.md").exists():
        sys.exit("нет brief.md в папке шага")
    snap = (ROOT / "canon" / "SNAPSHOT.txt").read_text(encoding="utf-8").strip().replace("\n", ", ")
    out = [f"# Пакет контекста шага {step.name}",
           "",
           f"Собрано скриптом `tools/context_pack.py`. Снимок канона: {snap}.",
           "Разделы канона перенесены дословно: ставь метку `[canon:<файл>#<заголовок>]` по строке «Источник» над разделом.",
           "Нужен раздел, которого здесь нет, — прочитай его в `canon/` и назови в ответе дирижёру; догадкой пробел не заполняй.",
           ""]
    out += ["## 1. Памятка роли", "", (ROOT / "docs" / "ROLE-DIGEST.md").read_text(encoding="utf-8").split("\n", 1)[1].strip(), ""]

    if a.owner:
        out += ["## 2. Решения владельца для шага", ""] + owner_entries(a.owner.split(",")) + [""]

    out += ["## 3. Разделы канона", ""]
    missing = []
    for spec in a.canon:
        fname, _, head = spec.partition("#")
        title, text = section(ROOT / "canon" / fname, head)
        if text is None:
            missing.append(spec)
            continue
        out += [f"Источник: `[canon:{fname}#{title}]`", "", text, ""]

    heroes = [h for h in a.heroes.split(",") if h.strip()]
    if heroes:
        lore = (ROOT / "canon" / "lore-bible.md").read_text(encoding="utf-8")
        out += ["## 4. Строки таблиц канона о героях шага", "",
                "Выборка строк из `canon/lore-bible.md`; заголовок раздела каждой строки смотри в файле, если ставишь метку.", ""]
        cur = ""
        for line in lore.split("\n"):
            if line.startswith("#"):
                cur = line.lstrip("#").strip()
            elif line.startswith("|"):
                for h in heroes:
                    if any(n in line for n in HERO_NAMES.get(h, [h])):
                        out.append(f"[{cur}] {line}")
                        break
        out.append("")

    for b in a.bible:
        p = ROOT / "bibles" / b
        if p.exists():
            out += [f"## Принятый документ `bibles/{b}`", "", p.read_text(encoding="utf-8").strip(), ""]
        else:
            missing.append("bibles/" + b)

    if not a.no_keys:
        keys = {}
        srcs = [ROOT / "canon" / "lore-bible.md"] + sorted((ROOT / "bibles").rglob("*.md"))
        for p in srcs:
            for k in KEY_RE.findall(p.read_text(encoding="utf-8")):
                keys.setdefault(k, p.relative_to(ROOT).as_posix())
        out += ["## 5. Занятые ключи строк", "",
                "Новый ключ не должен совпадать ни с одним из этих. Схема: `<hero>.first.N`, `nail.goal.N`, `<hero>.idle.N`, `<hero>.chN[.слово]`, `echo.nN`, `journal.pN`, `event.<событие>.N`, `<hero>.q1.sN`, `<hero>.q1.offer`, `<hero>.q1.done`, `<hero>.loop.N`.", "",
                ", ".join(f"`{k}`" for k in sorted(keys)), ""]

    finds = []
    for fp in sorted((ROOT / "drafts" / "_findings").glob("*.md")):
        sec = ""
        for line in fp.read_text(encoding="utf-8").split("\n"):
            if line.startswith("## "):
                sec = line[3:].strip()
            m = re.match(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|", line)
            if m and sec:
                finds.append(f"- {fp.name}, «{sec}» № {m.group(1)}: {m.group(2)}")
    if finds:
        out += ["## 6. Известные находки канона", "",
                "Уже записаны в `drafts/_findings/`: не ищи их заново, ссылайся на номер; новая находка — только если её здесь нет.", ""] + finds + [""]

    if missing:
        out += ["## Не найдено", ""] + [f"- {m}" for m in missing] + [""]
    target = step / "pack.md"
    target.write_text("\n".join(out), encoding="utf-8")
    print(f"{target.relative_to(ROOT)}: {len(chr(10).join(out))} знаков, разделов канона: {len(a.canon) - len([m for m in missing if '#' in m])}, не найдено: {len(missing)}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
