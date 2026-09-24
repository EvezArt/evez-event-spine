from pathlib import Path

from evez_event_spine.file_spine import FileEventSpine

def test_append_and_verify(tmp_path: Path) -> None:
    spine = FileEventSpine(tmp_path / 'spine.jsonl')
    first = spine.append('SPINE', 'genesis', {'ok': True})
    second = spine.append('CAIN', 'check', {'contradiction': False})
    assert first['seq'] == 0
    assert second['seq'] == 1
    result = spine.verify()
    assert result['valid'] is True
    assert result['events_checked'] == 2

def test_tamper_is_detected(tmp_path: Path) -> None:
    path = tmp_path / 'spine.jsonl'
    spine = FileEventSpine(path)
    spine.append('SPINE', 'test', {'value': 1})
    text = path.read_text(encoding='utf-8')
    path.write_text(text.replace('"value":1', '"value":2'), encoding='utf-8')
    result = spine.verify()
    assert result['valid'] is False
    assert any(item['error'] == 'event hash mismatch' for item in result['errors'])

def test_replay_preserves_order(tmp_path: Path) -> None:
    spine = FileEventSpine(tmp_path / 'spine.jsonl')
    spine.append('A', 'one', {})
    spine.append('B', 'two', {})
    events = spine.replay()
    assert [event['seq'] for event in events] == [0, 1]
