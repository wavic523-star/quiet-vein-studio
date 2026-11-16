# Чужие материалы

Всё, что взято из открытых репозиториев: текст ролей и шаблонов, код, инструменты. Одна запись на источник: репозиторий, коммит, файлы, лицензия, что взято и что изменено. Порядок работы — в навыке `oss-adapt`.

Правило: чужой текст адаптируется, а не копируется целиком; чужой код не исполняется до полного прочтения; уведомление о лицензии сохраняется.

## Источники текста ролей и навыков плагина (версия 0.1.0)

Общие условия для всех записей ниже. Дословного чужого текста в плагине нет: взяты структура и идеи, текст написан заново под канон проекта. Чужой код не исполнялся. Коммиты сняты с клонов 15–16 ноября 2026, лицензии прочитаны в файлах `LICENSE` клонов и в метаданных пакетов, а не на живых страницах репозиториев. Статус проверки записей: не проверено контролёром.

### Арт-дирекшен и двухмерная графика

Фрагмент для `third_party/NOTICE.md`. Дата: 2026-11-16. Из источников взяты структура и правила; дословно ничего не скопировано, текст переписан по-русски под канон проекта. Ни один чужой файл не исполнялся. Коммиты сняты командой `git -C <клон> rev-parse HEAD`, лицензии прочитаны в файлах `LICENSE` клонов на этих коммитах. Проверил: не проверено, ждёт контролёра. Одна строка — один источник.

| Репозиторий | Коммит | Файл | Лицензия | Что взято |
| --- | --- | --- | --- | --- |
| `Donchitos/Claude-Code-Game-Studios` | `abc0de79d6ceb0b5d7aa693945849b3937afbe6a` | `.claude/agents/art-director.md` | MIT | Круг обязанностей роли (арт-библия, сверка со стилем, цвет и свет, иерархия взгляда), список «чего роль не делает», шаблон имени файла `[category]_[name]_[variant]_[size].[ext]`. Убрано: память агента, протокол «May I write», запись в `production/` и `design/`, формат вердиктов ворот, делегирование другим агентам |
| `Donchitos/Claude-Code-Game-Studios` | `abc0de79d6ceb0b5d7aa693945849b3937afbe6a` | `.claude/skills/art-bible/SKILL.md` | MIT | Девять разделов арт-библии и состав каждого; «разделы 1–4 задают язык, остальные из них следуют»; два отдельных взгляда на интерфейс с выносом конфликта, а не тихим решением; требования к ориентирам; «библия — документ ограничений». Убрано: фазы с `AskUserQuestion`, вызов `yaml-helper.sh`, режимы `workflow` и `review`, пути `design/`, запуск агентов |
| `Donchitos/Claude-Code-Game-Studios` | `abc0de79d6ceb0b5d7aa693945849b3937afbe6a` | `.claude/docs/director-gates/ad-art-bible.md` | MIT | Шесть вопросов приёмки арт-библии (самопроверка в шаблоне). Вердикт у нас выносит контролёр по `canon-guard`, а не арт-директор |
| `AlterLab-IEU/AlterLab_GameForge` | `aff1a3a58613a2b78d4b7a5224f29c86414aff85` | `skills/agents/game-art-director/SKILL.md` | MIT | Правила: силуэт раньше детали; цвет не несёт смысл в одиночку; чёрный силуэт на дистанции игровой камеры; тон по серому кадру настоящей игры; согласованность важнее одного объекта; ограничение как стиль; библия действует до письменной правки; значки как один язык; ориентиры не из чужих игр. Убрано: персона, файлы «непрерывности», таблица ИИ-инструментов и их лицензий, разделы о движках, MCP (Blender, Figma), `WebFetch`, права на запись |
| `AlterLab-IEU/AlterLab_GameForge` | `aff1a3a58613a2b78d4b7a5224f29c86414aff85` | `skills/agents/game-ux-designer/SKILL.md` | MIT | Одно правило-опора: цель касания не меньше 48 dp. В шаблоне стоит как справка, не как число проекта |
| `Roblox/creator-docs` | `5a56d0d361d709aa785585b738354134ae47b4ae` | `content/en-us/production/publishing/experience-icons.md`, `content/en-us/production/publishing/thumbnails.md`, `content/en-us/cloud/guides/experience-icons-and-thumbnails.md`, `content/en-us/cloud/guides/usage-assets.md`, `content/en-us/projects/assets/index.md`, `content/en-us/effects/particle-emitters.md`, `content/en-us/studio/mcp.md`, `content/en-us/reference/engine/classes/{ScreenGui,Light,Lighting,Atmosphere}.yaml`, `content/en-us/reference/engine/enums/Material.yaml` | CC-BY-4.0 (текст документации) | Только факты: размеры и форматы иконки и обложек, правила модерации, свойства частиц, имена свойств и список `Enum.Material`. Текст не копировался; в файлах стоят метки `[roblox:<URL>, 2026-11-16]` |

