# 2D-графика кодом

Значки интерфейса, иконку игры, спрайты частиц, константы палитры и обложки студия делает скриптами в песочнице сессии. Причин три. Картинка пересобирается одной командой из исходника, значит её можно проверить и поправить, не рисуя заново. Цвет берётся из палитры числом, а не на глаз. У своей картинки нет чужой лицензии: в манифесте это строка `generated-by-code`. Генераторы картинок и готовые наборы интерфейса не используются: первые из сессии недоступны и платные (отчёт «Скиллы GitHub для сюжета и графики», 16 ноября 2026), вторые часто собраны из чужих игр (ворота G5).

Метки источников, ворота и схема манифеста — в `docs/CONVENTIONS.md` и `plugin/skills/canon-guard/`. Здесь только то, чего там нет.

Факты о Roblox сверены 2026-11-16 по клону `Roblox/creator-docs`, коммит `5a56d0d`: файл клона `content/en-us/<путь>.md` — это страница `https://create.roblox.com/docs/<путь>`.

## Сначала вопрос: нужна ли картинка

Плашка, кнопка и рамка собираются без единого файла: `Frame`, `UICorner`, `UIStroke`, текст. Такой элемент не загружают и не модерируют, а цвет у него меняется одной константой. Картинка нужна там, где форму не собрать из прямоугольников: значок предмета, спрайт частицы, иконка игры, обложка.

| Что | Чем | Результат |
| --- | --- | --- |
| Константы палитры, расстояние между цветами | `coloraide` | `Palette.luau` с метками источников и строками `dE2000` |
| Значки интерфейса, иконка игры | свой SVG → `rsvg-convert` или CairoSVG → Pillow | PNG, превью 150×150, серый вариант, силуэт |
| Спрайты частиц | Pillow | белые PNG с альфой |
| Обложки, вариант иконки из кадра | Pillow поверх настоящего снимка из Studio | PNG 1920×1080 или 512×512 |
| Читаемость кадра | Pillow | кадр в размере телефона, цветной и серый |

## Среда

```bash
python3 -c "import PIL; print(PIL.__version__)"; which rsvg-convert
python3 -c "import coloraide, cairosvg" || pip install coloraide cairosvg
```

Проверено прямым запуском 2026-11-16: в сессии уже стояли Pillow 12.3.0 (MIT-CMU) и `rsvg-convert` 2.58.0; `coloraide` 8.15 (MIT) и CairoSVG 2.9.1 (LGPL-3.0-or-later) поставились через `pip`. Все пять скриптов ниже отработали на этих версиях. CairoSVG — запасной путь и только инструмент песочницы: в игру его код не попадает, основной путь — `rsvg-convert`.

Других пакетов не ставить. Каждый новый пакет — чужой код, а чужой код проходит через инструментальщика и навык `oss-adapt`. Сеть скриптам не нужна.

## Где лежат скрипты и результат

Скрипты студии живут в `tools/`, ведёт их инструментальщик. Роль арт-директора запускает только то, что там лежит. Для графики предлагается папка `tools/art/` по образцу `tools/audio/` (задача Е-3 в `BACKLOG.md`); тексты ниже — проверенные эталоны для неё. Пока нужного файла в `tools/art/` нет, роль кладёт исходники и текст скрипта в свою папку `out`, картинку не собирает и пишет об этом в «Открытые вопросы». Так в репозитории не появляется код, которого никто не принимал.

Результат идёт только в папку роли:

```
drafts/<шаг>/out/art-director/
  src/       исходники: *.svg, palette.json, shots.md (список кадров)
  check/     превью 150×150, серые варианты, силуэты, кадры в размере телефона
  Palette.luau
  icon_<имя>_v<N>_<размер>.png
  particle_<имя>_<размер>.png
  thumb_<имя>_v<N>_1920x1080.png
```

