#!/usr/bin/env node
// make_sfx.mjs — короткие SFX кодом (jsfxr, Unlicense) -> WAV 16 бит моно, по желанию OGG через ffmpeg.
//
// Читает: список звуков (--list, JSON) и свой package.json. Пишет: только в каталог --out
// (<id>.wav, <id>.ogg, sfx-report.json). Сеть не нужна. Ничего не скачивает и не загружает в Roblox.
// Внешний процесс один: ffmpeg, и только с флагом --ogg.
// Внутри репозитория --out принимается только вида drafts/<шаг>/out/...; вне репозитория — любая
// временная папка для пробного прогона.
// Результат — кандидаты: никто, кроме владельца, их не слышал. Статус выше «кандидат» ставит только он.
//
//   node make_sfx.mjs --out <каталог> --demo [--ogg]
//   node make_sfx.mjs --out <каталог> --list <список.json> [--ogg] [--peak 0.6]
//   node make_sfx.mjs --out <каталог> --item sfx.ui.click:click:11 [--item ...]
//
// Список: [{ "id": "sfx.ui.click", "preset": "click", "seed": 11, "maxSeconds": 0.3 },
//          { "id": "sfx.ui.back", "params": { ...JSON из отчёта или из sfxr.me... }, "seed": 1 }]
// Один и тот же preset + seed даёт один и тот же файл: Math.random на время генерации заменён.

import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, isAbsolute, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { sfxr } from "jsfxr";

const PRESETS = ["pickupCoin", "laserShoot", "explosion", "powerUp", "hitHurt", "jump", "blipSelect", "synth", "tone", "click", "random"];
const ID_RE = /^[a-z0-9][a-z0-9._-]{0,63}$/;
// Поля звука jsfxr. Объект params принимается только целиком: с пропуском рендер даёт мусор или не кончается.
const PARAM_KEYS = ["wave_type", "p_env_attack", "p_env_sustain", "p_env_punch", "p_env_decay", "p_base_freq", "p_freq_limit", "p_freq_ramp", "p_freq_dramp", "p_vib_strength", "p_vib_speed", "p_arp_mod", "p_arp_speed", "p_duty", "p_duty_ramp", "p_repeat_speed", "p_pha_offset", "p_pha_ramp", "p_lpf_freq", "p_lpf_ramp", "p_lpf_resonance", "p_hpf_freq", "p_hpf_ramp", "sound_vol"];
const DEMO = [
  { id: "test.click", preset: "click", seed: 1 },
  { id: "test.blip", preset: "blipSelect", seed: 2 },
  { id: "test.pickup", preset: "pickupCoin", seed: 3 },
  { id: "test.powerup", preset: "powerUp", seed: 4, maxSeconds: 1.0 },
];

function fail(msg) {
  console.error("make_sfx: " + msg);
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
  const a = { items: [], ogg: false, demo: false, peak: 0.6, rate: 44100 };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    const next = () => argv[++i] ?? fail("после " + k + " нужно значение");
    if (k === "--out") a.out = next();
    else if (k === "--list") a.list = next();
    else if (k === "--item") a.items.push(next());
    else if (k === "--peak") a.peak = Number(next());
    else if (k === "--rate") a.rate = Number(next());
    else if (k === "--ogg") a.ogg = true;
    else if (k === "--demo") a.demo = true;
    else fail("неизвестный аргумент " + k);
  }
  return a;
}