Пакеты, на которые опираются сниппеты `graphics-2d.md`. Они не скопированы в репозиторий и ставятся в сессии; лицензии прочитаны в метаданных установленных пакетов 2026-11-16:

| Пакет | Версия при проверке | Лицензия | Зачем |
| --- | --- | --- | --- |
| Pillow | 12.3.0 в сессии | MIT-CMU | Сборка PNG, превью, обложки |
| coloraide | 8.15 | MIT | Расстояние между цветами `dE2000` |
| CairoSVG | 2.9.1 | LGPL-3.0-or-later | Запасной путь SVG → PNG; только инструмент песочницы, в игру не попадает |
| `rsvg-convert` (librsvg) | 2.58.0, системная программа | не проверено | Основной путь SVG → PNG |

### Окружение, облики и эффекты

Источники навыков `environment-spec`, `skins-vfx` и агентов `environment-designer`, `skins-vfx-designer` (версия 0.1.0). Дословно не скопировано ничего: взяты структура и идеи, текст написан заново. Чужой код не исполнялся. Коммиты сняты командой `git -C <клон> rev-parse HEAD`.

| Репозиторий | Коммит | Файл | Лицензия | Что взято | Что убрано |
| --- | --- | --- | --- | --- | --- |
| Donchitos/Claude-Code-Game-Studios | abc0de79d6ceb0b5d7aa693945849b3937afbe6a | `.claude/agents/level-designer.md` | MIT | Состав документа уровня (раскладка, главный путь, сюжетные точки), требование отмечать ведущие элементы, запрет роли строить в движке и решать сюжет | Протокол вопросов и разрешений на запись, файл состояния сессии, память агента, столкновения с врагами, графики темпа и сложности |
| Donchitos/Claude-Code-Game-Studios | abc0de79d6ceb0b5d7aa693945849b3937afbe6a | `.claude/agents/world-builder.md` | MIT | Уровень канона и видимость игроку у каждой записи; порядок при противоречии: назвать обе версии, указать закреплённую, дать варианты | Фракции, хронология, культуры, запись «истины» за каждой загадкой (противоречит воротам G1), память агента, разрешения на запись |
| Donchitos/Claude-Code-Game-Studios | abc0de79d6ceb0b5d7aa693945849b3937afbe6a | `.claude/agents/technical-artist.md` | MIT | У каждого эффекта свой бюджет; числа бюджета берутся из проекта, а не подставляются; перечень сокращений частиц; роль не принимает решений о стиле | Шейдеры, уровни детализации, пайплайн ассетов, сверка версии движка, инструмент Bash, порядок написания кода |
| msitarzewski/agency-agents | 8ae6164602c95ca78828b148b9052460ee426885 | `game-development/level-designer.md` | MIT | Структура Blockout Specification (габариты, назначение, счётный список объектов с местом, свет с назначением, видимость входа и выхода); три пункта Navigation Affordance Checklist, включая «выход виден за 3 секунды» | Таблицы боёв и врагов, график темпа, «личность» и память агента, разделы про процедурные уровни, спидран и соревновательные карты |
| msitarzewski/agency-agents | 8ae6164602c95ca78828b148b9052460ee426885 | `game-development/technical-artist.md` | MIT | Структура VFX Performance Audit Checklist (худший случай по частицам, слои наложения); примерные мобильные потолки 500 частиц и 3 слоя — приведены с пометкой «не замер Roblox» | Шейдер HLSL, цепочки LOD, сжатие текстур, скрипт Python, всё про Unity, Unreal и Godot, трассировка лучей, постобработка |
| adnvli/vfxskill | f17b9a60a4ac5af06dfaaff211eed8a379864351 | `SKILL.md` | MIT | Принцип «эффект — это показ, результат игры его не ждёт» | Модули `Emit`, `Build`, `Capture`, шаблоны, скрипты Node и Blender, загрузки через Open Cloud, анимации |
| adnvli/vfxskill | f17b9a60a4ac5af06dfaaff211eed8a379864351 | `references/vfx-craft.md` | MIT | Проверка эффекта снимками в нескольких моментах с камеры игрока, включая миг после конца; мысль, что эмиттер стоит вызова отрисовки, а перекрытие дороже числа | Рецепты слоёв боевых ударов, числа яркости и вспышек, инструкции по модулю и захвату кадров |
| Fraktality/spr | 665be1721c2a85e5cdfd9d44888d85dfc920626a | `spr.lua`, `README.md` | MIT | Ничего не скопировано: описаны назначение, вызовы `spr.target`, `spr.stop`, `spr.completed` и размер файла как модуля, который можно предложить | — |
| Sleitnick/RbxUtil | 31f9120fca021e3dec275b42bc7047d626962082 | `modules/shake/init.luau`, `modules/shake/wally.toml` | MIT | Ничего не скопировано: описаны назначение, поля тряски и отсутствие зависимостей | — |
| Pyseph/ObjectCache | 5775fc7a9272ab52a32e363789bd36e1dfa750ed | `src/init.luau`, `README.md` | MIT | Ничего не скопировано: описаны назначение и вызовы `new`, `GetPart`, `ReturnPart` | — |
| Roblox/creator-docs | 5a56d0d361d709aa785585b738354134ae47b4ae | `content/en-us/effects/particle-emitters.md`, `beams.md`, `trails.md`, `highlighting.md`, `light-sources.md`; `content/en-us/performance-optimization/improve.md`; `content/en-us/studio/mcp.md`; `content/en-us/reference/engine/classes/ParticleEmitter.yaml`, `PointLight.yaml`, `Trail.yaml`; `content/en-us/reference/engine/enums/Material.yaml`, `PartType.yaml` | CC BY 4.0 (текст), MIT (примеры кода) | Факты о движке своими словами, каждый с меткой `[roblox:<URL>, 2026-11-16]`; текст и код не копировались | — |

