# Verification, 2026-10-11

## This pass

These checks were run in the existing workspace checkout on 2026-10-11 while updating the judge-facing docs. The shell had `SERPAPI_API_KEY` unset. No SerpApi request was made. The interpreter was `.venv/bin/python`, Python 3.14.6, on macOS.

- `python -m unittest discover -s tests` reported `Ran 52 tests in 0.244s` and `OK`.
- `python -m pip install --require-hashes -r requirements.txt` completed with the hashed requirements already installed.
- `python app.py` was not started. A process was already listening on `127.0.0.1:8501`. `GET /` returned HTTP 200, `Server: Werkzeug/3.1.9 Python/3.14.6`, title Dependency Drift Radar. That GET was not a search.

Counts of 12, 27, 49, and 50 are not the result of this run. The only current suite result is the 52 above.

## What those 52 tests cover

The suite is `tests/test_radar.py`, `tests/test_ui.py`, `tests/test_freshness.py`, and `tests/test_reviews.py`. It uses Flask's test client, temporary directories, and mocks. It does not open live source pages and it does not call SerpApi.

Covered here:

- Requirement parsing, duplicate names, unsafe input, the five-package limit, and the pin remaining in the query string.
- Source-link filtering, canonical URL handling, and source-category ordering, including spoofed hostnames and documentation subdomains. These are classifier checks on URLs and snippets, not page fetches.
- Cache writes omitting the key and provider metadata, the local live-attempt budget, and redacted network and API errors.
- Synthetic fixture rendering and Markdown export, CSRF rejection, and HTML escaping.
- Synthetic mode rendering a pydantic card with zero `urlopen` calls (`tests/test_ui.py`).
- Live mode with an empty key stopping as "Live mode was not run" and showing no evidence-origin summary (`tests/test_freshness.py`).
- A Live request whose queries are already in a temporary cache staying "cached search result", keeping the stored timestamp, and not calling the network. The test key is the placeholder `fixture-key-not-a-real-secret`, and the page must not echo it.
- Missing and invalid retrieval timestamps staying unknown, and mixed provenance staying mixed in the brief.
- A new lead starting unreviewed, with version applicability not established. Keep does not copy the snippet into the saved review and does not verify it. Unsure stays unresolved.
- "Reviewer says applicable" and "reviewer says not applicable" requiring both a source URL and a rationale. The suite checks that validation. It does not decide applicability for pydantic 1.10.0.
- A changed title, snippet, or pin marking the saved review for re-review. A lead absent from a later result is not dismissed. A corrupt review file is not overwritten.
- The next-check brief keeping the human decision apart from the snippet, and the evidence export still listing queries after the review UI.

## Earlier reports, not re-run in this pass

The previous text of this file, dated October 9, 2026, said 12 automated tests passed on Python 3.10/Linux; transport was tested with mocked JSON; no live SerpApi call was made because free signup hit an image-grid CAPTCHA; and no GitHub repo or event submission had been made. That paragraph is historical. This pass did not reproduce the Python 3.10/Linux run. This repository's first commit is 2026-10-11, "Add the Dependency Drift Radar hackathon app," and `origin` is https://github.com/denelbjohn18/dependency-drift-radar-hackathon.

`docs/OUTCOME_PROOF.md` records a saved-cache default-form run on 2026-10-11: no search key, a localhost log with no SerpApi host, Keep on pydantic issue 9768, applicability left not established, and a FastAPI top 3 that still had no relevant lead. This pass did not repeat that browser run or re-fetch those pages.

`docs/EVALUATION.md` records Cursor-assisted labels for nine leads on 2026-10-11: relevant lead 3, irrelevant lead 2, uncertain 4. This pass did not repeat those page reads. Those labels are not an independent review by the project owner.

## Bounded tracked-file scan

On 2026-10-11, `git grep` searched the paths from `git ls-files` for `api_key`, `SERPAPI_API_KEY`, private-key headers, `AKIA` access-key ids, `sk-` tokens, and Slack-style `xox` tokens.

Included: the tracked application, tests, docs, `fixtures/search.json`, `requirements.txt`, `uv.lock`, `pyproject.toml`, and `MANIFEST.sha256`.

Excluded from this scan: gitignored `.venv/`, `.cache/`, and `.reviews/`; untracked files, including `docs/OUTCOME_PROOF.md`, `docs/outcome-next-check-brief.md`, and `docs/outcome-screenshots/`; and the rest of the machine. This scan does not say those excluded locations are free of secrets.

A repeat of that scan after these doc edits still matches only names and the test placeholder: `SERPAPI_API_KEY` in `README.md`, `app.py`, `tests/test_freshness.py`, `docs/SUBMISSION.md`, and this file; the request parameter name `api_key` in `radar.py`; and `fixture-key-not-a-real-secret` in `tests/test_freshness.py`. No tracked path was named `.env`, `.pem`, or `credentials`. The same scan found no private-key block and no `AKIA`, `sk-`, or `xox` token.

## Not verified in this pass

- The new demo video, and whether a public or unlisted link opens in an incognito window without an access request.
- A fresh clone of the public repository after this commit, and an incognito view of that GitHub page.
- A fresh download of a hosted ZIP.
- Final submission of the entry.
- A live SerpApi call, the account quota, or a new cache write.
- The October 9 Python 3.10/Linux note.
- An independent owner review of the nine-lead labels or of the Keep on issue 9768.
- Applicability of pin 1.10.0 to issue 9768. The recorded review left that not established.
