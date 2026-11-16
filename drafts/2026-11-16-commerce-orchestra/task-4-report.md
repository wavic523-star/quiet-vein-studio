# Отчёт задачи 4: правила в плагине и скрипты

Шаг: 2026-11-16-commerce-orchestra · Дата: 16 ноября 2026 · Исполнитель: агент задачи 4 · Статус: готово с оговорками

## Что сделано по файлам

| Файл | Что добавлено |
| --- | --- |
| `plugin/skills/orchestra/SKILL.md` | В «Кого звать» — пять строк: ориентиры рынка, календарь окна, каталог окна, набор продвижения, совместный шаг (маршруты из `design.md`, раздел 6). Абзац под таблицей: ссылка на `design.md` 4, 6, 7 и `docs/GUIDE.md`, условие вызова `market-analyst` (нет `РЫН-N` свежее 30 дней), `--preset commerce` и `--bible`, ссылка на уже описанный способ звать роль, которой нет в установленной версии, и на запасной путь |
| `plugin/skills/owner-proxy/SKILL.md` | Класс Б: заработанная косметика и её сюжетный повод; место награды в календаре в пределах дат и часов плана; слоты и тексты продвижения в рамках правил Roblox. Класс В: сводная таблица этапа с меткой `[владелец:О-34]` |
| `plugin/skills/owner-proxy/references/owner-positions.md` | Раздел «Коммерция»: О-28, О-29, О-30, О-32, О-34 дословными цитатами (каждая цитата сверена скриптом как подстрока `decisions/OWNER.md`) |
| `plugin/skills/game-writing/SKILL.md` | Абзац «Строки продвижения»: четыре ключа `promo.*`, тексты только по слотам стратега, пределы — константы `PROMO_LIMIT`, `PROMO_UNCONFIRMED` в `tools/lint_strings.py` |
| `plugin/agents/writer.md` | Правило о ключах `promo.*`, слотах стратега и пределах из скрипта |
| `tools/lint_strings.py` | В `KEY` — ветка `promo.<единица>.(tile.title\|tile.desc\|news\|notify)`; `kind()` даёт вид `promo`; `.news` > 60 и `.notify` > 99 — ошибка; `.tile.title`, `.tile.desc` — предупреждение «предел не подтверждён до метки [roblox:…]»; строки `promo` не входят в мерки канона; строка «пределы продвижения» печатается, только если в проверке есть ключи `promo`. Старые проверки и вывод не изменены |
| `tools/context_pack.py` | Пресет `commerce` из девяти разделов задачи 4; все девять находятся в снимке |
| `drafts/_template/story-brief.md` | Необязательный блок «Коммерция»: цель по метрике, белые пятна, вне шага, ориентиры `РЫН-N` |
| `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `plugin/README.md` | Версия 0.5.0; строка 0.5.0 в «Версиях» README |

## Решено самостоятельно

- Ключ `promo` строгий: единица — один сегмент `[a-z0-9]+`, хвост — только четыре вида из `design.md`, раздел 5. Иное — «ключ не по схеме».
- Пределы 60 и 99 сверены с отчётом `drafts/2026-11-16-offer-pool/reports/Сюжетная косметика и продвижение Roblox.md` («до 60 символов», «до 99 символов»).
- Позиции владельца: только записи, названные задачей (О-28, О-29, О-30, О-32, О-34); О-31 и О-33, которые упомянуты в `design.md`, раздел 8, не добавлены.

## Что не сделано

- `KEY_RE` в `tools/context_pack.py` (список занятых ключей) не знает `promo`: задачей не названо.
- Во вступлении `plugin/README.md` счёт «двенадцати ролей… тринадцать навыков» и таблица ролей не обновлены: задачей названа только версия. Поле `metadata.version` в навыках осталось 0.4.2.
- `plugin/skills/game-writing/SKILL.md` стал 11 160 байт (было 9 756): предел 10 КБ в плане задан для новых навыков.

## Вывод проверки

```
python3 -I tools/lint_strings.py drafts/2026-11-16-plan-asks      — совпадает с /tmp/ls_planasks_before.txt
файлов: 4, строк: 16, ошибок: 0, предупреждений: 0
мерки длины по канону: goal 30, journal 63, line 79, note 34, step 34
python3 -I tools/lint_strings.py drafts/2026-11-16-green-starfall — совпадает с /tmp/ls_starfall_before.txt
файлов: 4, строк: 3, ошибок: 0, предупреждений: 0
мерки длины по канону: goal 30, journal 63, line 79, note 34, step 34
```

Временная папка `/tmp/promo_test/` (удалена после проверки):

```
файлов: 1, строк: 7, ошибок: 3, предупреждений: 2
пределы продвижения: .news 60, .notify 99; не подтверждены: .tile.title, .tile.desc
  ОШИБКА promo.starfall.news: 68 знаков, предел .news — 60
  ОШИБКА promo.starfall.notify: 120 знаков, предел .notify — 99
  ОШИБКА promo.lantern.banner: ключ не по схеме
  внимание promo.lantern.tile.title: предел .tile.title не подтверждён до метки [roblox:…]
  внимание promo.lantern.tile.desc: предел .tile.desc не подтверждён до метки [roblox:…]
```
Короткие `promo.lantern.news` (22) и `.notify` (54) прошли. Граница: `.news` 60 проходит, 61 — ошибка; `.notify` 99 проходит, 100 — ошибка.

```
python3 -I tools/context_pack.py --help
  --preset {arc,commerce,event,hero,quest,writing}
python3 -I toolkit/tools/validate_repo.py — совпадает с /tmp/validate_before.txt
Итого: ошибок 0, предупреждений 0
python3 -I tools/lint_tags.py plugin — код 0
файлов: 56, меток проверено: 698, не открылось: 0
python3 -I tools/lint_tags.py drafts/_template/story-brief.md
файлов: 1, меток проверено: 1, не открылось: 0
```

Счёт `lint_tags plugin` включает файлы задач 1–2, которые писались параллельно.