### Звук и музыка

Источники навыка `audio-design`, агента `audio-designer` и скриптов `tools/audio/` (версия 0.1.0). Дата: 2026-11-16. Из текстовых источников взяты структура и правила; дословно ничего не скопировано, текст написан заново по-русски под канон проекта. Клонированные репозитории не исполнялись. Коммиты сняты командой `git -C <клон> log -1`; лицензии прочитаны в файле `LICENSE` каждого клона и в установленных пакетах. Одна строка — один источник.

#### Текст ролей, шаблонов и правил

| Репозиторий | Коммит | Файл | Лицензия | Что взято | Что убрано |
| --- | --- | --- | --- | --- | --- |
| `Donchitos/Claude-Code-Game-Studios` | `abc0de79d6ceb0b5d7aa693945849b3937afbe6a` | `.claude/docs/templates/sound-bible.md` | MIT | Порядок разделов звуковой библии: опоры звука, музыка, эффекты, сведение по группам, запреты → `plugin/skills/audio-design/references/sound-bible-template.md` | Боевые состояния музыки, уровни в dBFS и LUFS, бюджеты памяти, диалоги, схема имён файлов |
| `Donchitos/Claude-Code-Game-Studios` | `abc0de79d6ceb0b5d7aa693945849b3937afbe6a` | `.claude/agents/audio-director.md` | MIT | Круг обязанностей: звуковая палитра, музыка по состояниям игры, порядок слышимости («важный для игры звук слышен всегда»); граница «роль не создаёт игровой код» → `plugin/agents/audio-designer.md`, `SKILL.md` | Порядок «сначала вопросы пользователю», запись состояния сессии, память проекта, запрет Bash, делегирование другим ролям |
| `Donchitos/Claude-Code-Game-Studios` | `abc0de79d6ceb0b5d7aa693945849b3937afbe6a` | `.claude/agents/sound-designer.md` | MIT | Состав строки звука (что запускает, длина, громкость, варианты); мысль о разбросе высоты против повторов → `references/cue-sheet.md`, шаблон библии | Кривые затухания по расстоянию, приоритеты и лимиты одновременных звуков, настройки звукового движка |
| `AlterLab-IEU/AlterLab_GameForge` | `aff1a3a58613a2b78d4b7a5224f29c86414aff85` | `skills/workflows/game-ai-assets/SKILL.md` | MIT | Правила: лицензия раньше качества; строка журнала в момент создания, а не выпуска; условия источника записываются с датой чтения; зерно и параметры каждого оставленного варианта; плохой вариант отбрасывается, а не чинится → лестница источников, строки манифеста, отчёты скриптов | Образ персонажа-ведущего, таблица платных генераторов, раскрытие ИИ для Steam и itch.io, обработка 3D и 2D |
| `AlterLab-IEU/AlterLab_GameForge` | `aff1a3a58613a2b78d4b7a5224f29c86414aff85` | `templates/ai-asset-log.md` | MIT | Ничего сверх схемы манифеста из `canon-guard`: файл прочитан для сверки полей | — |
| `Roblox/creator-docs` | `5a56d0d361d709aa785585b738354134ae47b4ae` | `content/en-us/audio/assets.md`, `content/en-us/cloud/guides/usage-assets.md`, `content/en-us/studio/mcp.md`, `content/en-us/studio/mcp-open-cloud.md`, `content/en-us/reference/engine/classes/Sound.yaml`, `content/en-us/reference/engine/classes/SoundGroup.yaml`, `content/en-us/production/publishing/account-verification.md` | CC BY 4.0 (текст), MIT (примеры кода) — по README репозитория | Факты о каталоге, загрузке, квотах, разрешениях и свойствах звука, пересказанные со ссылкой на страницу → `references/roblox-audio-rules.md` | Текст страниц не копировался |

