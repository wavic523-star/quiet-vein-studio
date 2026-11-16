#!/usr/bin/env python3
"""Проверка репозитория навыков Quiet Vein. Только стандартная библиотека.

Запуск из корня репозитория: python tools/validate_repo.py
Код возврата 0: ошибок нет (предупреждения допустимы), 1: есть ошибки.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_SKILL_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FORBIDDEN_NAMES = {"bin", "hooks", "plan_digest"}
FORBIDDEN_FILES = {".mcp.json", "settings.json", "settings.local.json"}
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    "API key (sk-)": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Slack token": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    "Private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "Roblox cookie": re.compile(r"_\|WARNING:-DO-NOT-SHARE-THIS"),
}
MAX_DESC = 1024
MAX_LINES = 500
WARN_CHARS = 12000  # ≈ 5 тыс. токенов при ≈ 2,5 знака на токен (консервативно для русского)

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def rel(p):
    return str(p.relative_to(ROOT))


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        err(f"{rel(path)}: файл не найден")
    except json.JSONDecodeError as e:
        err(f"{rel(path)}: неверный JSON ({e})")
    return None


def parse_frontmatter(text):
    """Возвращает (словарь, номер строки начала тела) или (None, 0)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, 0
    fm = {}
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return fm, i + 1
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        if ":" not in line:
            return None, 0
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return None, 0


def check_skill(skill_dir):
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        err(f"{rel(skill_dir)}: нет SKILL.md")
        return
    text = md.read_text(encoding="utf-8")
    fm, body_start = parse_frontmatter(text)
    if fm is None:
        err(f"{rel(md)}: нет корректного блока frontmatter (--- ... ---)")
        return
    for key in fm:
        if key not in ALLOWED_SKILL_KEYS:
            err(f"{rel(md)}: недопустимое поле frontmatter «{key}» (навык аккаунта принимает {sorted(ALLOWED_SKILL_KEYS)})")
    name = fm.get("name", "")
    if name != skill_dir.name:
        err(f"{rel(md)}: name «{name}» не совпадает с папкой «{skill_dir.name}»")
    if not NAME_RE.match(name) or len(name) > 64:
        err(f"{rel(md)}: name «{name}» должен быть из строчных латинских букв, цифр и дефисов, до 64 знаков")
    if "claude" in name or "anthropic" in name:
        err(f"{rel(md)}: name не должен содержать claude или anthropic")
    desc = fm.get("description", "")
    if not desc:
        err(f"{rel(md)}: пустой description")
    if len(desc) > MAX_DESC:
        err(f"{rel(md)}: description {len(desc)} знаков, предел {MAX_DESC}")
    if "<" in desc or ">" in desc:
        err(f"{rel(md)}: в description нельзя угловые скобки")
    n_lines = len(text.split("\n"))
    if n_lines > MAX_LINES:
        err(f"{rel(md)}: {n_lines} строк, предел {MAX_LINES}")
    body = "\n".join(text.split("\n")[body_start:])
    if len(body) > WARN_CHARS:
        warn(f"{rel(md)}: тело {len(body)} знаков, это больше ≈ 5 тыс. токенов; вынеси справку в references/")
    if len(desc) > 300:
        warn(f"{rel(md)}: description {len(desc)} знаков; все описания навыков всегда лежат в контексте, держи короче")


def check_tree_rules():
    for p in ROOT.rglob("*"):
        if ".git" in p.relative_to(ROOT).parts[:1]:
            continue
        r = p.relative_to(ROOT)
        if p.is_dir() and p.name in FORBIDDEN_NAMES:
            err(f"{r}: папка «{p.name}» запрещена правилами проекта (хуки, исполняемые файлы, копия плана)")
        if p.is_file() and p.name in FORBIDDEN_FILES:
            err(f"{r}: файл «{p.name}» запрещён правилами проекта")
        if p.is_file() and r.parts and r.parts[0] == ".claude":
            err(f"{r}: папка .claude не нужна: навыки живут в plugins/")


def check_secrets():
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.relative_to(ROOT).parts[:1]:
            continue
        if p.suffix.lower() in {".zip", ".png", ".jpg", ".jpeg", ".gif"}:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for label, pat in SECRET_PATTERNS.items():
            if pat.search(text):
                err(f"{rel(p)}: похоже на секрет ({label})")


def main():
    market_path = ROOT / ".claude-plugin" / "marketplace.json"
    market = load_json(market_path)
    if market is not None:
        mname = market.get("name", "")
        if not mname or not mname.isascii() or " " in mname:
            err(f"{rel(market_path)}: name «{mname}» должен быть ASCII без пробелов")
        if not isinstance(market.get("owner"), dict) or not market["owner"].get("name"):
            err(f"{rel(market_path)}: нужен owner.name")
        plugins = market.get("plugins")
        if not isinstance(plugins, list) or not plugins:
            err(f"{rel(market_path)}: plugins должен быть непустым списком")
            plugins = []
        for entry in plugins:
            ename = entry.get("name", "")
            source = entry.get("source")
            if not ename or " " in ename:
                err(f"{rel(market_path)}: у записи плагина нет name или в нём пробел")
            if not isinstance(source, str) or not source.startswith("./") or ".." in source:
                err(f"{rel(market_path)}: source «{source}» должен быть путём от корня, начинаться с ./ и не содержать ..")
                continue
            pdir = ROOT / source
            if not pdir.is_dir():
                err(f"{rel(market_path)}: папки плагина «{source}» нет")
                continue
            pj_path = pdir / ".claude-plugin" / "plugin.json"
            pj = load_json(pj_path)
            if pj is not None:
                if pj.get("name") != ename:
                    err(f"{rel(pj_path)}: name «{pj.get('name')}» не совпадает с записью в marketplace.json «{ename}»")
                if "version" in pj and "version" in entry:
                    err(f"{rel(pj_path)}: version задан и в plugin.json, и в marketplace.json; оставь один (лучше ни одного, тогда обновления идут по коммитам)")
            skills_dir = pdir / "skills"
            if not skills_dir.is_dir() or not any(skills_dir.iterdir()):
                err(f"{rel(pdir)}: нет skills/ или она пуста")
            else:
                for sd in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
                    check_skill(sd)
    check_tree_rules()
    check_secrets()
    for w in warnings:
        print(f"ПРЕДУПРЕЖДЕНИЕ {w}")
    for e in errors:
        print(f"ОШИБКА {e}")
    print(f"Итого: ошибок {len(errors)}, предупреждений {len(warnings)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
