#!/usr/bin/env python3
"""
LoopDetectionMiddleware
Агент вызывает этот скрипт после каждой правки файла.
При 3+ правках одного файла — выводит предупреждение о смене подхода.
Персистентность через .gemini/middleware/.loop_state.json
"""
import json
import sys
from pathlib import Path

STATE_FILE = Path(__file__).parent / ".loop_state.json"
LOOP_THRESHOLD = 3


def track_edit(filepath: str) -> None:
    state: dict[str, int] = {}
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())

    state[filepath] = state.get(filepath, 0) + 1
    STATE_FILE.write_text(json.dumps(state, indent=2))

    count = state[filepath]
    if count >= LOOP_THRESHOLD:
        print(
            f"\n⚠️  LOOP DETECTED: файл '{filepath}' правился {count} раз.\n"
            f"   → Рассмотри принципиально другой подход к реализации.\n"
            f"   → Возможно, проблема в архитектуре, а не в деталях.\n"
            f"   → Перечитай AGENTS.md Фазу 1 и пересоставь план."
        )


def reset() -> None:
    """Сбрасывает счётчики после успешного коммита."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    print("✅ Loop state сброшен")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: loop_detection.py <filepath> | reset")
        sys.exit(1)
    if sys.argv[1] == "reset":
        reset()
    else:
        track_edit(sys.argv[1])