#### Инструменты песочницы (`tools/audio/`)

Пакеты в репозиторий не скопированы: точные версии стоят в `tools/audio/package.json`, контрольные суммы — в `tools/audio/package-lock.json`. Установка только `npm ci --ignore-scripts`.

| Пакет (репозиторий) | Версия | Лицензия | Что взято |
| --- | --- | --- | --- |
| `jsfxr` (`chr15m/jsfxr`) | 1.4.1 | Unlicense | Зависимость `make_sfx.mjs`: пресеты и синтез эффекта |
| `midi-writer-js` (`grimmdude/MidiWriterJS`) | 3.2.1 | MIT | Зависимость `make_loop.mjs`: запись файла MIDI. В архиве пакета лежат чужие `postinstall.js`, `CLAUDE.md` и `.claude/settings.local.json`: не исполняются и правилами не считаются |
| `spessasynth_core` (`spessasus/spessasynth_core`) | 4.4.10 | Apache-2.0 | Зависимость `make_loop.mjs`: рендер MIDI через SoundFont. Цикл рендера написан по примеру «MIDI to wav converter» из README пакета |
| `@tonaljs/midi` | 4.10.5 | MIT | Попутная зависимость `midi-writer-js` |
| `@tonaljs/pitch` | 5.0.3 | MIT | Попутная зависимость `midi-writer-js` |
| `@tonaljs/pitch-note` | 6.1.2 | MIT | Попутная зависимость `midi-writer-js` |
| `fflate` | 0.8.3 | MIT | Попутная зависимость `spessasynth_core` |
| `stb-vorbis` (`spessasus/stb-vorbis`) | 0.0.7 | Apache-2.0 | Попутная зависимость `spessasynth_core`; объявлена как `latest`, закреплена файлом блокировки |
| `generaluser` (npm; банк GeneralUser GS 1.471) | 1.47.1 | Своя лицензия банка v2.0 (`LICENSE.txt` в пакете) | Только вход одного проверочного рендера во временной папке. В репозиторий не попал, в игру не идёт: автор банка не ручается за происхождение всех сэмплов |

