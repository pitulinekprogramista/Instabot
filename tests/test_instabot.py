import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import Instabot as ib


def test_normalize():
    assert ib.normalize("  Hello   WORLD ") == "hello world"


def test_apply_result_correct_and_wrong():
    d = {}
    assert ib.apply_result(d, "pies", "dog", "dog") is True
    assert d["pies"] == {"translation": "dog", "locked": False}
    assert ib.apply_result(d, "kot", "?", "Cat") is False
    assert d["kot"]["translation"] == "cat"


def test_locked_not_overwritten():
    d = {"pies": {"translation": "dog", "locked": True}}
    assert ib.apply_result(d, "pies", "dog", "hound") is False
    assert d["pies"]["translation"] == "dog"


def test_json_roundtrip_and_corrupt(tmp_path):
    p = tmp_path / "a.json"
    ib.write_json(p, {"zażółć": 1})
    assert ib.read_json(p, {}) == {"zażółć": 1}
    p.write_text("{zepsute", encoding="utf-8")
    assert ib.read_json(p, {"x": 0}) == {"x": 0}
    assert (tmp_path / "a.json.bak").exists()


def test_env_file(tmp_path, monkeypatch):
    f = tmp_path / ".env"
    f.write_text('# c\nINSTALING_LOGIN="jan"\nINSTALING_PASSWORD=abc=1\n', encoding="utf-8")
    monkeypatch.delenv("INSTALING_LOGIN", raising=False)
    monkeypatch.delenv("INSTALING_PASSWORD", raising=False)
    ib.load_env_file(f)
    assert ib.os.environ["INSTALING_LOGIN"] == "jan"
    assert ib.os.environ["INSTALING_PASSWORD"] == "abc=1"


def test_args_validation():
    assert ib.parse_args(["--limit", "5"]).limit == 5
    try:
        ib.parse_args(["--delay-min", "5", "--delay-max", "1"])
    except SystemExit:
        return
    raise AssertionError("powinno odrzucić złe opóźnienia")
