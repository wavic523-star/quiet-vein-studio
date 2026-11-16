#!/usr/bin/env node
// make_loop.mjs — короткая музыкальная петля из JSON-партитуры:
// партитура -> MIDI (midi-writer-js, MIT) -> рендер через SoundFont (spessasynth_core, Apache-2.0)
// -> WAV 16 бит стерео, по желанию OGG через ffmpeg.
//
// Читает: партитуру (--score, JSON), файл SoundFont (--soundfont) и свой package.json.
// Пишет: только в каталог --out (<id>.mid, <id>.wav, <id>.ogg, <id>.report.json). Сеть не нужна.
// Сам ничего не скачивает и не загружает в Roblox: путь к SoundFont даётся аргументом, без него
// пишется только MIDI. Внешний процесс один: ffmpeg, и только с флагом --ogg.
// Внутри репозитория --out принимается только вида drafts/<шаг>/out/...; вне репозитория — любая
// временная папка для пробного прогона.
// Результат — кандидат: его никто не слышал. Статус выше «кандидат» ставит только владелец.
//
//   node make_loop.mjs --out <каталог> --demo                       # только MIDI
//   node make_loop.mjs --out <каталог> --score <партитура.json> --soundfont <файл.sf2> [--ogg] [--peak 0.6]
//
// Партитура (at и dur в долях, от начала петли; program — номер General MIDI с нуля):
// { "id": "music.test.loop", "bpm": 80, "beatsPerBar": 4, "bars": 4,
//   "tracks": [ { "name": "lead", "program": 10, "volume": 100, "reverb": 40,
//                 "notes": [ { "at": 0, "dur": 1, "pitch": "E5", "vel": 70 },
//                            { "at": 1, "dur": 2, "pitch": ["C4", "G4"] } ] } ] }
//
// Шов петли: рендерится один проход и ещё TAIL_SECONDS тишины после него. Всё, что доиграло после
// конца петли (затухание нот, реверберация), складывается с её началом. Конец файла поэтому
// продолжается в его начале так же, как продолжался бы в отрендеренном хвосте.

import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { closeSync, existsSync, mkdirSync, openSync, readFileSync, readSync, statSync, writeFileSync } from "node:fs";
import { basename, dirname, isAbsolute, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import MidiWriter from "midi-writer-js";

const PPQ = 128; // тиков на долю в midi-writer-js
const ID_RE = /^[a-z0-9][a-z0-9._-]{0,63}$/;
const MAX_SECONDS = 120;
const TAIL_SECONDS = 8; // сколько доигрываем после конца петли, чтобы завернуть хвост в начало
// Проверочная фраза: гамма до мажор и два аккорда. Это тест конвейера, а не тема игры.
const DEMO = {
  id: "test.loop",
  bpm: 80,
  beatsPerBar: 4,
  bars: 4,
  tracks: [
    {
      name: "lead",
      program: 10,
      volume: 100,
      reverb: 40,
      notes: ["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6", "C6", "B5", "A5", "G5", "F5", "E5", "D5", "C5"].map((pitch, i) => ({ at: i, dur: 1, pitch, vel: 70 })),
    },
    {
      name: "pad",
      program: 89,
      volume: 70,
      reverb: 60,
      notes: [
        { at: 0, dur: 8, pitch: ["C3", "E3", "G3"], vel: 50 },
        { at: 8, dur: 8, pitch: ["F3", "A3", "C4"], vel: 50 },
      ],
    },
  ],
};

function fail(msg) {
  console.error("make_loop: " + msg);
  process.exit(1);
}

// Граница записи: в репозитории только drafts/<шаг>/out/..., остальное дерево закрыто.
function checkOutDir(outDir, here) {
  const rel = relative(resolve(here, "..", ".."), outDir);
  if (rel.startsWith("..") || isAbsolute(rel)) return; // вне репозитория: пробный прогон
  const parts = rel.split(sep);
  if (!(parts.length >= 3 && parts[0] === "drafts" && parts[2] === "out")) {
    throw new Error("--out внутри репозитория должен быть вида drafts/<шаг>/out/...; получено: " + (rel || "."));
  }
}

function parseArgs(argv) {
  const a = { ogg: false, demo: false, peak: 0.6, rate: 44100 };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    const next = () => argv[++i] ?? fail("после " + k + " нужно значение");
    if (k === "--out") a.out = next();
    else if (k === "--score") a.score = next();
    else if (k === "--soundfont") a.soundfont = next();
    else if (k === "--peak") a.peak = Number(next());
    else if (k === "--rate") a.rate = Number(next());
    else if (k === "--ogg") a.ogg = true;
    else if (k === "--demo") a.demo = true;
    else fail("неизвестный аргумент " + k);
  }
  return a;
}

