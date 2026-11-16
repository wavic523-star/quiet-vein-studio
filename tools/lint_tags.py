#!/usr/bin/env python3
"""Проверка меток источников в репозитории студии.

Что читает: все .md в plugin/, docs/, bibles/, drafts/, tests/, BACKLOG.md.
Что проверяет: метки [canon:файл#заголовок], [readme:заголовок], [владелец:О-N],
[владелец:E-N] открываются (у вопроса E-N должен быть непустой ответ владельца);
любая другая метка, начинающаяся с «[владелец», считается ошибкой; старых меток
[canon:project-readme.md#…] нет. Содержание строки с источником не сверяет:
это работа контролёра.
Запуск: python3 tools/lint_tags.py [папка шага или файл ...]
Код возврата 1, если есть неоткрывающиеся метки.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

def headings(path):
    if not path.exists():
        return None
    return [l.lstrip('#').strip() for l in path.read_text(encoding='utf-8').split('\n') if l.startswith('#')]

def main(argv):
    targets = [pathlib.Path(a) for a in argv] or [ROOT / d for d in ('plugin', 'docs', 'bibles', 'drafts', 'tests')] + [ROOT / 'BACKLOG.md']
    files = []
    for t in targets:
        files += [t] if t.is_file() else sorted(t.rglob('*.md'))
    # папки с файлом ARCHIVED.md — архив прежних версий меток, их не проверяем
    files = [f for f in files if not (f.parent / 'ARCHIVED.md').exists()]
    owner = (ROOT / 'decisions' / 'OWNER.md').read_text(encoding='utf-8')
    esc = (ROOT / 'decisions' / 'ESCALATIONS.md').read_text(encoding='utf-8')
    readme_h = headings(ROOT / 'docs' / 'project-readme.md') or []
    cache, bad, count = {}, [], 0
    for f in files:
        text = f.read_text(encoding='utf-8')
        rel = f.relative_to(ROOT) if f.is_absolute() and ROOT in f.parents else f
        for m in re.finditer(r'\[canon:([^\]#]+)#([^\]]+)\]', text):
            count += 1
            name, head = m.group(1).strip(), m.group(2).strip()
            if '<' in name or '…' in head or '<' in head:
                continue  # образец записи метки, а не метка
            hs = cache.setdefault(name, headings(ROOT / 'canon' / name))
            if hs is None or not any(h.startswith(head) for h in hs):
                bad.append((rel, m.group(0)))
        for m in re.finditer(r'\[readme:([^\]]+)\]', text):
            count += 1
            head = m.group(1).strip()
            if '<' in head or '…' in head:
                continue
            if not any(h.startswith(head) for h in readme_h):
                bad.append((rel, m.group(0)))
        # Любая метка, начинающаяся с «[владелец», должна иметь вид [владелец:О-<число>]
        # или [владелец:E-<число>]. Буквы О/O и E/Е принимаются в обоих алфавитах.
        for m in re.finditer(r'\[владелец[^\]]*\]', text):
            tag = m.group(0)
            if '<' in tag or tag in ('[владелец:О-N]', '[владелец:E-N]', '[владелец:…]', '[владелец…]'):
                continue  # образец записи метки
            count += 1
            mm = re.fullmatch(r'\[владелец:([ОOEЕ])-(\d+)\]', tag)
            if not mm:
                bad.append((rel, 'метка владельца не по образцу: ' + tag))
                continue
            num = mm.group(2)
            if mm.group(1) in 'ОO':
                if not re.search(r'\|\s*[ОO]-' + num + r'\s*\|', owner):
                    bad.append((rel, tag + ' — записи нет в decisions/OWNER.md'))
            else:
                sec = re.search(r'###\s*[EЕ]-' + num + r'\b(.*?)(?=\n###\s|\Z)', esc, re.S)
                ans = sec and re.search(r'Ответ владельца:\*{0,2}[ \t]*(\S.*)', sec.group(1))
                if not sec:
                    bad.append((rel, tag + ' — вопроса нет в decisions/ESCALATIONS.md'))
                elif not ans:
                    bad.append((rel, tag + ' — у вопроса нет ответа владельца'))
        for m in re.finditer(r'\[canon:project-readme\.md#[^\]]+\]', text):
            bad.append((rel, 'старый вид метки: ' + m.group(0)))
    print(f'файлов: {len(files)}, меток проверено: {count}, не открылось: {len(bad)}')
    for rel, tag in bad:
        print(f'  {rel}: {tag}')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
