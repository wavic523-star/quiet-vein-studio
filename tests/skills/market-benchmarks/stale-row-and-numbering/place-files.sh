#!/usr/bin/env bash
# Кладёт проверочные файлы в текущую папку. Запускать только в одноразовой копии
# репозитория студии: внутри настоящего клона (в любой его подпапке) скрипт останавливается.
set -eu
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Это настоящий клон git. Тест запускается только в копии без git." >&2
  exit 1
fi
if [ -d "$(dirname "$0")/files" ]; then
  cp -R "$(dirname "$0")/files/." .
fi