const isInt = (v, lo, hi) => Number.isInteger(v) && v >= lo && v <= hi;

// Приводит партитуру к проверенному виду; всё сомнительное — ошибка или предупреждение, а не догадка.
function normalizeScore(raw) {
  const warnings = [];
  if (!raw || typeof raw !== "object") fail("партитура должна быть объектом JSON");
  if (!ID_RE.test(raw.id ?? "")) fail("плохой id партитуры: " + JSON.stringify(raw.id));
  if (!(raw.bpm >= 40 && raw.bpm <= 200)) fail("bpm от 40 до 200");
  const beatsPerBar = raw.beatsPerBar ?? 4;
  if (!isInt(beatsPerBar, 1, 12) || !isInt(raw.bars, 1, 64)) fail("beatsPerBar 1–12, bars 1–64 (целые)");
  const loopBeats = beatsPerBar * raw.bars;
  const loopSeconds = (loopBeats * 60) / raw.bpm;
  if (loopSeconds > MAX_SECONDS) fail(`петля ${loopSeconds.toFixed(1)} с длиннее ${MAX_SECONDS} с: инструмент рассчитан на короткие петли`);
  if (!Array.isArray(raw.tracks) || raw.tracks.length < 1 || raw.tracks.length > 8) fail("tracks: от 1 до 8 дорожек");
  const tracks = raw.tracks.map((t, ti) => {
    const channel = t.channel ?? (ti < 9 ? ti + 1 : ti + 2); // канал 10 оставлен ударным
    if (!isInt(channel, 1, 16)) fail(`дорожка ${ti}: channel 1–16`);
    if (!isInt(t.program ?? 0, 0, 127)) fail(`дорожка ${ti}: program 0–127`);
    for (const cc of ["volume", "pan", "reverb"]) if (t[cc] !== undefined && !isInt(t[cc], 0, 127)) fail(`дорожка ${ti}: ${cc} 0–127`);
    if (!Array.isArray(t.notes) || t.notes.length === 0) fail(`дорожка ${ti}: нет нот`);
    const notes = [];
    t.notes.forEach((n, ni) => {
      const where = `дорожка ${ti}, нота ${ni}`;
      if (!(n.at >= 0 && n.at < loopBeats)) fail(`${where}: at вне петли (0…${loopBeats})`);
      if (!(n.dur > 0)) fail(`${where}: dur должен быть больше 0`);
      let dur = n.dur;
      if (n.at + dur > loopBeats) {
        dur = loopBeats - n.at;
        warnings.push(`${where}: нота обрезана по концу петли`);
      }
      const vel = n.vel ?? 70;
      if (!isInt(vel, 1, 100)) fail(`${where}: vel 1–100`);
      const start = Math.round(n.at * PPQ);
      const end = Math.max(start + 1, Math.round((n.at + dur) * PPQ));
      for (const pitch of Array.isArray(n.pitch) ? n.pitch : [n.pitch]) {
        const ok = typeof pitch === "string" ? /^[A-Ga-g][#b]?-?\d$/.test(pitch) : isInt(pitch, 0, 127);
        if (!ok) fail(`${where}: pitch ${JSON.stringify(pitch)} (нужно вида "C#4" или число 0–127)`);
        notes.push({ start, end, pitch, vel });
      }
    });
    return { name: String(t.name ?? "track" + ti), channel, program: t.program ?? 0, volume: t.volume ?? 100, pan: t.pan, reverb: t.reverb, notes };
  });
  return { id: raw.id, bpm: raw.bpm, beatsPerBar, bars: raw.bars, loopBeats, loopSeconds, tracks, warnings };
}

// События пишутся по абсолютным тикам с собственным расчётом дельт: так время нот не зависит
// от порядка добавления.
function buildMidi(score) {
  const tracks = score.tracks.map((t, ti) => {
    const track = new MidiWriter.Track();
    if (ti === 0) {
      track.setTempo(score.bpm);
      track.setTimeSignature(score.beatsPerBar, 4);
    }
    track.addTrackName(t.name);
    // Внимание: у ProgramChangeEvent в midi-writer-js 3.2.1 канал считается с нуля, у остальных событий — с единицы.
    track.addEvent(new MidiWriter.ProgramChangeEvent({ instrument: t.program, channel: t.channel - 1 }));
    track.addEvent(new MidiWriter.ControllerChangeEvent({ controllerNumber: 7, controllerValue: t.volume, channel: t.channel }));
    if (t.pan !== undefined) track.addEvent(new MidiWriter.ControllerChangeEvent({ controllerNumber: 10, controllerValue: t.pan, channel: t.channel }));
    if (t.reverb !== undefined) track.addEvent(new MidiWriter.ControllerChangeEvent({ controllerNumber: 91, controllerValue: t.reverb, channel: t.channel }));
    const events = [];
    for (const n of t.notes) {
      events.push({ tick: n.start, on: 1, pitch: n.pitch, vel: n.vel });
      events.push({ tick: n.end, on: 0, pitch: n.pitch, vel: n.vel });
    }
    events.sort((a, b) => a.tick - b.tick || a.on - b.on); // на одном тике сначала снятия
    let cursor = 0;
    for (const e of events) {
      const delta = e.tick - cursor;
      cursor = e.tick;
      track.addEvent(
        e.on
          ? new MidiWriter.NoteOnEvent({ channel: t.channel, pitch: e.pitch, velocity: e.vel, wait: "T" + delta })
          : new MidiWriter.NoteOffEvent({ channel: t.channel, pitch: e.pitch, velocity: e.vel, delta }),
      );
    }
    return track;
  });
  return Buffer.from(new MidiWriter.Writer(tracks).buildFile());
}

function wav16(channels, rate) {
  const n = channels[0].length;
  const ch = channels.length;
  const buf = Buffer.alloc(44 + n * ch * 2);
  buf.write("RIFF", 0);
  buf.writeUInt32LE(36 + n * ch * 2, 4);
  buf.write("WAVEfmt ", 8);
  buf.writeUInt32LE(16, 16);
  buf.writeUInt16LE(1, 20);
  buf.writeUInt16LE(ch, 22);
  buf.writeUInt32LE(rate, 24);
  buf.writeUInt32LE(rate * ch * 2, 28);
  buf.writeUInt16LE(ch * 2, 32);
  buf.writeUInt16LE(16, 34);
  buf.write("data", 36);
  buf.writeUInt32LE(n * ch * 2, 40);
  let o = 44;
  for (let i = 0; i < n; i++) {
    for (let c = 0; c < ch; c++) {
      const v = Math.max(-1, Math.min(1, channels[c][i]));
      buf.writeInt16LE(Math.round(v * 32767), o);
      o += 2;
    }
  }
  return buf;
}

// Цикл рендера (processTick + process блоками по 128 сэмплов) — по примеру «MIDI to wav converter»
// из README spessasynth_core 4.4.10 (Apache-2.0).
async function renderLoop(score, midiBytes, soundfontPath, rate) {
  // Импорт здесь, чтобы режим «только MIDI» не грузил синтезатор.
  const { BasicMIDI, SoundBankLoader, SpessaSynthProcessor, SpessaSynthSequencer } = await import("spessasynth_core");
  const sf = readFileSync(soundfontPath);
  const toArrayBuffer = (b) => b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
  const midi = BasicMIDI.fromArrayBuffer(toArrayBuffer(midiBytes));
  const synth = new SpessaSynthProcessor(rate, { eventsEnabled: false });
  let bank;
  try {
    bank = SoundBankLoader.fromArrayBuffer(toArrayBuffer(sf));
  } catch (e) {
    fail("файл не читается как SoundFont (" + soundfontPath + "): " + e.message.split("\n")[0]);
  }
  synth.soundBankManager.addSoundBank(bank, "main");
  await synth.ready;
  synth.setSystemParameter("autoAllocateVoices", true);
  const seq = new SpessaSynthSequencer(synth);
  seq.skipToFirstNoteOn = false; // иначе пауза в начале партитуры пропадёт и петля станет короче
  seq.loopCount = 0;
  seq.loadNewSongList([midi]);
  seq.play();

  const loopSamples = Math.round(score.loopSeconds * rate);
  const total = loopSamples + Math.round(TAIL_SECONDS * rate);
  const rawL = new Float32Array(total);
  const rawR = new Float32Array(total);
  const started = performance.now();
  for (let filled = 0; filled < total; ) {
    seq.processTick();
    const n = Math.min(128, total - filled);
    synth.process(rawL, rawR, filled, n);
    filled += n;
  }
  const renderMs = Math.round(performance.now() - started);

  // Заворачиваем хвост в начало петли.
  const left = new Float32Array(loopSamples);
  const right = new Float32Array(loopSamples);
  for (let i = 0; i < total; i++) {
    left[i % loopSamples] += rawL[i];
    right[i % loopSamples] += rawR[i];
  }
  // Если к концу хвоста звук ещё не затих, окно хвоста мало: шов будет слышен.
  let tailEnd = 0;
  for (let i = total - Math.round(0.25 * rate); i < total; i++) tailEnd = Math.max(tailEnd, Math.abs(rawL[i]), Math.abs(rawR[i]));
  return {
    left,
    right,
    renderMs,
    tailEndPeak: tailEnd,
    soundfont: { file: basename(soundfontPath), bytes: sf.length, sha256: createHash("sha256").update(sf).digest("hex") },
  };
}

// Числа вместо ушей: пик, средняя громкость и скачок на шве в сравнении с шагами между
// соседними сэмплами рядом со швом (последние и первые 20 мс).
function measure(left, right, rate) {
  let peak = 0;
  let sum = 0;
  const n = left.length;
  for (let i = 0; i < n; i++) {
    peak = Math.max(peak, Math.abs(left[i]), Math.abs(right[i]));
    sum += left[i] * left[i] + right[i] * right[i];
  }
  const w = Math.min(Math.round(0.02 * rate), n - 1);
  let nearStep = 0;
  for (const ch of [left, right]) {
    for (let i = 1; i <= w; i++) nearStep = Math.max(nearStep, Math.abs(ch[i] - ch[i - 1]), Math.abs(ch[n - i] - ch[n - i - 1]));
  }
  const seamStep = Math.max(Math.abs(left[0] - left[n - 1]), Math.abs(right[0] - right[n - 1]));
  return { peak, rms: Math.sqrt(sum / (2 * n)), nearStep, seamStep };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.out) fail("нужен --out <каталог>. Для роли звука это drafts/<шаг>/out/audio-designer/");
  if (args.demo === Boolean(args.score)) fail("нужно ровно одно из двух: --demo или --score <файл.json>");
  if (!(args.peak > 0 && args.peak <= 1)) fail("--peak от 0 до 1");
  if (!(args.rate >= 22050 && args.rate <= 48000)) fail("--rate от 22050 до 48000");
  if (args.soundfont) {
    if (!existsSync(args.soundfont)) fail("SoundFont не найден: " + args.soundfont + ". Скрипт ничего не скачивает; см. README.md");
    // Проверка до первой записи: у файлов SoundFont и DLS заголовок RIFF.
    const fd = openSync(args.soundfont, "r");
    const magic = Buffer.alloc(4);
    readSync(fd, magic, 0, 4, 0);
    closeSync(fd);
    if (!["RIFF", "RIFS"].includes(magic.toString("latin1"))) fail("файл не похож на SoundFont (нет заголовка RIFF): " + args.soundfont);
  }
  const here = dirname(fileURLToPath(import.meta.url));
  const outDir = resolve(args.out);
  try {
    checkOutDir(outDir, here);
  } catch (e) {
    fail(e.message);
  }

  const score = normalizeScore(args.demo ? DEMO : JSON.parse(readFileSync(args.score, "utf8")));
  score.warnings.forEach((w) => console.error("make_loop: предупреждение: " + w));
  mkdirSync(outDir, { recursive: true });

  const pinned = JSON.parse(readFileSync(join(here, "package.json"), "utf8")).dependencies;
  const midiPath = join(outDir, score.id + ".mid");
  const midiBytes = buildMidi(score);
  writeFileSync(midiPath, midiBytes);
  const report = {
    id: score.id,
    script: "tools/audio/make_loop.mjs",
    tools: `midi-writer-js ${pinned["midi-writer-js"]} (MIT), spessasynth_core ${pinned.spessasynth_core} (Apache-2.0)`,
    node: process.version,
    generatedAt: new Date().toISOString(),
    bpm: score.bpm,
    bars: score.bars,
    beatsPerBar: score.beatsPerBar,
    loopSeconds: Number(score.loopSeconds.toFixed(3)),
    tracks: score.tracks.map((t) => ({ name: t.name, channel: t.channel, program: t.program, notes: t.notes.length })),
    warnings: score.warnings,
    midi: { file: midiPath, bytes: midiBytes.length },
    rendered: false,
    status: "кандидат — не прослушано",
    note: "Сгенерировано кодом, никем не прослушано. Не загружать и не ставить в игру без владельца.",
  };
  console.log(`${score.id}: MIDI ${midiBytes.length} Б, петля ${report.loopSeconds} с`);

  if (!args.soundfont) {
    console.log("SoundFont не задан: записан только MIDI. Для рендера добавьте --soundfont <файл>.");
  } else {
    const r = await renderLoop(score, midiBytes, args.soundfont, args.rate);
    const before = measure(r.left, r.right, args.rate);
    if (before.peak === 0) fail("рендер дал тишину: в этом SoundFont нет нужных инструментов?");
    const gain = args.peak / before.peak;
    const left = r.left.map((v) => v * gain);
    const right = r.right.map((v) => v * gain);
    const m = measure(left, right, args.rate);
    const tailDecayed = r.tailEndPeak * gain < 0.002;
    if (!tailDecayed) console.error(`make_loop: предупреждение: через ${TAIL_SECONDS} с после конца петли звук ещё не затих; шов может быть слышен`);
    const wavPath = join(outDir, score.id + ".wav");
    const wav = wav16([left, right], args.rate);
    writeFileSync(wavPath, wav);
    Object.assign(report, {
      rendered: true,
      sampleRate: args.rate,
      channels: 2,
      samples: left.length,
      renderMs: r.renderMs,
      soundfont: r.soundfont,
      peakRaw: Number(before.peak.toFixed(4)),
      peakOut: Number(m.peak.toFixed(4)),
      rms: Number(m.rms.toFixed(4)),
      seam: { seamStep: Number(m.seamStep.toFixed(5)), stepNearSeam: Number(m.nearStep.toFixed(5)), tailDecayed, ok: tailDecayed && m.seamStep <= m.nearStep * 1.5 },
      wav: { file: wavPath, bytes: wav.length, sha256: createHash("sha256").update(wav).digest("hex") },
      ogg: null,
    });
    console.log(`WAV ${wav.length} Б, рендер ${r.renderMs} мс, пик ${report.peakRaw} -> ${report.peakOut}, шов ${report.seam.ok ? "в норме" : "ПРОВЕРИТЬ"}`);
    if (args.ogg) {
      const oggPath = join(outDir, score.id + ".ogg");
      const f = spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-i", wavPath, "-c:a", "libvorbis", "-q:a", "5", oggPath], { encoding: "utf8" });
      if (f.error || f.status !== 0) console.error("make_loop: ffmpeg не отработал (" + (f.error?.code ?? f.stderr.trim()) + "), OGG пропущен");
      else {
        report.ogg = { file: oggPath, bytes: statSync(oggPath).size };
        console.log(`OGG ${report.ogg.bytes} Б`);
      }
    }
  }
  const reportPath = join(outDir, score.id + ".report.json");
  writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n");
  console.log("отчёт: " + reportPath);
}

export { buildMidi, checkOutDir, measure, normalizeScore };

// Запуск из командной строки; при import из теста main не выполняется.
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
