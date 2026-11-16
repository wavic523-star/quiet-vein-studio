#!/usr/bin/env python3
"""Механическая проверка коммерческих черновиков шага.

Ловит то, что не требует суждения, до проверяющего коммерции (навык
commerce-check): цена без ориентира рынка, один вариант цены, платное без
пары «игрой и платно», случайность в платном, слова срочности, даты не из
снимка, повторные и висячие идентификаторы, строки рынка без ссылки и со
старой датой проверки. Суждение (цена разумна, давление на ребёнка) остаётся
проверяющему.

Строка — строка таблицы markdown, первая ячейка которой начинается с РЫН-,
КАЛ-, КАТ- или ПРО- и числа. Колонки находятся по шапке таблицы, по ключевым
словам: «цена» (без «вариант»), «ориентир», «вариант» (без «платн»; у сводной
таблицы этапа это «ниже» и «выше»), «платн», «игрой», «источник»,
«дата проверки». Нет колонки в шапке — проверка, которой она нужна,
пропускается. Справочником идентификаторов всегда читаются bibles/commerce/*.md.

Оговорки разбора: повтор идентификатора считается только у строк, чья первая
ячейка — ровно идентификатор, и только в таблицах с одинаковой шапкой
(сводная таблица этапа пересказывает каталог и повтором не считается).
Слова срочности ищутся также в строках текста (не таблицы) со словами
«уведомлен», «объявлен», «плитк» или ключом promo. — так ловится уведомление,
написанное списком. Строки рынка проверяются только в таблицах с колонкой «источник…» (первое слово шапки) (в таблицах
проверяющих РЫН-N лишь упомянуты). Ссылки в строке со словами «не используются»
или «сняты» (список снятых номеров) висячими не считаются. Папка читается
рекурсивно. Дата проверки строки рынка берётся из колонки «дата
проверки», а если её нет — из строки файла «Дата проверки …: <дата>».

Запуск: python3 -I tools/lint_commerce.py [--today ГГГГ-ММ-ДД] [папка шага или файл ...]
Без путей проверяется bibles/commerce/. Скрипт ничего не пишет.
Код возврата 1, если есть ошибки. Предупреждения кода не меняют.
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ID_RE = re.compile(r"(РЫН|КАЛ|КАТ|ПРО)-(\d+)")
ROW_RE = re.compile(r"^(РЫН|КАЛ|КАТ|ПРО)-(\d+)")
SEP_RE = re.compile(r"^\|\s*:?-{3,}")
NUM_RE = re.compile(r"\d+(?:[.,]\d+)?")
SKIP_NAMES = ("brief.md", "pack.md", "review.md", "decision.md")
RANDOM = ["случайн", "ящик", "crate", "random", "шанс", "удач", "luck"]
URGENT = ["last chance", "forever", "only today", "hurry", "последний шанс", "только сегодня", "успей", "навсегда исчез"]
NO_SOURCE = ["открыто до", "не сгорает", "нет данных"]
MONTHS = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7, "августа": 8,
          "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12}
SNAP_DATE_RE = re.compile(r"(\d{1,2})(?:\s*[–—-]\s*(\d{1,2}))?\s+(ноября|декабря|января|февраля|марта)")
DATE_RE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})|(\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+(\d{4})")
RETIRED_RE = re.compile(r"не использу|сняты", re.I)
TEXT_URGENT_RE = re.compile(r"уведомлен|объявлен|плитк|promo\.", re.I)


REPORT_NAMES = ("review.md", "decision.md", "lore-check.md", "lore-keeper.md",
                "growth-reviewer.md", "commerce-reviewer.md")


def cells(line: str):
    inner = line.strip().strip("|")
    return [c.strip() for c in re.split(r"(?<!\\)\|", inner)]


def norm_id(cell: str) -> str:
    return cell.replace("*", "").replace("`", "").strip()


def find_col(head, key, exclude=()):
    for n, h in enumerate(head):
        if key in h and not any(x in h for x in exclude):
            return n
    return None


def parse_date(s: str):
    m = DATE_RE.search(s)
    if not m:
        return None
    try:
        if m.group(1):
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        return datetime.date(int(m.group(6)), MONTHS[m.group(5)], int(m.group(4)))
    except ValueError:
        return None


def rows(text: str):
    """Отдаёт (номер строки, ячейки, шапка) для строк с идентификатором в первой ячейке."""
    lines = text.split("\n")
    head = None
    for i, line in enumerate(lines):
        if line.startswith("|"):
            if i + 1 < len(lines) and SEP_RE.match(lines[i + 1]):
                head = [c.lower() for c in cells(line)]
            elif SEP_RE.match(line):
                pass
            elif head is not None:
                cs = cells(line)
                if cs and ROW_RE.match(norm_id(cs[0])):
                    yield i + 1, cs, head
        else:
            head = None


def has_word(text: str, words):
    low = text.lower()
    return [w for w in words if w in low]


def main(argv):
    today = datetime.date.today()
    paths = []
    it = iter(argv)
    for a in it:
        if a == "--today":
            try:
                today = datetime.date.fromisoformat(next(it))
            except (StopIteration, ValueError):
                sys.exit("--today ожидает дату ГГГГ-ММ-ДД")
        elif a in ("-h", "--help"):
            sys.exit(__doc__)
        else:
            paths.append(a)
    if not paths:
        paths = ["bibles/commerce"]
    files = []
    for a in paths:
        p = pathlib.Path(a)
        if not p.is_absolute():
            p = ROOT / p
        if p.is_dir():
            files += sorted(f for f in p.rglob("*.md") if f.name not in SKIP_NAMES)
        elif p.exists():
            files.append(p)
        else:
            sys.exit(f"нет пути: {a}")

    # Справочник идентификаторов: строки bibles/commerce/*.md.
    known = set()
    for f in sorted((ROOT / "bibles" / "commerce").glob("*.md")):
        for _, cs, _ in rows(f.read_text(encoding="utf-8")):
            m = ROW_RE.match(norm_id(cs[0]))
            known.add(f"{m.group(1)}-{m.group(2)}")

    # Тексты снимка для проверки дат КАЛ.
    snap = ""
    for p in sorted((ROOT / "canon").glob("*.md")) + sorted((ROOT / "bibles" / "story").rglob("*.md")):
        snap += p.read_text(encoding="utf-8") + "\n"
    snap = re.sub(r"\s*[–—-]\s*", "–", snap)

    errors, warns = [], []
    nrows = 0
    defined = {}          # идентификатор -> (шапка, где)
    refs = []             # (идентификатор, где)
    file_text = {}

    def err(where, ident, msg):
        errors.append(f"{where} {ident}: {msg}")

    def warn(where, ident, msg):
        warns.append(f"{where} {ident}: {msg}")

    for f in files:
        rel = f.relative_to(ROOT).as_posix() if ROOT in f.parents else str(f)
        text = f.read_text(encoding="utf-8")
        file_text[f] = text
        lines = text.split("\n")
        # дата проверки на уровне файла — запасной вариант для строк рынка
        file_check = None
        for ln_text in lines:
            m = re.search(r"[Дд]ата проверки[^:\n]*:\s*(.+)", ln_text)
            if m and parse_date(m.group(1)):
                file_check = parse_date(m.group(1))
                break

        for ln, cs, head in rows(text):
            nrows += 1
            ident_cell = norm_id(cs[0])
            m = ROW_RE.match(ident_cell)
            kind, ident = m.group(1), f"{m.group(1)}-{m.group(2)}"
            where = f"{rel}:{ln}"
            row = " | ".join(cs)
            if ident_cell == ident:
                if ident in defined and defined[ident][0] == tuple(head):
                    err(where, ident, f"идентификатор повторён ({defined[ident][1]})")
                defined.setdefault(ident, (tuple(head), where))

            def col(n):
                return cs[n] if n is not None and n < len(cs) else None

            price_i = find_col(head, "цена", ("вариант",))
            bench_i = find_col(head, "ориентир")
            var_i = find_col(head, "вариант", ("платн",))
            below_i, above_i = find_col(head, "ниже"), find_col(head, "выше")
            paid_i = find_col(head, "платн")
            game_i = find_col(head, "игрой")
            date_i = find_col(head, "дата проверки")

            if kind == "КАТ":
                price = col(price_i)
                if price is not None and NUM_RE.search(price):
                    if not re.search(r"РЫН-\d+", row):
                        err(where, ident, "цена без ориентира: в строке нет РЫН-N")
                    if var_i is not None:
                        nvar = len(NUM_RE.findall(col(var_i) or ""))
                    elif below_i is not None and above_i is not None:
                        nvar = len(NUM_RE.findall((col(below_i) or "") + " " + (col(above_i) or "")))
                    else:
                        nvar = None
                    if nvar is not None and nvar < 2:
                        err(where, ident, f"вариантов цены меньше двух (чисел: {nvar})")
                paid = col(paid_i)
                if paid is not None:
                    pl = paid.lower().strip("` ")
                    has_paid = bool(pl) and not pl.startswith("нет") and pl not in ("—", "-", "–")
                    if has_paid:
                        game = col(game_i)
                        if game is not None:
                            gl = game.lower().strip("` ")
                            if not gl or gl.startswith("нет") or gl in ("—", "-", "–"):
                                err(where, ident, "платный вариант без заработанной пары: колонка «игрой» пуста")
                        for w in has_word(paid, RANDOM):
                            err(where, ident, f"случайность в платном варианте: «{w}»")

            if kind in ("КАЛ", "КАТ", "ПРО") or "promo." in row:
                for w in has_word(row, URGENT):
                    err(where, ident, f"слово срочности «{w}»")

            if kind == "КАЛ":
                if has_word(row, NO_SOURCE) and not re.search(r"\[[^\]]+:[^\]]+\]", row):
                    for w in has_word(row, NO_SOURCE):
                        warn(where, ident, f"«{w}» без метки источника в строке")
                for dm in SNAP_DATE_RE.finditer(row):
                    s = re.sub(r"\s*[–—-]\s*", "–", dm.group(0))
                    if s not in snap:
                        warn(where, ident, f"даты «{dm.group(0)}» нет в canon/ и bibles/story/")

            if kind == "РЫН" and any(h.startswith("источник") for h in head):
                if "http" not in row:
                    warn(where, ident, "в строке рынка нет ссылки (http)")
                chk = parse_date(col(date_i) or "") if date_i is not None else file_check
                if chk is None:
                    pass
                elif (today - chk).days > 30:
                    warn(where, ident, f"дата проверки {chk.isoformat()} старше 30 дней от {today.isoformat()}")

        # слова срочности в строках текста (списки, абзацы)
        for n, line in enumerate(lines, 1):
            if not line.startswith("|") and TEXT_URGENT_RE.search(line):
                for w in has_word(line, URGENT):
                    err(f"{rel}:{n}", "текст", f"слово срочности «{w}» (уведомление, плитка или ключ promo.)")
            if RETIRED_RE.search(line):
                continue
            for m in ID_RE.finditer(line):
                refs.append((f"{m.group(1)}-{m.group(2)}", f"{rel}:{n}"))

    seen = set()
    for ident, where in refs:
        name = where.rsplit(":", 1)[0].rsplit("/", 1)[-1]
        if name in REPORT_NAMES or name.endswith("-report.md"):
            continue  # отчёт проверяющего вправе ссылаться на строку, которую автор потом снял
        if ident not in defined and ident not in known and (ident, where) not in seen:
            seen.add((ident, where))
            err(where, ident, "ссылка на идентификатор, которого нет в проверяемых файлах и в bibles/commerce/")

    print(f"файлов: {len(files)}, строк: {nrows}, ошибок: {len(errors)}, предупреждений: {len(warns)}")
    for e in errors:
        print("  ОШИБКА " + e)
    for w in warns:
        print("  внимание " + w)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
