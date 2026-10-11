# Dependency Drift Radar

Python dependency search leads, then an explicit human review, then a traceable next-check brief.

This is a local Flask app. It searches for migration, deprecation, and security-related references, keeps each lead attached to its link, snippet, query, and retrieval time, and lets a person save Keep, Dismiss, or Unsure. The next-check brief is the downloadable work list of those decisions. It does not install packages, crawl the linked pages, compare versions, or apply an upgrade.

## Setup

Python 3.10 or newer. Clone the repository and run:

```sh
git clone https://github.com/denelbjohn18/dependency-drift-radar-hackathon
cd dependency-drift-radar-hackathon
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements.txt
python -m unittest discover -s tests
python app.py
```

Flask serves http://127.0.0.1:8501. Synthetic fixtures run from that page with no API key.

### Commands checked on 2026-10-11

Checked in the existing workspace checkout, with `.venv/bin/python` (Python 3.14.6) because that virtualenv was already present. `SERPAPI_API_KEY` was unset. No SerpApi search was made.

- `python -m pip install --require-hashes -r requirements.txt` completed. The hashed requirements were already installed.
- `python -m unittest discover -s tests` reported `Ran 52 tests in 0.244s` and `OK`.
- `python app.py` was not started in this pass. Something was already listening on `127.0.0.1:8501`. A `GET /` returned HTTP 200 from `Werkzeug/3.1.9 Python/3.14.6` and the Dependency Drift Radar page. That request was not a search.

Not run in this pass: `git clone https://github.com/denelbjohn18/dependency-drift-radar-hackathon`, `python3 -m venv .venv`, and `source .venv/bin/activate`. The checks above were made in the existing checkout before this commit.

## Run modes

The form has three modes. The requested mode and the evidence origin are recorded separately. Choosing a mode does not relabel where a lead came from.

Synthetic fixtures work after clone with no key. They read `fixtures/search.json`, make no search-API call, and stay labeled synthetic. They have no real retrieval time.

Saved cache only reads real responses already stored in the private `.cache/` directory and makes no network call. A clone leaves that cache behind: `.cache/` is gitignored. Without those files, saved-cache mode stops on a missing saved response and does not call the network.

Live reads `SERPAPI_API_KEY` from the process environment and uses that account's free quota. The key is never a file in the repository. With no key, live mode stops and does not present a completed search. Selecting Live is not proof a network call happened. A hit in `.cache/` stays a cached search result and keeps the stored retrieval time.

## Default workflow

The shipped form starts with:

```
pydantic==1.10.0
fastapi==0.95.0
```

Each package gets two queries: a documentation-scoped migration and deprecation search, then a broader security-advisory and release-notes search. The documentation scope for Flask is `flask.palletsprojects.com`. The same table covers FastAPI, Pydantic, Django, Requests, NumPy, Pandas, and SQLAlchemy. Any other name uses a PyPI project scope for the first query. The limit is five packages. The first exact pin wins when a name is repeated. A name without `==` is an unknown installed version. A version range is rejected.

Cards show the source link, the snippet, the query, the retrieval time, and the evidence origin. Search snippets stay `UNVERIFIED: search snippet only`. A person saves a review on a card. Download next-check brief writes the decisions beside that provenance.

The recorded default run is [docs/OUTCOME_PROOF.md](docs/OUTCOME_PROOF.md). The brief from that run is [docs/outcome-next-check-brief.md](docs/outcome-next-check-brief.md). It used Saved cache only, with no search key. The kept lead was [pydantic issue 9768](https://github.com/pydantic/pydantic/issues/9768), from `site:docs.pydantic.dev pydantic 1.10.0 migration deprecation`, retrieved `2026-10-10T09:29:23.321816+00:00`. The page compares multiple-parent `extra` configuration: its v1 sample prints pydantic 1.10.13 and its v2 sample prints pydantic 2.7.2. Applicability to pin 1.10.0 was left not established. The stored `site:` results for that scan were not on `docs.pydantic.dev` or `fastapi.tiangolo.com`. The FastAPI default top 3 still had no relevant lead: a release-date discussion, a release-notes page whose fetch was empty, and a short repository stub. Those three stayed listed.

## Targeted follow-up

The shipped screen has no custom-query field and no targeted-follow-up control. The default scan above did not need one.

A separate manually cached query, `Pydantic official Migration Guide V1 V2 model_dump dict`, retrieved `2026-10-10T10:13:33.575558+00:00`, is stored in the private cache and labeled in [docs/EVALUATION.md](docs/EVALUATION.md). It is not output from the default two-query form.

## Evaluation sample

[docs/EVALUATION.md](docs/EVALUATION.md) records nine leads: the top 3 from three cases. The labels are relevant lead 3, irrelevant lead 2, and uncertain 4. They were Cursor-assisted manual labels recorded in this workspace on 2026-10-11, not an independent review by the project owner. The sample is those nine leads. Uncertain stays its own label. Pin applicability stays not established on every row. Search snippets stay unverified. A separate note in that file records order after a ranking change; it does not replace the 3/2/4 counts.

## Reviews

Each lead starts unreviewed. Keep means worth investigating. It does not verify the snippet and it does not establish applicability. Dismiss means deprioritized. It does not mean fixed or resolved. Unsure stays unresolved.

Version applicability stays "not established" until a person saves "reviewer says applicable" or "reviewer says not applicable" with a source URL and a rationale. That pair is a reviewer-entered assessment. The recorded outcome left applicability not established. The fields are not filled from the pin, the query, or the snippet.

Reviews are stored in `.reviews/` on this machine. That directory is gitignored. If a later result changes a lead's title or snippet, the card shows "needs re-review: evidence changed" and the lead returns to unresolved until a person saves it again. A lead missing from a later search is not dismissed.

The next-check brief is a Markdown work list. It is not a vulnerability report.

## Limits that stay on every lead

Freshness is the age of the retrieved evidence. It is not proof that the page or the claim is current. There is no expiry cutoff. A missing or invalid retrieval timestamp stays unknown. Freshness does not apply to a synthetic fixture.

The process allows 20 live attempts, including failures, and spaces uncached live attempts 80 seconds apart. Restarting the process resets that counter. It does not reset the SerpApi account quota. There is no automatic retry, paid fallback, or upgrade.

The development server binds `127.0.0.1` only. Cached queries can reveal package names. Leave confidential names out of the form, and leave the API key out of source, screenshots, video, and chat.

## Tests

On 2026-10-11, `python -m unittest discover -s tests` in this checkout reported 52 tests, OK, on Python 3.14.6. See [docs/VERIFICATION.md](docs/VERIFICATION.md).

Draft entry text is in [docs/SUBMISSION.md](docs/SUBMISSION.md). The recording guide is [docs/DEMO.md](docs/DEMO.md). AI-tool disclosure is the draft in [docs/AI_DISCLOSURE.md](docs/AI_DISCLOSURE.md).

Rules and terms: https://serpapi.github.io/serpapi-india-hackathon-2026/rules.html and https://serpapi.github.io/serpapi-india-hackathon-2026/terms.html
