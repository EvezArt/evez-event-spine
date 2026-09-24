"""Durable append-only Event Spine JSONL implementation."""

from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ZERO_HASH = "0" * 64

def canonical_event_bytes(event: dict[str, Any]) -> bytes:
    body = {key: value for key, value in event.items() if key != 'hash'}
    return json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')

def event_hash(event: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_event_bytes(event)).hexdigest()

class FileEventSpine:
    """Append-only JSONL Event Spine with deterministic verification."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open('r', encoding='utf-8') as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def append(self, actor: str, event_type: str, data: Any, timestamp: str | None = None) -> dict[str, Any]:
        if not actor.strip():
            raise ValueError('actor is required')
        if not event_type.strip():
            raise ValueError('event_type is required')
        with self._lock:
            events = self._read()
            seq = len(events)
            previous_hash = events[-1]['hash'] if events else ZERO_HASH
            event = {'version': 1, 'seq': seq, 'timestamp': timestamp or self._timestamp(), 'actor': actor, 'event_type': event_type, 'data': data, 'prev_hash': previous_hash}
            event['hash'] = event_hash(event)
            with self.path.open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(',', ':')))
                handle.write('\n')
            return event

    def verify(self) -> dict[str, Any]:
        with self._lock:
            events = self._read()
        errors: list[dict[str, Any]] = []
        previous_hash = ZERO_HASH
        for index, event in enumerate(events):
            if event.get('version') != 1:
                errors.append({'seq': index, 'error': 'unsupported version'})
                continue
            if event.get('seq') != index:
                errors.append({'seq': index, 'error': 'sequence mismatch'})
            if event.get('prev_hash') != previous_hash:
                errors.append({'seq': index, 'error': 'previous hash mismatch'})
            expected = event_hash(event)
            if event.get('hash') != expected:
                errors.append({'seq': index, 'error': 'event hash mismatch'})
            previous_hash = event.get('hash', '')
        return {'valid': not errors, 'events_checked': len(events), 'errors': errors[:20], 'first_error_seq': errors[0]['seq'] if errors else None, 'last_hash': previous_hash if events else ZERO_HASH}

    def replay(self) -> list[dict[str, Any]]:
        with self._lock:
            return self._read()