Рассмотрено и не взято: `ZzFX` (`KilledByAPixel/ZzFX`, MIT) — та же задача, что у `jsfxr`.

#### Не проверено

- Тексты лицензий сверены в клонах и пакетах, а не на живых страницах репозиториев.
- Лицензии SoundFont FluidR3 и MuseScore General известны по заметкам исследования 15–16 ноября 2026; сами файлы не скачивались.

### Адаптация открытого кода и сюжетные реестры

Источники, из которых взяты идеи для навыков `oss-adapt` и `story-registers` и ролей `toolsmith` и `lore-keeper`. Одна строка на взятый файл. Дословного текста не скопировано ни из одного источника: взяты идеи и структура, пересказанные под проект. Файлы источников в репозиторий студии не копировались, папок в `third_party/` для них нет.

Коммиты получены командой `git -C <клон> rev-parse HEAD` 15 ноября 2026; лицензия прочитана в файле `LICENSE` каждого клона на этом коммите. Проверил: не проверено (ждёт контролёра).

#### Взято

- `fcsouza/agent-skills` @ `282fd138852f49ccecbddad4cb25901c85d17a07` · `skills/quest-narrative-coherence/SKILL.md` · MIT в клоне, требует сверки (см. примечание) · порядок проверки квеста: прочитать мир, прочитать реестр, сверить, привязать к записанному, записать строку; остановка при конфликте → семь проверок новой сайд-истории в `story-registers/SKILL.md`
- `fcsouza/agent-skills` @ `282fd138852f49ccecbddad4cb25901c85d17a07` · `skills/quest-narrative-coherence/templates/quest-registry.md` · MIT в клоне, требует сверки · идея реестра «одна строка на квест», урезанная до колонок проекта → `story-registers/references/side-story-register.md`
- `fcsouza/agent-skills` @ `282fd138852f49ccecbddad4cb25901c85d17a07` · `skills/game-dev-commands/game-lore/SKILL.md` · MIT в клоне, требует сверки · приём «неизвестное поле остаётся явно неизвестным и уходит в открытые вопросы» → прочерки «канон молчит» и разделы пробелов в трёх реестрах
- `Donchitos/Claude-Code-Game-Studios` @ `abc0de79d6ceb0b5d7aa693945849b3937afbe6a` · `.claude/agents/world-builder.md` · MIT · при противоречии показать оба варианта и не выбирать молча; статус записи рядом с записью → правила `lore-keeper` и реестров. Указание хранить правду о каждой тайне отдельно не взято и перевёрнуто: ответы не фиксируются
- `Donchitos/Claude-Code-Game-Studios` @ `abc0de79d6ceb0b5d7aa693945849b3937afbe6a` · `.claude/docs/director-gates/nd-consistency.md` · MIT · три угла проверки готового текста: голос героя, противоречие записанным фактам, тон → проверки строк в `story-registers/SKILL.md`
- `msitarzewski/agency-agents` @ `8ae6164602c95ca78828b148b9052460ee426885` · `game-development/narrative-designer.md` · MIT · правило «лор необязателен для прохождения» как отдельная проверка строки → проверка 9 в `story-registers/SKILL.md`
- `AlterLab-IEU/AlterLab_GameForge` @ `aff1a3a58613a2b78d4b7a5224f29c86414aff85` · `skills/agents/game-narrative-director/references/dialogue-tooling.md` · MIT · список проверок сценария: уникальный устойчивый идентификатор строки, идентификатор не занимается повторно, нет недостижимых строк и тупиков, длина в пределах интерфейса → проверки 1 и 6 и проверка «нет тупика» в `story-registers/SKILL.md`
- `AlterLab-IEU/AlterLab_GameForge` @ `aff1a3a58613a2b78d4b7a5224f29c86414aff85` · `skills/workflows/game-ai-assets/SKILL.md` · MIT · принципы «лицензия раньше качества», «условия датируются», «нет записи — нет файла» → шаги 2 и 8 в `oss-adapt/SKILL.md`
- `AlterLab-IEU/AlterLab_GameForge` @ `aff1a3a58613a2b78d4b7a5224f29c86414aff85` · `templates/ai-asset-log.md` · MIT · поля «что изменено человеком» и «кто проверил»; строка не удаляется, а помечается снятой → `oss-adapt/references/source-record-template.md` и правила ведения реестров

