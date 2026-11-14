# Build guide

You get the structure, the contracts and the tests. You write the logic.

- `models.py` is complete. Read it first.
- Every other function has a docstring contract and a `TODO`. The tests check that contract exactly.
- Hints are folded. Try for 20–30 minutes before opening one, and open them in order: hint 1 is a nudge, hint 2 is the approach. There is no hint 3 with code.

**Rule for yourself:** don't edit the tests to make them pass. If you think a test is wrong, write down why. That's a good interview story either way.

## Step 0: Set up (15 min)

```console
cd doc-chunker
uv sync
uv run pytest
```

You should see 46 tests, almost all failing with `NotImplementedError`. That's your progress bar.

Then create the GitHub repo and push this skeleton as your first commit. CI will be red; that's fine.

## Step 1: `split_text` (the hardest bit, ~2 hours)

`uv run pytest tests/test_splitter.py -k "not chunk_sections" -v`

Start with the cheap tests: validation, empty text, short text. Then the window loop.

<details><summary>Hint 1</summary>

Think of a `start` index walking through the text. Each step: compute `end = start + size`. If `end` reaches the end of the text, that's the last piece. Otherwise, decide where to cut, record the piece, and set the next `start`. Write it without the "don't cut words" rule first and get the overlap and rebuild tests green.
</details>

<details><summary>Hint 2</summary>

For the word rule, search backwards from `end - 1` for a whitespace character (`str.isspace()`), but stop before you go below `start + overlap`. If you find one at position `j`, the piece ends at `j + 1`. Why that lower bound? The next start is `end - overlap`; if `end` could fall to `start + overlap` or below, `start` would never move forward and you'd loop forever.
</details>

**Checkpoint:** commit. Message idea: `feat: split_text with overlap and word boundaries`.

## Step 2: `chunk_sections` (~20 min)

`uv run pytest tests/test_splitter.py -v`

<details><summary>Hint 1</summary>

Two nested `for` loops and a counter that lives outside both. `yield` makes the function a generator; you don't need to build a list.
</details>

## Step 3: `read_markdown` (~1.5 hours)

`uv run pytest tests/test_readers.py -k markdown -v`

<details><summary>Hint 1</summary>

Go line by line and keep three pieces of state: the current heading path, the lines collected for the current section, and whether you're inside a code fence. When a heading arrives, "flush" the collected lines as a Section, then update the path.
</details>

<details><summary>Hint 2</summary>

A regex for a heading line: one to six `#`, then at least one whitespace character, then the title. Use `re.match` with `^(#{1,6})\s+(.+?)\s*$`, and `len(group(1))` is the level.

For the path, keep a list of `(level, title)`. On a new heading, pop entries while the top one's level is >= the new level, then push. The path is the titles joined with `" > "`.

Don't forget to flush once more after the last line.
</details>

## Step 4: `read_html` (~1 hour)

`uv run pytest tests/test_readers.py -k html -v`

<details><summary>Hint 1</summary>

`soup(["script", "style", ...])` returns all matching tags; call `.decompose()` on each. `soup.find_all([...])` with a list of tag names returns them in document order.
</details>

<details><summary>Hint 2</summary>

The heading-path and flush logic is the same as Markdown, with levels from the tag name (`"h2"` → 2). If you copied code from step 3, this is the moment to pull it into a small shared helper (a function or a tiny class), and rerun the Markdown tests to prove you didn't break them.

For whitespace: `" ".join(s.split())` collapses any whitespace run into one space.
</details>

## Step 5: `read_pdf` and `read_file` (~30 min)

`uv run pytest tests/test_readers.py -v`

<details><summary>Hint 1</summary>

`PdfReader(path).pages` is a list; `page.extract_text()` can return `None` or an empty string. `enumerate(..., start=1)` gives you page numbers that count blank pages too.

For `read_file`, `path.suffix.lower()` gives `".md"` for `NOTES.MD`.
</details>

## Step 6: CLI (~1 hour)

`uv run pytest tests/test_cli.py -v`, then try it for real:

```console
uv run doc-chunker tests/fixtures --size 120 --overlap 20
```

<details><summary>Hint 1</summary>

`Path.rglob("*")` walks a folder recursively; filter with `is_file()` and wrap in `sorted()`. Decide the output stream once: an opened file if `--out` was given, otherwise `sys.stdout`. Remember to close the file (and not `sys.stdout`): `try`/`finally` or a context manager.
</details>

<details><summary>Hint 2</summary>

The "bad overlap writes nothing" test: if you only discover the bad arguments while writing, you've already created the file. Validate first. The cheapest way is to call `split_text` once on a tiny string inside `try`/`except ValueError`, before opening `--out`.
</details>

## Step 7: Make it presentable (~1 hour)

- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass
- [ ] All 46 tests pass locally, then push and confirm CI is green
- [ ] Uncomment the CI badge in `README.md` with your username
- [ ] Fill in every `TODO` in `README.md` in your own words, with real output from your run
- [ ] Delete the instruction comments from the README
- [ ] Pin the repo on your GitHub profile

**Stretch, if you have time:** add a pre-commit hook that runs ruff ([ruff's pre-commit docs](https://docs.astral.sh/ruff/integrations/)), or add a test of your own for a case you think is missing, such as Setext headings (`Title` underlined with `===`).
