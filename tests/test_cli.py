import json
import shutil
from pathlib import Path

import pytest

from doc_chunker.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def docs_dir(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    (docs / "nested").mkdir(parents=True)
    shutil.copy(FIXTURES / "sample.md", docs / "a.md")
    shutil.copy(FIXTURES / "sample.html", docs / "nested" / "b.html")
    shutil.copy(FIXTURES / "sample.pdf", docs / "c.pdf")
    (docs / "ignore.txt").write_text("not supported", encoding="utf-8")
    return docs


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_folder_to_jsonl_file(docs_dir, tmp_path):
    out = tmp_path / "chunks.jsonl"
    code = main([str(docs_dir), "--size", "200", "--overlap", "20", "--out", str(out)])

    assert code == 0
    rows = read_jsonl(out)
    assert rows
    assert all(set(r) == {"text", "source", "section", "index"} for r in rows)
    assert all(len(r["text"]) <= 200 for r in rows)

    names = {Path(r["source"]).name for r in rows}
    assert names == {"a.md", "b.html", "c.pdf"}  # nested folder included, .txt skipped


def test_index_restarts_per_file(docs_dir, tmp_path):
    out = tmp_path / "chunks.jsonl"
    main([str(docs_dir), "--size", "200", "--overlap", "20", "--out", str(out)])

    by_file: dict[str, list[int]] = {}
    for r in read_jsonl(out):
        by_file.setdefault(r["source"], []).append(r["index"])
    for indexes in by_file.values():
        assert indexes == list(range(len(indexes)))


def test_files_are_processed_in_sorted_order(docs_dir, tmp_path):
    out = tmp_path / "chunks.jsonl"
    main([str(docs_dir), "--out", str(out)])

    seen: list[str] = []
    for r in read_jsonl(out):
        if not seen or seen[-1] != r["source"]:
            seen.append(r["source"])
    assert seen == sorted(seen)


def test_unsupported_file_warns_on_stderr(docs_dir, tmp_path, capsys):
    main([str(docs_dir), "--out", str(tmp_path / "out.jsonl")])
    assert "ignore.txt" in capsys.readouterr().err


def test_single_file_to_stdout(capsys):
    code = main([str(FIXTURES / "sample.md")])

    assert code == 0
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert rows[0]["section"] == ""
    assert rows[0]["index"] == 0


def test_missing_path_returns_1(tmp_path, capsys):
    assert main([str(tmp_path / "nope")]) == 1
    assert capsys.readouterr().err


def test_bad_overlap_returns_1_and_writes_nothing(docs_dir, tmp_path, capsys):
    out = tmp_path / "chunks.jsonl"
    code = main([str(docs_dir), "--size", "50", "--overlap", "50", "--out", str(out)])

    assert code == 1
    assert capsys.readouterr().err
    assert not out.exists() or out.read_text() == ""