// Детерминированный генератор (mulberry32): нужен, чтобы звук можно было получить заново.
function mulberry32(seed) {
  let t = seed >>> 0;
  return () => {
    t = (t + 0x6d2b79f5) >>> 0;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

function withSeed(seed, fn) {
  const original = Math.random;
  Math.random = mulberry32(seed);
  try {
    return fn();
  } finally {
    Math.random = original;
  }
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

function toOgg(wavPath, oggPath) {
  const r = spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-i", wavPath, "-c:a", "libvorbis", "-q:a", "5", oggPath], { encoding: "utf8" });
  if (r.error || r.status !== 0) {
    console.error("make_sfx: ffmpeg не отработал (" + (r.error?.code ?? r.stderr.trim()) + "), OGG пропущен: " + oggPath);
    return null;
  }
  return { file: oggPath, bytes: statSync(oggPath).size };
}

// Проверка до первой записи на диск: при ошибке в списке не остаётся половины файлов.
function validate(item) {
  if (!item || !ID_RE.test(item.id ?? "")) fail("плохой id: " + JSON.stringify(item?.id) + " (нужны строчные латинские буквы, цифры, . _ -)");
  const hasParams = item.params && typeof item.params === "object";
  if (!hasParams && !PRESETS.includes(item.preset)) fail(item.id + ": неизвестный preset " + JSON.stringify(item.preset) + "; есть: " + PRESETS.join(", "));
  if (hasParams) {
    for (const k of PARAM_KEYS) if (!Number.isFinite(item.params[k])) fail(`${item.id}: params неполные, нет числа в поле ${k}; возьмите объект params целиком из sfx-report.json`);
    for (const k of ["p_env_attack", "p_env_sustain", "p_env_decay"]) if (item.params[k] < 0 || item.params[k] > 1) fail(`${item.id}: ${k} должен быть от 0 до 1`);
  }
  if (item.seed !== undefined && !Number.isInteger(item.seed)) fail(item.id + ": seed должен быть целым числом");
}

function render(item, args) {
  const seed = item.seed ?? 1;
  let params;
  if (item.params && typeof item.params === "object") {
    params = { ...item.params, sample_rate: args.rate, sample_size: 16 };
  } else {
    params = withSeed(seed, () => sfxr.generate(item.preset, { sample_rate: args.rate, sample_size: 16, sound_vol: 0.25 }));
  }
  // Рендер получает свой отсчёт от того же seed: params + seed из отчёта дают тот же файл (шумовые волны тоже).
  const wave = withSeed(seed, () => sfxr.toWave(params));

  let samples = Float32Array.from(wave.buffer);
  if (item.maxSeconds > 0) samples = samples.subarray(0, Math.min(samples.length, Math.round(item.maxSeconds * args.rate)));
  if (samples.length === 0) fail(item.id + ": пустой звук");

  // Громкость одна на все файлы: пик приводится к --peak, чтобы в наборе не было внезапно громкого.
  let peakRaw = 0;
  for (const v of samples) peakRaw = Math.max(peakRaw, Math.abs(v));
  const gain = peakRaw > 0 ? args.peak / peakRaw : 1;
  const fadeIn = Math.min(samples.length, Math.round(0.003 * args.rate));
  const fadeOut = Math.min(samples.length, Math.round(0.01 * args.rate));
  const out = new Float32Array(samples.length);
  for (let i = 0; i < samples.length; i++) {
    let g = gain;
    if (i < fadeIn) g *= i / fadeIn;
    const tail = samples.length - 1 - i;
    if (tail < fadeOut) g *= tail / fadeOut;
    out[i] = samples[i] * g;
  }

  const wavPath = join(args.outDir, item.id + ".wav");
  const data = wav16([out], args.rate);
  writeFileSync(wavPath, data);
  const row = {
    id: item.id,
    preset: item.params ? null : item.preset,
    seed,
    seconds: Number((out.length / args.rate).toFixed(3)),
    sampleRate: args.rate,
    channels: 1,
    peakRaw: Number(peakRaw.toFixed(4)),
    peakOut: args.peak,
    clippedInSource: wave.clipping ?? 0,
    wav: { file: wavPath, bytes: data.length, sha256: createHash("sha256").update(data).digest("hex") },
    ogg: args.ogg ? toOgg(wavPath, join(args.outDir, item.id + ".ogg")) : null,
    params: JSON.parse(JSON.stringify(params)),
    status: "кандидат — не прослушано",
  };
  console.log(`${row.id}: ${row.seconds} с, WAV ${row.wav.bytes} Б` + (row.ogg ? `, OGG ${row.ogg.bytes} Б` : ""));
  return row;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.out) fail("нужен --out <каталог>. Для роли звука это drafts/<шаг>/out/audio-designer/");
  if (!(args.peak > 0 && args.peak <= 1)) fail("--peak от 0 до 1");
  if (!(args.rate >= 8000 && args.rate <= 48000)) fail("--rate от 8000 до 48000");
  const here = dirname(fileURLToPath(import.meta.url));
  args.outDir = resolve(args.out);
  try {
    checkOutDir(args.outDir, here);
  } catch (e) {
    fail(e.message);
  }

  let items = [];
  if (args.demo) items = items.concat(DEMO);
  if (args.list) {
    const parsed = JSON.parse(readFileSync(args.list, "utf8"));
    if (!Array.isArray(parsed)) fail("--list: в файле должен быть массив");
    items = items.concat(parsed);
  }
  for (const s of args.items) {
    const [id, preset, seed] = s.split(":");
    items.push({ id, preset, seed: seed === undefined ? 1 : Number.parseInt(seed, 10) });
  }
  if (items.length === 0) fail("нечего делать: дайте --demo, --list или --item");
  items.forEach(validate);
  const ids = items.map((x) => x.id);
  if (new Set(ids).size !== ids.length) fail("повторяющиеся id в списке");

  mkdirSync(args.outDir, { recursive: true });
  const rows = items.map((it) => render(it, args));
  // Версия берётся из нашего package.json: зависимости закреплены точными номерами.
  const pinned = JSON.parse(readFileSync(join(here, "package.json"), "utf8")).dependencies;
  const report = {
    tool: "jsfxr " + pinned.jsfxr + " (Unlicense)",
    script: "tools/audio/make_sfx.mjs",
    node: process.version,
    generatedAt: new Date().toISOString(),
    note: "Сгенерировано кодом, никем не прослушано. Не загружать и не ставить в игру без владельца.",
    items: rows,
  };
  const reportPath = join(args.outDir, "sfx-report.json");
  writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n");
  console.log("отчёт: " + reportPath);
}

export { checkOutDir };

// Запуск из командной строки; при import из теста main не выполняется.
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