- Имя файла: `<вид>_<имя>_<вариант>_<размер>.<расширение>`, строчными буквами. `[oss:Donchitos/Claude-Code-Game-Studios@abc0de7:.claude/agents/art-director.md, MIT]` По имени видно, что это и какого размера, без открытия файла.
- Исходник лежит рядом с PNG. Картинку без исходника нельзя пересобрать, значит нельзя ни проверить, ни поправить.
- На каждую картинку — строка манифеста по `plugin/skills/canon-guard/references/manifest-schema.md`: `kind: image`, `source_type: generated-by-code`, в `source` скрипт и исходник, `status: кандидат`.
- Файл тяжелее 2 МБ назови в ответе дирижёру: по `CLAUDE.md` репозитория такой файл не коммитят без решения владельца. Тяжёлую обложку сохраняй в `.jpg`.

## Правила Roblox

| Что | Правило | Источник |
| --- | --- | --- |
| Иконка игры | Квадрат, не меньше 512×512; шаблон 512×512 | [roblox:https://create.roblox.com/docs/production/publishing/experience-icons, 2026-11-16] |
| Иконка игры | В списках уменьшается до размеров вроде 150×150, поэтому мелкое превью проверяется до сдачи | [roblox:https://create.roblox.com/docs/production/publishing/experience-icons, 2026-11-16] |
| Иконка игры | Одна на локаль; до показа проходит модерацию | [roblox:https://create.roblox.com/docs/production/publishing/experience-icons, 2026-11-16] |
| Иконка игры | Неквадратный файл при загрузке через Open Cloud отклоняется | [roblox:https://create.roblox.com/docs/cloud/guides/experience-icons-and-thumbnails, 2026-11-16] |
| Обложка | 16:9, желательно 1920×1080; `.jpg`, `.gif`, `.png`, `.tga`, `.bmp` | [roblox:https://create.roblox.com/docs/production/publishing/thumbnails, 2026-11-16] |
| Обложка | Другое соотношение сторон на странице растягивается до 16:9 | [roblox:https://create.roblox.com/docs/production/publishing/thumbnails, 2026-11-16] |
| Обложка | На странице игры до 10 изображений и видео; изображения бесплатны; всё проходит модерацию | [roblox:https://create.roblox.com/docs/production/publishing/thumbnails, 2026-11-16] |
| Обложка | Важное не ставится у нижнего края: его может закрыть счётчик игроков | [roblox:https://create.roblox.com/docs/production/publishing/thumbnails, 2026-11-16] |
| Обложка для главной | Файл до 3 МБ и 1920×1080; подбор обложки под игрока начинается с двух активных, активными делают 2–5 | [roblox:https://create.roblox.com/docs/production/publishing/thumbnails, 2026-11-16] |
| Видео-обложка | Только настоящий игровой процесс. Допустимы лёгкая цветокоррекция и логотип игры. Не допускаются механики и интерфейс, которых в игре нет, посторонние кадры, реклама и обещания вроде «50% off» | [roblox:https://create.roblox.com/docs/production/publishing/thumbnails, 2026-11-16] |
| Спрайт частиц | PNG с прозрачным фоном; серой текстуре без альфы помогает `LightEmission = 1`; цвет задаёт `ParticleEmitter.Color` | [roblox:https://create.roblox.com/docs/effects/particle-emitters, 2026-11-16] |
| Частицы | Один источник выпускает до 400 частиц в секунду, на телефоне до 100; крупные и перекрывающиеся частицы обходятся дороже | [roblox:https://create.roblox.com/docs/effects/particle-emitters, 2026-11-16] |
| Любое изображение | При загрузке через Open Cloud: `.png`, `.jpeg`, `.bmp`, `.tga`, меньше 8000×8000 | [roblox:https://create.roblox.com/docs/cloud/guides/usage-assets, 2026-11-16] |
| Любое изображение | Пока модерация не пройдена, игроки его не видят; обычно она занимает несколько часов | [roblox:https://create.roblox.com/docs/projects/assets, 2026-11-16] |

## Палитра

Палитра — один файл `src/palette.json`. Из него скрипт печатает модуль Luau и считает, насколько каждый цвет далёк от зарезервированного бирюзового.

```json
{
  "reserved": "DeepTeal",
  "min_de": 20,
  "colors": {
    "DeepTeal":   {"rgb": [0, 200, 180],  "source": "[canon:lore-bible.md#ТЗ окружения для команды разработки]"},
    "GuideAmber": {"rgb": [255, 190, 80], "source": "[canon:work-plans.md#Шаг 6: первая минута]"}
  }
}
```

```python
#!/usr/bin/env python3
"""palette.py — палитра из JSON -> константы Luau и расстояние dE2000 до зарезервированного цвета.

Читает один JSON. Печатает в stdout. Файлов не пишет, сеть не нужна.
Запуск: python3 palette.py <palette.json> > <папка out>/Palette.luau
"""
import json
import sys

from coloraide import Color

spec = json.load(open(sys.argv[1], encoding="utf-8"))
colors, reserved, min_de = spec["colors"], spec["reserved"], float(spec["min_de"])


def col(rgb):
    return Color("srgb", [v / 255 for v in rgb])


untagged = [n for n, c in colors.items() if not str(c.get("source", "")).startswith("[")]
if untagged:
    sys.exit(f"нет метки источника: {', '.join(untagged)}")  # цвет без метки в палитру не попадает

print("-- Сгенерировано из palette.json. Руками не править.")
print("return {")
for name, c in colors.items():
    r, g, b = c["rgb"]
    print(f"\t{name} = Color3.fromRGB({r}, {g}, {b}), -- {c['source']}")
print("}")
for name, c in colors.items():
    if name == reserved:
        continue
    de = col(c["rgb"]).delta_e(col(colors[reserved]["rgb"]), method="2000")
    print(f"-- dE2000 {name} / {reserved}: {de:.1f} {'ok' if de >= min_de else 'СЛИШКОМ БЛИЗКО'}")
```

```bash
python3 tools/art/palette.py drafts/<шаг>/out/art-director/src/palette.json > drafts/<шаг>/out/art-director/Palette.luau
```

Вывод на двух цветах канона (запуск 2026-11-16):

```
return {
	DeepTeal = Color3.fromRGB(0, 200, 180), -- [canon:lore-bible.md#ТЗ окружения для команды разработки]
	GuideAmber = Color3.fromRGB(255, 190, 80), -- [canon:work-plans.md#Шаг 6: первая минута]
}
-- dE2000 GuideAmber / DeepTeal: 42.4 ok
```

- Цвет без метки источника скрипт не принимает и останавливается. Это то же правило «число без метки не принимается», только исполняемое.
- `min_de: 20` — `[предложено]`. Порог утверждает владелец вместе с арт-библией; до этого строка «СЛИШКОМ БЛИЗКО» означает «покажи владельцу», а не «запрещено».
- Объектам Echo и знаку the Deep нужен сам `DeepTeal`, а не похожий оттенок. Похожий оттенок размывает правило «бирюзовое — чужое». `[canon:lore-bible.md#Облик героев]`
- Расстояние — число для решения, а не решение. Близость цвета Crystal к бирюзовому записана как противоречие и ждёт владельца `[readme:9. Открытые вопросы и противоречия]`. Значения цвета Crystal в снимке канона нет: попроси у дирижёра вывод из Studio, посчитай расстояние и принеси число с вариантами. Сам цвет Crystal роль не меняет.
- Разовый расчёт без файла:

```bash
python3 -c "from coloraide import Color as C; print(round(C('srgb',[0/255,200/255,180/255]).delta_e(C('srgb',[255/255,190/255,80/255]), method='2000'), 1))"
```

- `Palette.luau` — черновик. В игру он попадёт только после статуса «принято владельцем», руками исполнителя.

## Значки и иконка игры

- Значки говорят на одном языке: одна сетка, одна толщина линии, одна степень упрощения. `[oss:AlterLab-IEU/AlterLab_GameForge@aff1a3a:skills/agents/game-art-director/SKILL.md, MIT]` Значок, нарисованный иначе, рядом с остальными выглядит чужим.
- Рисуй то, что в игре есть: кирку, рюкзак, руду, яйцо, страницу журнала. Картинка должна показывать, чего ждать в игре. `[roblox:https://create.roblox.com/docs/production/publishing/experience-icons, 2026-11-16]`
- Цвета берутся константами из `Palette.luau`. Бирюзовый — только на значках Echo и знака the Deep. `[canon:lore-bible.md#Облик героев]`
- Смысл не держится на одном цвете: у каждого значка своя форма. `[oss:AlterLab-IEU/AlterLab_GameForge@aff1a3a:skills/agents/game-art-director/SKILL.md, MIT]`
- SVG рисуется в квадратном `viewBox`, без внешних файлов и ссылок.
- Чужой набор значков берётся только через инструментальщика и строку манифеста. Пока его нет в `third_party/`, значки свои.
- Иконка игры: план просит три варианта для сравнения `[canon:stages.md#Этап 3: полировка и подготовка к публикации, 28 ноября – 4 декабря]`. Вариант из кадра собирает `thumb.py` с размером `512 512`, вариант из своих SVG — `icon.py`. Выбирает владелец.

```python
#!/usr/bin/env python3
"""icon.py — SVG -> PNG заданного размера, превью 150x150, серый вариант и силуэт.

Читает один SVG. Пишет только в папку вывода. Сеть не нужна.
Запуск: python3 icon.py <icon.svg> <папка вывода> [размер, по умолчанию 512]
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image

svg, out = Path(sys.argv[1]), Path(sys.argv[2])
size = int(sys.argv[3]) if len(sys.argv) > 3 else 512
out.mkdir(parents=True, exist_ok=True)
png = out / f"{svg.stem}_{size}.png"
try:
    subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), str(svg), "-o", str(png)], check=True)
except (FileNotFoundError, subprocess.CalledProcessError):
    import cairosvg  # запасной путь, если rsvg-convert нет

    cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=size, output_height=size)

img = Image.open(png).convert("RGBA")
assert img.size == (size, size), f"нужен квадрат {size}x{size}, получено {img.size}"
img.resize((150, 150), Image.LANCZOS).save(out / f"{svg.stem}_150.png")  # так иконку видят в списках
img.convert("L").save(out / f"{svg.stem}_gray.png")  # читается ли без цвета
sil = Image.new("RGBA", img.size, (128, 128, 128, 255))  # всё непрозрачное — чёрным на сером
sil.paste(Image.new("RGBA", img.size, (0, 0, 0, 255)), (0, 0), img.getchannel("A"))
sil.save(out / f"{svg.stem}_silhouette.png")
print(png, img.size)
```

```bash
python3 tools/art/icon.py drafts/<шаг>/out/art-director/src/icon_journal.svg drafts/<шаг>/out/art-director/check 512
```

Открой `_150.png` и `_gray.png`. Значок не узнаётся — упрощай форму, а не добавляй деталь. `_silhouette.png` считается по альфа-каналу и нужен значкам с прозрачным фоном; у иконки игры фон непрозрачный, для неё смотри превью и серый вариант.

## Спрайты частиц

- Спрайт белый, с мягкой альфой. Цвет задаётся в `ParticleEmitter.Color`, поэтому один файл служит и янтарным искрам, и бирюзовым. `[roblox:https://create.roblox.com/docs/effects/particle-emitters, 2026-11-16]`
- Размер по умолчанию 128×128 — `[предложено]`: в прочитанных страницах Roblox размер текстуры частиц не задан.
- Спрайт не повод для нового эффекта. Эффекты разрешены у удара (уже есть), метеорита и вылупления `[readme:5. Визуальный и звуковой канон]`; бюджет каждого считает роль обликов и эффектов.

```python
#!/usr/bin/env python3
"""sprites.py — белые спрайты частиц с мягкой альфой: точка, кольцо, искра.

Ничего не читает. Пишет только в папку вывода. Сеть не нужна.
Запуск: python3 sprites.py <папка вывода> [размер, по умолчанию 128]
"""
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
S = int(sys.argv[2]) if len(sys.argv) > 2 else 128


def save(alpha, name):
    img = Image.new("RGBA", alpha.size, (255, 255, 255, 0))  # белый: цвет даёт ParticleEmitter.Color
    img.putalpha(alpha)
    img.save(out / f"particle_{name}_{S}.png")


dot = ImageChops.invert(Image.radial_gradient("L")).resize((S, S), Image.LANCZOS)
save(dot.point(lambda v: max(0, v * 2 - 255)), "dot")  # мягкая точка, прозрачная к краю

ring = Image.new("L", (S, S), 0)
ImageDraw.Draw(ring).ellipse([S * 0.18, S * 0.18, S * 0.82, S * 0.82], outline=255, width=max(2, S // 16))
save(ring.filter(ImageFilter.GaussianBlur(S / 64)), "ring")

spark = Image.new("L", (S, S), 0)  # четырёхлучевая искра из двух ромбов
d, c, w = ImageDraw.Draw(spark), S / 2, S * 0.07
d.polygon([(c, S * 0.04), (c + w, c), (c, S * 0.96), (c - w, c)], fill=255)
d.polygon([(S * 0.04, c), (c, c - w), (S * 0.96, c), (c, c + w)], fill=255)
save(spark.filter(ImageFilter.GaussianBlur(S / 96)), "spark")
print(sorted(p.name for p in out.glob("particle_*.png")))
```

```bash
python3 tools/art/sprites.py drafts/<шаг>/out/art-director 128
```

## Обложки: только поверх настоящих снимков

Обложка собирается из кадра, снятого в Studio. Сцену для обложки не рисуют и не собирают из примитивов в скрипте. Игрок должен увидеть в игре то же, что на обложке: Roblox просит показывать, чего ждать в игре, а для видео-обложек настоящий игровой процесс — условие приёма `[roblox:https://create.roblox.com/docs/production/publishing/thumbnails, 2026-11-16]`. Студия держит ту же планку для картинок.

- Снимки делает дирижёр: `screen_capture` принимает положение камеры и точку взгляда `[roblox:https://create.roblox.com/docs/studio/mcp, 2026-11-16]`. Он кладёт их в папку шага, путь называет бриф. У роли доступа к Studio нет.
- Роль заранее отдаёт список кадров в `src/shots.md`:

| Кадр | Что в кадре (`PoiId`) | Камера: откуда и куда, studs | Что должно быть видно | Для чего |
| --- | --- | --- | --- | --- |

- Что известно о съёмке: снимок Studio не захватывает подписи с `AlwaysOnTop` `[canon:work-plans.md#Шаг 6: первая минута]`; у записей тестеров водяной знак, поэтому кадры снимают в Studio `[canon:step-order-agents.md#Материалы для продвижения]`.
- На страницу игры план закладывает иконку и 3–5 скриншотов. `[canon:stages.md#Этап 3: полировка и подготовка к публикации, 28 ноября – 4 декабря]`
- Можно: обрезать кадр, слегка поднять контраст и насыщенность, поставить название игры в левом верхнем углу.
- Нельзя: дорисовывать героев, предметы, интерфейс и эффекты, которых нет в кадре; писать обещания, скидки, таймеры и «Free» (ворота G2); ставить ссылки и QR (G4), чужих персонажей и логотипы (G5), страшные лица (G4).
- Название игры — единственный текст на обложке. Шрифту названия нужна строка манифеста (`kind: font`); в каноне шрифт не выбран, до решения обложка собирается без логотипа (второй аргумент `-`).
- Нет снимка — нет обложки. Это открытый вопрос, а не повод собрать похожую сцену.

```python
#!/usr/bin/env python3
"""thumb.py — обложка поверх настоящего снимка из Studio. Сцену не рисует.

Читает снимок и, если дан, логотип PNG. Пишет один файл. Сеть не нужна.
Запуск: python3 thumb.py <снимок.png> <логотип.png или -> <выход.png> [ширина высота, по умолчанию 1920 1080]
"""
import sys

from PIL import Image, ImageEnhance, ImageOps

W, H = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (1920, 1080)
SAFE_BOTTOM = 0.80  # ниже этой доли высоты ничего важного: низ может закрыть счётчик игроков

shot = Image.open(sys.argv[1]).convert("RGB")
if shot.width < W or shot.height < H:
    print(f"ВНИМАНИЕ: снимок {shot.size} меньше {W}x{H}, картинка выйдет мягкой: нужен снимок крупнее")
thumb = ImageOps.fit(shot, (W, H), Image.LANCZOS, centering=(0.5, 0.5))  # обрезка без растяжения
thumb = ImageEnhance.Contrast(thumb).enhance(1.06)  # лёгкая правка; вид игры не меняется
thumb = ImageEnhance.Color(thumb).enhance(1.05)

if sys.argv[2] != "-":
    logo = Image.open(sys.argv[2]).convert("RGBA")
    logo.thumbnail((int(W * 0.34), int(H * 0.22)), Image.LANCZOS)
    x, y = int(W * 0.04), int(H * 0.06)  # левый верхний угол
    assert y + logo.height <= H * SAFE_BOTTOM, "логотип заходит в нижнюю полосу"
    thumb.paste(logo, (x, y), logo)

assert thumb.size == (W, H)
thumb.save(sys.argv[3], optimize=True)
print(sys.argv[3], thumb.size)
```

```bash
python3 tools/art/thumb.py <снимок из папки шага> - drafts/<шаг>/out/art-director/thumb_camp_v1_1920x1080.png
python3 tools/art/thumb.py <снимок из папки шага> - drafts/<шаг>/out/art-director/icon_camp_v1_512.png 512 512
```

Доля нижней полосы `SAFE_BOTTOM = 0.80` — `[предложено]`: Roblox говорит «не ставить важное внизу» и числа не даёт.

## Читаемость на телефоне и чёрный силуэт

Самый маленький экран в списке проверки — симулятор iPhone 7, 667×375. `[canon:work-plans.md#Огород, шаг 5]` Что не читается в этом размере, игрок с маленьким телефоном не увидит.

```python
#!/usr/bin/env python3
"""readability.py — как кадр читается на самом маленьком телефоне и без цвета.

Читает один снимок. Пишет два файла в папку вывода. Сеть не нужна.
Запуск: python3 readability.py <снимок.png> <папка вывода> [ширина телефона, по умолчанию 667]
"""
import sys
from pathlib import Path

from PIL import Image

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
phone_w = int(sys.argv[3]) if len(sys.argv) > 3 else 667
shot = Image.open(src).convert("RGB")
small = shot.resize((phone_w, round(shot.height * phone_w / shot.width)), Image.LANCZOS)
small.save(out / f"{src.stem}_phone.png")  # размер экрана телефона
small.convert("L").save(out / f"{src.stem}_phone_gray.png")  # только тон, без цвета
print(small.size)
```

```bash
python3 tools/art/readability.py <снимок из папки шага> drafts/<шаг>/out/art-director/check 667
```

Проверка силуэта идёт в два приёма:

1. **До постройки.** Нарисуй вид спереди по раскладке частей: SVG из прямоугольников в одном масштабе для всех сравниваемых объектов. `icon.py` даст чёрные силуэты; положи их рядом. Два силуэта совпали — меняй один из них формой, а не цветом.
2. **После постройки.** По настоящему кадру с дистанции игровой камеры: `readability.py` даёт размер телефона и серый вариант. Объект должен узнаваться в обоих.

Дистанция игровой камеры в каноне не записана. Её снимает дирижёр в Studio; до этого проверка «после постройки» остаётся в «Не проверено».

## Загрузка в Roblox — решение владельца

Роль не загружает картинки, не просит об этом инструменты и не пишет «загружено». Причины:

- Загрузка своих файлов в схеме манифеста стоит в списке «только по решению владельца», с согласием на каждую пачку. `plugin/skills/canon-guard/references/manifest-schema.md`
- Каждое загруженное изображение проходит модерацию Roblox. `[roblox:https://create.roblox.com/docs/projects/assets, 2026-11-16]`
- До запуска и в первые 30 дней проект не платит за загрузки, за которые Roblox просит Robux. `[canon:not-doing-later.md#Не делаем до запуска]`

Статус картинки в манифесте остаётся `кандидат`, пока владелец её не посмотрел. В ответе дирижёру перечисли, что нужно посмотреть, одним списком: так владелец решает один раз за шаг.

## Не проверено

- Размер кадра, который отдаёт `screen_capture`: от него зависит, выйдет ли обложка 1920×1080 резкой.
- Принимает ли `upload_image` что-то кроме адресов HTTP: документация называет только их. `[roblox:https://create.roblox.com/docs/studio/mcp, 2026-11-16]`
- Рекомендуемый Roblox размер текстуры частиц.
- Порог `dE2000` и доля нижней полосы: это предложения, а не замеры.
- Скрипты прошли на синтетических входах. Настоящий снимок Studio и настоящие значки через них ещё не проходили.
- Как значки и обложки смотрятся на настоящем телефоне: это видит только владелец.