#### Примечание о лицензии fcsouza/agent-skills

Лицензию нужно сверить на живой странице репозитория до любого дословного заимствования (задача Е-4 в `BACKLOG.md`).

- В клоне на коммите `282fd13` файл `LICENSE` — MIT, Copyright (c) 2026 Fabricio Cavalcante.
- Чтение страницы `blob/main/LICENSE` 15 ноября 2026 тоже показало MIT.
- В заметках исследования записано, что страница репозитория на GitHub показывала GPL-3.0. Что показывает метка лицензии на главной странице, в этой сессии увидеть не удалось: `api.github.com` из песочницы закрыт, а текст страницы файла метки не содержит.
- Пока расхождение не снято: из этого источника берутся только идеи и структура, дословного текста нет. Так сделано во всех трёх строках выше.

#### Упомянуты как примеры, ничего не взято

Эти репозитории названы в `oss-adapt/SKILL.md` как примеры проблем с лицензией; меткам `[oss:…]` там соответствуют эти коммиты.

- `prooheckcp/RoQuest` @ `ab9fff87b846873d4ffef6d71384ff9b914546fc` · `LICENSE.txt`, `wally.toml`, `README.md`, `RoQuest/Vendor/` · файл лицензии Apache-2.0, README и `wally.toml` называют MIT · пример расхождения и пример копий уже установленных библиотек
- `DialogueMaker/plugin` @ `fddef54de35634d136c552cab78912619542fa82` · `LICENSE`, `README.md` · файл MPL-2.0, README говорит о GPL-3.0 · пример расхождения
- `DialogueMaker/client` @ `1caf98eb1b750bc37d55a3e5dbc8af92cc2c2f70` · `LICENSE`, `pesde.toml` · GPL-3.0 · пример запрещённой лицензии и зависимости от pesde
- `TemporaryLooker22/Stud-UI-Clean-Roblox` @ `7ae67f3f4cf4bd55a597d8f58d81feebb1be7dee` · `SKILL.md` · MIT · пример набора, по собственному описанию извлечённого из выпущенной игры
- `imafreakandyalldontknowit67/steal-a-template` @ `9088ddec03d0c9ae6f55fd2953e8b7e971119413` · `packs/systems/dialogue-system/CREDITS.md` · MIT · пример пакета, где автор исходника не установлен
- `Donchitos/Claude-Code-Game-Studios` @ `abc0de79d6ceb0b5d7aa693945849b3937afbe6a` · `.claude/rules/narrative.md` · MIT · пример правила, которое проекту противоречит (записывать «истинный ответ» тайны)

## Навыки сюжета (версия 0.3.0, 16 ноября 2026)

Только идеи и структура, без дословного текста. Опора — отчёт «Скиллы GitHub для сюжета и графики»; файлы в этой сессии не открывались.

- `Donchitos/Claude-Code-Game-Studios` @ `abc0de79d6ceb0b5d7aa693945849b3937afbe6a` · `.claude/agents/world-builder.md`, `.claude/agents/live-ops-designer.md`, `.claude/docs/director-gates/nd-consistency.md` · MIT · идея: разделение «решает — пишет — сторожит канон», календарь и тема сезона (без пропусков и валюты), проверка голоса и противоречий. В навыке `story-arc`. Требование «истинного ответа» перевёрнуто.
- `msitarzewski/agency-agents` @ `8ae6164602c95ca78828b148b9052460ee426885` · `game-development/narrative-designer.md` · MIT · идея: опоры голоса героя с полем «чего никогда не скажет», «лор необязателен». В навыке `story-arc`.
- `fcsouza/agent-skills` @ `282fd138852f49ccecbddad4cb25901c85d17a07` · `skills/quest-narrative-coherence/SKILL.md` · MIT в клоне, требует сверки · идея: остановка при конфликте квеста. В навыке `quest-event-design`.
- `AlterLab-IEU/AlterLab_GameForge` @ `aff1a3a58613a2b78d4b7a5224f29c86414aff85` · `skills/workflows/game-ai-assets/SKILL.md` · MIT · идея: журнал происхождения наград. В навыке `quest-event-design`.

## Команда сюжета (версия 0.4.0, 16 ноября 2026)

Только идеи и структура, без дословного текста; чужие файлы в репозиторий не копировались и не исполнялись. Клоны читались как недоверенные данные; хуки, настройки и исполняемые файлы из них не брались. Коммиты и лицензии сняты с клонов 16 ноября 2026 (короткие хеши; лицензия — файл `LICENSE` клона). Проверил: не проверено контролёром.

- `AlterLab-IEU/AlterLab_GameForge` @ `aff1a3a` · `templates/character-sheet.md`, `skills/agents/game-narrative-director/` · MIT · идея: лист героя с полями голоса, желания и связей; устойчивый идентификатор и статус строки. В `story-arc/references/hero-sheet.md`, `game-writing/SKILL.md`. Убрано: бои, характеристики, ветвящиеся диалоги, инструменты ИИ.
- `fcsouza/agent-skills` @ `282fd13` · шаблон листа персонажа и навык построения мира · MIT в клоне, требует сверки (Е-4) · идея: поле «что герой прячет» отдельно от «чего хочет». В `hero-sheet.md`. Моды с хуками не взяты.
- `msitarzewski/agency-agents` @ `8ae6164` · `game-development/narrative-designer.md` · MIT · идея: «чего герой никогда не скажет». В таблице голосов `game-writing`.
- `lvtd-llc/skills` @ `a3ad087` · навык о сюжете, мире и героях игры · MIT · прочитан для сверки полей листа героя; отдельно ничего не взято.
- `Donchitos/Claude-Code-Game-Studios` @ `abc0de7` · состав ролей студии · MIT · прочитан как пример варианта «комната сценаристов» (`docs/TEAM-DESIGN.md`, раздел 3); хуки и `settings.json` набора не взяты.
- `jwynia/agent-skills` @ `e02ec7e` · файла лицензии в клоне нет · ничего не взято.
- `MengTo/Skills` @ `3cc9345` · MIT · сюжетных игровых навыков нет; ничего не взято.

Статьи и доклады (идеи, со ссылкой в `docs/TEAM-DESIGN.md`, раздел 2): три бита мини-истории события и «крошки» лора — доклад King на GDC 2021 в пересказе Game Developer; таблица строк с идентификаторами и статусами — статья Ian Thomas «A Dialogue Pipeline»; документация Claude Code о субагентах и кэше — факты о полях агента и времени жизни кэша.

